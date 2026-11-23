#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 6. Линейный, бинарный и интерполяционный поиск — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-06 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Каждая функция поиска работает с отсортированным по неубыванию массивом
и возвращает пару (индекс найденного элемента или -1, число сравнений ключей).

Запуск: python lab06-search-starter.py --variant N
"""
from __future__ import annotations

import argparse
import bisect
import random
import statistics
import time
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска (реализуются вручную, без in/index/bisect в основной части)
# ---------------------------------------------------------------------------


def linear_search(a: list[int], key: int) -> tuple[int, int]:
    """Линейный поиск первого вхождения key.

    Возвращает (индекс первого вхождения или -1, число сравнений ключей).
    Ожидаемая сложность: O(n) по времени, O(1) по памяти.  (обосновать в отчёте).
    """
    comparisons = 0
    for i, val in enumerate(a):
        comparisons += 1
        if val == key:
            return i, comparisons
    return -1, comparisons


def binary_search(a: list[int], key: int) -> tuple[int, int]:
    """Бинарный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Аккуратно поддерживайте инвариант обеих границ lo и hi: искомый элемент,
    если он есть, всегда лежит в текущем отрезке; цикл обязан завершаться.
    Ожидаемая сложность: O(log n) по времени, O(1) по памяти.
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        elif a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons


def interpolation_search(a: list[int], key: int) -> tuple[int, int]:
    """Интерполяционный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Позиция зонда: mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo]).
    Обязательно защититься от деления на ноль при a[hi] == a[lo] и от выхода
    key за пределы [a[lo], a[hi]]. Средняя сложность на равномерных данных: O(n) на сильно неравномерных данных.
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    
    while lo <= hi:
        if key < a[lo] or key > a[hi]:
            comparisons += 2
            break
        comparisons += 2
        
        if lo == hi:
            comparisons += 1
            if a[lo] == key:
                return lo, comparisons
            return -1, comparisons
        
        if a[lo] == a[hi]:
            comparisons += 1
            if a[lo] == key:
                return lo, comparisons
            return -1, comparisons
        
        mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        
        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        elif a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
            
    return -1, comparisons


# ---------------------------------------------------------------------------
# 2. Данные по варианту: два распределения, присутствующие/отсутствующие ключи
# ---------------------------------------------------------------------------


def make_dataset(n: int, distribution: str, rng: random.Random) -> list[int]:
    """Отсортированный массив n ключей: 'uniform' — равномерное распределение,
    'exponential' — неравномерное (экспоненциальное, значения сгущаются у нуля)."""
    if distribution == "uniform":
        return sorted(rng.randint(0, 10 * n) for _ in range(n))
    if distribution == "exponential":
        return sorted(int(rng.expovariate(1.0 / 1000.0)) for _ in range(n))
    raise ValueError(f"неизвестное распределение: {distribution!r}")


def pick_keys(a: list[int], rng: random.Random, count: int,
              present: bool) -> list[int]:
    """count ключей для серии поисков: присутствующие берутся из массива,
    отсутствующие подбираются вне множества его значений."""
    if present:
        return [a[rng.randrange(len(a))] for _ in range(count)]
    have = set(a)
    hi = (a[-1] if a else 0) + 2
    keys: list[int] = []
    while len(keys) < count:
        k = rng.randint(-hi, hi)
        if k not in have:
            keys.append(k)
    return keys


# ---------------------------------------------------------------------------
# 3. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------

ALGORITHMS = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
]


def self_check() -> None:
    """Граничные случаи + сверка с эталоном (оператор in, list.index, bisect)."""
    for name, fn in ALGORITHMS:
        # Пустой массив: элемент не найден, сравнений нет.
        assert fn([], 1) == (-1, 0), f"{name}: пустой массив"
        # Один элемент: найден / не найден.
        assert fn([7], 7)[0] == 0, f"{name}: один элемент, ключ найден"
        assert fn([7], 3)[0] == -1, f"{name}: один элемент, ключ отсутствует"
        # Первый, последний и отсутствующие ключи (внутри и вне диапазона).
        a = [1, 3, 3, 5, 8, 13, 21]
        assert fn(a, 1)[0] == 0, f"{name}: первый элемент"
        assert fn(a, 21)[0] == len(a) - 1, f"{name}: последний элемент"
        assert fn(a, 4)[0] == -1, f"{name}: отсутствующий ключ внутри диапазона"
        assert fn(a, 100)[0] == -1, f"{name}: ключ вне диапазона"

    # Сверка с эталоном стандартной библиотеки на случайных массивах.
    rng = random.Random(0)
    for _ in range(300):
        a = sorted(rng.randint(0, 60) for _ in range(rng.randint(1, 40)))
        key = rng.randint(-5, 65)
        # Эталон присутствия ключа — bisect_left (и, эквивалентно, оператор in).
        j = bisect.bisect_left(a, key)
        present = j < len(a) and a[j] == key
        assert present == (key in a)
        for name, fn in ALGORITHMS:
            idx, cmp_count = fn(a, key)
            assert cmp_count >= 1, f"{name}: счётчик сравнений не ведётся"
            if present:
                # При дубликатах бинарный/интерполяционный могут вернуть
                # любое вхождение — проверяем значение по индексу.
                assert idx != -1 and a[idx] == key, f"{name}: ключ не найден"
            else:
                assert idx == -1, f"{name}: найден отсутствующий ключ"
        # Линейный поиск обязан возвращать первое вхождение — эталон list.index.
        if present:
            assert linear_search(a, key)[0] == a.index(key)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Бенчмарк: сравнения и время от n (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
N_KEYS = 200


def bench(fn, a: list[int], keys: list[int]) -> float:
    for k in keys:
        fn(a, k)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def mean_comparisons(fn, a: list[int], keys: list[int]) -> float:
    return statistics.mean(fn(a, k)[1] for k in keys)


def run_benchmarks_and_plot(seed: int) -> None:
    rng = random.Random(seed)
    
    plot_data = {
        "uniform": {"present": {}, "absent": {}},
        "exponential": {"present": {}, "absent": {}}
    }
    
    for dist in ("uniform", "exponential"):
        for present in (True, False):
            state = "present" if present else "absent"
            for name, _ in ALGORITHMS:
                plot_data[dist][state][name] = {"n": [], "cmp": [], "time": []}

    for distribution in ("uniform", "exponential"):
        print(f"\nРаспределение: {distribution}")
        for n in SIZES:
            a = make_dataset(n, distribution, rng)
            for present in (True, False):
                keys = pick_keys(a, rng, N_KEYS, present)
                label = "есть" if present else "нет"
                for name, fn in ALGORITHMS:
                    if name == "linear" and n > 30_000:
                        continue
                    
                    cmp_avg = mean_comparisons(fn, a, keys)
                    t_avg = bench(fn, a, keys)
                    
                    print(f"  n={n:>7}  ключ {label:<4}  {name:<13}  "
                          f"сравнений={cmp_avg:>10.1f}  t={t_avg:.6f} c")
                    
                    state = "present" if present else "absent"
                    plot_data[distribution][state][name]["n"].append(n)
                    plot_data[distribution][state][name]["cmp"].append(cmp_avg)
                    plot_data[distribution][state][name]["time"].append(t_avg)

    plot_results(plot_data)


def plot_results(plot_data: dict) -> None:
    """Построение и сохранение графиков сравнений и времени."""
    colors = {"linear": "red", "binary": "blue", "interpolation": "green"}
    markers = {"linear": "o", "binary": "s", "interpolation": "^"}

    for distribution in ("uniform", "exponential"):
        for state, state_name in (("present", "Присутствующие ключи"), ("absent", "Отсутствующие ключи")):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            fig.suptitle(f"Поиск: {distribution.capitalize()} распределение ({state_name})")

            for name in ("linear", "binary", "interpolation"):
                data = plot_data[distribution][state][name]
                if not data["n"]:
                    continue
                
                ax1.plot(data["n"], data["cmp"], marker=markers[name], color=colors[name], label=name.capitalize())
                ax2.plot(data["n"], data["time"], marker=markers[name], color=colors[name], label=name.capitalize())

            ax1.set_xlabel("Размер массива (n)")
            ax1.set_ylabel("Среднее число сравнений")
            ax1.set_xscale("log")
            ax1.legend()
            ax1.grid(True, which="both", ls="--")

            ax2.set_xlabel("Размер массива (n)")
            ax2.set_ylabel("Время выполнения (сек)")
            ax2.set_xscale("log")
            ax2.set_yscale("log")
            ax2.legend()
            ax2.grid(True, which="both", ls="--")

            plt.tight_layout()
            filename = f"plot_{distribution}_{state}.png"
            plt.savefig(filename, dpi=150)
            print(f"График сохранён: {filename}")
            plt.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="ЛР 6: Сравнение алгоритмов поиска")
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    
    seed = 30 + args.variant
    random.seed(seed)
    
    print(f"Запуск с seed={seed} (вариант {args.variant})")
    self_check()
    run_benchmarks_and_plot(seed)


if __name__ == "__main__":
    main()