#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-01 (Cases) и методикой верификации по шагам 1–4
(docs/ai-verification.md). Проверяемый код лежит рядом, в dz01-ai-code.py;
исправлять его до завершения верификации запрещено.

Запуск: python dz01-verification-starter.py --variant N
"""
from __future__ import annotations

import argparse
import importlib.util
import collections
import random
import statistics
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Загрузка проверяемого кода
# ---------------------------------------------------------------------------
# Имя файла содержит дефисы, поэтому обычный import не подходит —
# модуль загружается по пути через importlib.

AI_CODE_PATH = Path(__file__).with_name("dz01-ai-code.py")


def load_quicksort():
    """Загружает функцию quicksort из соседнего файла dz01-ai-code.py."""
    spec = importlib.util.spec_from_file_location("dz01_ai_code", AI_CODE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quicksort


quicksort = load_quicksort()

# ---------------------------------------------------------------------------
# 1. Шаг 1 методики: инварианты сортировки
# ---------------------------------------------------------------------------


def is_sorted(a: list[int]) -> bool:
    for i in range(len(a) - 1):
        if a[i] > a[i + 1]:
            return False
    return True


def same_multiset(a: list[int], b: list[int]) -> bool:
    return collections.Counter(a) == collections.Counter(b)


def check_invariants(original: list[int], result: list[int]) -> list[str]:
    errors = []
    if not is_sorted(result):
        errors.append("ИНВАРИАНТ 1 НАРУШЕН: выход не упорядочен")
    if not same_multiset(original, result):
        errors.append("ИНВАРИАНТ 2 НАРУШЕН: мультимножества не совпадают (потеря/дубликаты)")
    return errors

# ---------------------------------------------------------------------------
# 2. Шаг 2 методики: репрезентативные тесты
# ---------------------------------------------------------------------------


def representative_cases(rng: random.Random) -> list[tuple[str, list[int]]]:
    return [
        ("empty", []),
        ("single", [42]),
        ("two_equal", [5, 5]),
        ("all_equal", [7] * 10),
        ("sorted", list(range(10))),
        ("reversed", list(range(10, 0, -1))),
        ("random_dups_neg", [rng.randint(-10, 10) for _ in range(20)]),
    ]


def run_representative_tests(rng: random.Random) -> None:
    print("\n=== ШАГ 2: Репрезентативные тесты ===")
    for name, data in representative_cases(rng):
        try:
            res = quicksort(data)
            errs = check_invariants(data, res)
            status = "OK" if not errs else f"FAIL: {errs}"
            print(f"  {name:<20} | {status}")
        except RecursionError:
            print(f"  {name:<20} | FAIL: RecursionError (переполнение стека)")


# ---------------------------------------------------------------------------
# 3. Шаг 3 методики: сравнение с эталоном sorted()
# ---------------------------------------------------------------------------


def compare_with_reference(rng: random.Random, runs: int = 300) -> None:
    print("\n=== ШАГ 3: Сравнение с sorted() ===")
    mismatches = 0
    min_counterexample = None
    
    for _ in range(runs):
        n = rng.randint(0, 50)
        data = [rng.randint(-20, 20) for _ in range(n)]
        
        try:
            ai_res = quicksort(data)
            ref_res = sorted(data)
            
            if ai_res != ref_res:
                mismatches += 1
                if min_counterexample is None or len(data) < len(min_counterexample[0]):
                    min_counterexample = (data, ai_res, ref_res)
        except RecursionError:
            mismatches += 1
            if min_counterexample is None:
                min_counterexample = (data, "RecursionError", sorted(data))

    print(f"  Расхождений: {mismatches}/{runs}")
    if min_counterexample:
        inp, ai, ref = min_counterexample
        print(f"  Минимальный контрпример: вход={inp}")
        print(f"    Ожидается : {ref}")
        print(f"    Получено  : {ai}")
        print("  Причина: ИИ-код использует строгие сравнения (< и >), ")
        print("  поэтому элементы, равные опорному, теряются.")

# ---------------------------------------------------------------------------
# 4. Шаг 4 методики: бенчмарк на трёх классах входов
# (методика — docs/reproducibility.md: прогрев, >=5 повторов, медиана)
# ---------------------------------------------------------------------------

SIZES = [500, 1_000, 2_000, 4_000, 8_000]
REPEATS = 5
INPUT_KINDS = ("random", "sorted", "reversed")


def make_input(rng: random.Random, n: int, kind: str) -> list[int]:
    a = [rng.randint(-1000, 1000) for _ in range(n)]
    if kind == "sorted":
        a.sort()
    elif kind == "reversed":
        a.sort(reverse=True)
    return a


def bench(fn, data: list[int]) -> float:
    fn(data)  # прогрев
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    print("\n=== ШАГ 4: Бенчмарк производительности ===")
    rng = random.Random(seed)
    for kind in INPUT_KINDS:
        print(f"\n  Класс входа: {kind}")
        for n in SIZES:
            data = make_input(rng, n, kind)
            try:
                t = bench(quicksort, data)
                print(f"    n={n:>6}  t={t:.6f} c")
            except RecursionError:
                print(f"    n={n:>6}  RecursionError (деградация глубины рекурсии)")
                

# ---------------------------------------------------------------------------
# 5. Самопроверка каркаса (граничные случаи + сверка с эталоном stdlib)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Проверяет вспомогательные функции до основной верификации."""
    assert is_sorted([]) and is_sorted([7]) and is_sorted([1, 2, 2, 3])
    assert not is_sorted([3, 1, 2])
    assert same_multiset([], []) and same_multiset([2, 1, 2], [1, 2, 2])
    assert not same_multiset([1, 1, 2], [1, 2, 2])
    print("self_check: OK")


def main() -> None:
    ap = argparse.ArgumentParser(description="Верификация ИИ-сортировки")
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    
    seed = 30 + args.variant
    random.seed(seed)
    
    self_check()
    rng = random.Random(seed)
    
    run_representative_tests(rng)
    compare_with_reference(rng, runs=300)
    run_benchmarks(seed)

if __name__ == "__main__":
    main()