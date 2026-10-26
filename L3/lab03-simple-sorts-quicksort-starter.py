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
import time

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. 
    Ожидаемая сложность: лучший случай O(n) (благодаря досрочному выходу), 
    средний и худший случаи O(n^2).
    """
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return arr, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. 
    Ожидаемая сложность: лучший случай O(n) (уже отсортирован), 
    средний и худший случаи O(n^2).
    """
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
    """Сортировка выбором. 
    Ожидаемая сложность: всегда O(n^2), так как число сравнений не зависит 
    от порядка элементов (всегда n*(n-1)/2).
    """
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n):
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

    Ожидаемая сложность: в среднем O(n log n), в худшем случае O(n^2).
    Рандомизация делает вероятность худшего случая крайне малой, независимо от входа.
    """
    if rng is None:
        rng = random.Random()
    arr = list(a)
    
    def _qs(lo: int, hi: int):
        if lo >= hi:
            return
        p_idx = rng.randrange(lo, hi)
        pivot = arr[p_idx]
        
        # Схема разбиения Ломуто
        arr[p_idx], arr[hi - 1] = arr[hi - 1], arr[p_idx]
        i = lo
        for j in range(lo, hi - 1):
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
        arr[i], arr[hi - 1] = arr[hi - 1], arr[i]
        
        _qs(lo, i)
        _qs(i + 1, hi)

    _qs(0, len(arr))
    return arr


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, отсортировать 
    каждой сортировкой по ключу и напечатать порядок меток при равных ключах.
    """
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (2, "e"), (1, "f")]
    
    # Обёртка для сравнения только по первому элементу (ключу)
    class KW:
        __slots__ = ('v',)
        def __init__(self, v): self.v = v
        def __lt__(self, o): return self.v[0] < o.v[0]
        def __le__(self, o): return self.v[0] <= o.v[0]
        def __gt__(self, o): return self.v[0] > o.v[0]
        def __ge__(self, o): return self.v[0] >= o.v[0]
        def __eq__(self, o): return self.v[0] == o.v[0]
        
    wrapped = [KW(p) for p in pairs]
    
    print("\n--- Stability Demo ---")
    print(f"Original: {pairs}")
    
    b_res, _, _ = bubble_sort(wrapped)
    print(f"Bubble:   {[x.v for x in b_res]}")
    
    i_res, _, _ = insertion_sort(wrapped)
    print(f"Insertion:{[x.v for x in i_res]}")
    
    s_res, _, _ = selection_sort(wrapped)
    print(f"Selection:{[x.v for x in s_res]}")
    
    q_res = quick_sort(wrapped, random.Random(42))
    print(f"Quick:    {[x.v for x in q_res]}")


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


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
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
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    
    # Сбор данных для графиков
    plot_data = {name: {cls: [] for cls in ["упорядоченный", "случайный", "обратный"]} 
                 for name in ["bubble_sort", "insertion_sort", "selection_sort", "quick_sort"]}
    
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                plot_data[name][cls].append((n, t))
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
                
    # Таблицы счётчиков сравнений и обменов
    print("\n--- Таблицы счётчиков сравнений и обменов ---")
    for n in SIZES_QUADRATIC:
        print(f"\nn = {n}")
        for cls, data in make_inputs(n, seed).items():
            print(f"  {cls}:")
            for sort_name, fn in [("bubble_sort", bubble_sort), 
                                  ("insertion_sort", insertion_sort), 
                                  ("selection_sort", selection_sort)]:
                _, comps, swaps = fn(list(data))
                print(f"    {sort_name:<15} comps={comps:<8} swaps={swaps}")

    # Построение log-log графиков
    try:
        import matplotlib.pyplot as plt
        for name in plot_data:
            plt.figure()
            for cls in ["упорядоченный", "случайный", "обратный"]:
                ns = [x[0] for x in plot_data[name][cls]]
                ts = [x[1] for x in plot_data[name][cls]]
                plt.loglog(ns, ts, marker='o', label=cls)
            plt.title(name)
            plt.xlabel("n (log scale)")
            plt.ylabel("Time, s (log scale)")
            plt.legend()
            plt.grid(True, which="both", ls="--")
            plt.savefig(f"{name}_plot.png")
            plt.close()
        print("\nГрафики сохранены в файлы *_plot.png")
    except ImportError:
        print("\nmatplotlib не установлен, графики не построены.")


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