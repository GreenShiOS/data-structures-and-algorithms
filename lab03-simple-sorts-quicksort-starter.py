#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
import math
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: O(n^2) (обосновать в отчёте).

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0
    
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return arr, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность: O(n^2) (лучший/худший случаи)."""
    arr = list(a)
    n = len(arr)
    comparisons = 0
    shifts = 0

    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        arr[j + 1] = key

    return arr, comparisons, shifts


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: O(n^2) (почему не зависит от входа?)."""
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0

    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1

    return arr, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем O(n logn), в худшем случае O(n^2) (обосновать
    в отчёте, объяснить роль рандомизации). rng передаётся снаружи, чтобы
    запуск был воспроизводим по seed варианта.
    """
    if rng is None:
        rng = random.Random()
    
    arr = list(a)
    
    def _qs(lo, hi):
        if lo >= hi:
            return
        
        pivot_idx = rng.randrange(lo, hi + 1)
        arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
        
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            if arr[j] < pivot:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
        
        arr[i], arr[hi] = arr[hi], arr[i]
        
        _qs(lo, i - 1)
        _qs(i + 1, hi)

    if len(arr) > 1:
        _qs(0, len(arr) - 1)
        
    return arr


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    print("\n--- Stability Demo ---")
    print(f"Input: {data}")
    
    algorithms = {
        "Bubble Sort": lambda x: bubble_sort(x)[0],
        "Insertion Sort": lambda x: insertion_sort(x)[0],
        "Selection Sort": lambda x: selection_sort(x)[0],
        "Quick Sort": lambda x: quick_sort(x, random.Random(42))
    }
    
    for name, sort_func in algorithms.items():
        test_data = list(data)
        sorted_data = sort_func(test_data)
        print(f"{name}: {sorted_data}")
        
    print("\nВывод:")
    print("- Bubble Sort и Insertion Sort стабильны.")
    print("- Selection Sort и Quick Sort нестабильны.")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_counters() -> None:
    """Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе."""
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10,
           f"selection_sort: неверный счётчик сравнений — {comparisons}, ожидалось 10")

def check_stability() -> None:
    """Проверка инварианта стабильности на парах (ключ, метка)."""
    data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    expected_stable = [(1, "b"), (1, "d"), (2, "a"), (2, "c")]
    
    stable_algos = {
        "bubble_sort": lambda x: bubble_sort(x)[0],
        "insertion_sort": lambda x: insertion_sort(x)[0],
    }
    
    for name, fn in stable_algos.items():
        res = fn(list(data))
        expect(res == expected_stable, 
               f"{name} нестабилен! Ожидалось {expected_stable}, получено {res}")

def check_counters_extended() -> None:
    """Дополнительные проверки счетчиков для пузырька и вставок."""
    arr_sorted = [1, 2, 3, 4, 5]
    _, comp_bub, swaps_bub = bubble_sort(arr_sorted)
    expect(comp_bub == 4, f"bubble_sort (sorted): ожидалось 4 сравнения, got {comp_bub}")
    expect(swaps_bub == 0, f"bubble_sort (sorted): ожидалось 0 обменов, got {swaps_bub}")
    
    arr_rev = [5, 4, 3, 2, 1]
    _, comp_ins, shifts_ins = insertion_sort(arr_rev)
    expect(shifts_ins == 10, f"insertion_sort (rev): ожидалось 10 сдвигов, got {shifts_ins}")

def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
    checks.append(("счетчики (bubble/insertion)", check_counters_extended))
    checks.append(("стабильность", check_stability))
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
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    plot_data = {}
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        plot_data[name] = {}
        for cls in ["упорядоченный", "случайный", "обратный"]:
            plot_data[name][cls] = {}
            
        for n in sizes:
            inputs = make_inputs(n, seed)
            for cls, data in inputs.items():
                t = bench(fn, data)
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f}")
                plot_data[name][cls][n] = t

    if plt:
        _plot_results(plot_data, SIZES_QUADRATIC, SIZES_QUICK)
    else:
        print("\nMatplotlib not found. Install it to see graphs.")


def _plot_results(plot_data, sizes_quad, sizes_quick):
    """Строит log-log графики времени сортировки."""
    algos_quad = ["bubble_sort", "insertion_sort", "selection_sort"]
    input_types = ["упорядоченный", "случайный", "обратный"]
    colors = ['blue', 'green', 'red']
    
    
    plt.figure(figsize=(10, 6))
    for algo in algos_quad:
        for idx, inp_type in enumerate(input_types):
            times = [max(plot_data[algo][inp_type][n], 1e-9) for n in sizes_quad]
            plt.loglog(sizes_quad, times, marker='o', label=f"{algo} ({inp_type})", color=colors[idx])
    plt.title("Quadratic Sorts Performance (Log-Log)")
    plt.xlabel("Input Size (n)")
    plt.ylabel("Time (seconds)")
    plt.legend(loc="upper left", fontsize=8)
    plt.grid(True, which="both", ls="-")
    plt.savefig("quadratic_sorts.png")
    print("Saved quadratic_sorts.png")
    
    
    plt.figure(figsize=(10, 6))
    for idx, inp_type in enumerate(input_types):
        times = [max(plot_data["quick_sort"][inp_type][n], 1e-9) for n in sizes_quick]
        plt.loglog(sizes_quick, times, marker='s', label=f"quick_sort ({inp_type})", color=colors[idx])
    
   
    c_val = times[-1] / (sizes_quick[-1] * math.log2(sizes_quick[-1]))
    theoretical = [c_val * n * math.log2(n) for n in sizes_quick]
    plt.loglog(sizes_quick, theoretical, 'k--', label="O(n log n) reference")
    
    plt.title("QuickSort Performance (Log-Log)")
    plt.xlabel("Input Size (n)")
    plt.ylabel("Time (seconds)")
    plt.legend(loc="upper left", fontsize=8)
    plt.grid(True, which="both", ls="-")
    plt.savefig("quicksort_performance.png")
    print("Saved quicksort_performance.png")
    plt.show()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()