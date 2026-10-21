#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.

    Стабильность: при равенстве ключей элемент из left идёт раньше.
    Ожидаемая сложность: O( len(left) + len(right)) (обосновать в отчёте).
    """
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res

def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список. Ожидаемая сложность: O(n log n)."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].

    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Ожидаемые время и память: O(n+k) — n число элементов, k = key_max + 1 диапозон ключей;
    ограничение диапазона ключей обсудить в отчёте.
    """
    if not a:
        return []
    k = key_max + 1
    count = [0] * k
    for x in a:
        count[x] += 1
    for i in range(1, k):
        count[i] += count[i - 1]
    res = [0] * len(a)
    for i in range(len(a) - 1, -1, -1):
        x = a[i]
        count[x] -= 1
        res[count[x]] = x
    return res
    raise NotImplementedError


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.

    Поверх устойчивой поразрядной counting-сортировки: от младшего разряда
    к старшему. Ожидаемая сложность: O(d(n+b)) — d число разрядов, b основание СС, n кол-во элементов.
    """
    if not a:
        return []
    max_val = max(a)
    exp = 1
    res = list(a)
    while max_val // exp > 0:
        count = [0] * 10
        for x in res:
            digit = (x // exp) % 10
            count[digit] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        next_res = [0] * len(res)
        for i in range(len(res) - 1, -1, -1):
            x = res[i]
            digit = (x // exp) % 10
            count[digit] -= 1
            next_res[count[digit]] = x
        res = next_res
        exp *= 10
    return res
    raise NotImplementedError


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    largest = i
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            i = largest
        else:
            break


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте, без вспомогательного массива.

    Схема: построение max-кучи просейками вниз (снизу вверх, O(n)),
    затем обмен вершины с последним элементом и просейка. Сложность: O(n logn).
    """
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        sift_down(a, 0, i)

def quick_sort(a: list[int]) -> list[int]:
    """QuickSort с рандомизацией опорного элемента — перенести из своей ЛР 3."""
    def _qs(arr: list, low: int, high: int) -> None:
        if low >= high:
            return
        pivot_idx = random.randint(low, high)
        pivot = arr[pivot_idx]
        
        lt = low
        gt = high
        i = low
        while i <= gt:
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[gt], arr[i] = arr[i], arr[gt]
                gt -= 1
            else:
                i += 1
        
        _qs(arr, low, lt - 1)
        _qs(arr, gt + 1, high)

    res = list(a)
    _qs(res, 0, len(res) - 1)
    return res


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")

def check_heap_invariant() -> None:
    """Проверка свойства max-кучи после фазы построения."""
    rng = random.Random(42)
    for _ in range(50):
        n = rng.randint(1, 100)
        a = [rng.randint(0, 999) for _ in range(n)]
        buf = list(a)
        for i in range(n // 2 - 1, -1, -1):
            sift_down(buf, i, n)
        for i in range(n // 2):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n:
                expect(buf[i] >= buf[left],
                       f"куча: buf[{i}]={buf[i]} < buf[{left}]={buf[left]}")
            if right < n:
                expect(buf[i] >= buf[right],
                       f"куча: buf[{i}]={buf[i]} < buf[{right}]={buf[right]}")

def check_radix_stability() -> None:
    """Устойчивость radix: элементы с одинаковым значением сохраняют исходный порядок.
    Проверяем через сортировку пар (значение, исходный индекс)."""
    def radix_pairs(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not pairs:
            return []
        max_val = max(p[0] for p in pairs)
        exp = 1
        res = list(pairs)
        while max_val // exp > 0:
            count = [0] * 10
            for p in res:
                digit = (p[0] // exp) % 10
                count[digit] += 1
            for i in range(1, 10):
                count[i] += count[i - 1]
            next_res = [None] * len(res)
            for i in range(len(res) - 1, -1, -1):
                p = res[i]
                digit = (p[0] // exp) % 10
                count[digit] -= 1
                next_res[count[digit]] = p
            res = next_res
            exp *= 10
        return res

    rng = random.Random(123)
    pairs = [(rng.randint(0, 10), i) for i in range(200)]
    sorted_pairs = radix_pairs(pairs)
    prev_val = -1
    prev_idx = -1
    for val, idx in sorted_pairs:
        if val == prev_val:
            expect(idx > prev_idx,
                   f"radix нестабилен: ({prev_val},{prev_idx}) идёт перед ({val},{idx})")
        prev_val, prev_idx = val, idx
    expect(sorted_pairs == sorted(pairs, key=lambda p: p[0]),
           "radix_pairs расходится с sorted()")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    checks.append(("инвариант кучи", check_heap_invariant))
    checks.append(("устойчивость radix", check_radix_stability))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def plot_benchmarks(results: dict) -> None:
    """Строит log-log графики времени сортировки для каждого распределения."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[!] matplotlib не установлен. Графики не будут построены.")
        return

    dist_names = ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]
    dist_titles = ["Случайные (широкий диапазон)", "Случайные (узкий диапазон)", 
                   "Уже отсортированные", "Обратно отсортированные", "Почти отсортированные"]

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, dist in enumerate(dist_names):
        ax = axes[idx]
        ax.set_title(dist_titles[idx])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Размер массива (n)")
        ax.set_ylabel("Время выполнения (с)")
        ax.grid(True, which="both", linestyle="--", alpha=0.6)

        for algo_name, data in results.items():
            if dist in data and data[dist]:
                ns = [point[0] for point in data[dist]]
                ts = [point[1] for point in data[dist]]
                ax.plot(ns, ts, marker="o", label=algo_name, linewidth=1.5)
        ax.legend(fontsize=8, loc="upper left")

    axes[5].axis('off')
    plt.tight_layout()
    plt.savefig("lab04_benchmarks.png", dpi=150)
    print("\n[OK] Графики сохранены в файл: lab04_benchmarks.png")


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort (ЛР 3)", quick_sort),
        ("sorted() (эталон)", sorted),
    ]

    results = {name: {dist: [] for dist in ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]} 
               for name, _ in algorithms}

    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting; зафиксировать в таблице свойств
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                t = bench(fn, data)  # Сохраняем результат в переменную
                print(f"    {algo_name:>18}: t = {t:.6f} c")
                results[algo_name][dist_name].append((n, t))

    plot_benchmarks(results)
    


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()