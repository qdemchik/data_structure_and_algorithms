#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности.
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
import sys

# Увеличиваем лимит рекурсии для глубоких вызовов (актуально для Python)
sys.setrecursionlimit(200000)

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список."""
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
    """MergeSort: O(n log n) по времени, O(n) по памяти."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max]."""
    if not a:
        return []
    
    k = key_max + 1
    count = [0] * k
    for x in a:
        count[x] += 1
        
    for i in range(1, k):
        count[i] += count[i - 1]
        
    res = [0] * len(a)
    for x in reversed(a):
        idx = count[x] - 1
        res[idx] = x
        count[x] -= 1
        
    return res


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые."""
    if not a:
        return []
    
    max_val = max(a)
    if max_val == 0:
        return list(a)
        
    res = list(a)
    exp = 1
    while max_val // exp > 0:
        count = [0] * 10
        for x in res:
            digit = (x // exp) % 10
            count[digit] += 1
            
        for i in range(1, 10):
            count[i] += count[i - 1]
            
        next_res = [0] * len(res)
        for x in reversed(res):
            digit = (x // exp) % 10
            idx = count[digit] - 1
            next_res[idx] = x
            count[digit] -= 1
            
        res = next_res
        exp *= 10
        
    return res


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        largest = i
        left_child = 2 * i + 1
        right_child = 2 * i + 2
        
        if left_child < n and a[left_child] > a[largest]:
            largest = left_child
        if right_child < n and a[right_child] > a[largest]:
            largest = right_child
            
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            i = largest
        else:
            break


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: O(n log n) по времени, O(1) по памяти."""
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
        
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def quick_sort(a: list[int]) -> list[int]:
    """QuickSort с 3-частным разбиением (Dutch National Flag).
    Идеально обрабатывает массивы с большим числом дубликатов, 
    предотвращая RecursionError и деградацию до O(n^2).
    """
    rng = random.Random(0)
    arr = list(a)
    
    def _qs(lo: int, hi: int):
        if lo >= hi:
            return
        
        p_idx = rng.randrange(lo, hi)
        pivot = arr[p_idx]
        
        # 3-частное разбиение:
        # lt: граница элементов < pivot
        # gt: граница элементов > pivot
        lt = lo
        gt = hi - 1
        i = lo
        
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
                
        # Рекурсивно сортируем только части строго меньше и строго больше pivot.
        # Элементы, равные pivot, уже стоят на своих местах и не обрабатываются.
        _qs(lo, lt)
        _qs(gt + 1, hi)

    _qs(0, len(arr))
    return arr


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные и типовые случаи, стабильность, сверка с эталоном sorted()."""
    assert merge_sort([]) == []
    assert merge_sort([7]) == [7]
    assert merge_sort([5, 5, 5]) == [5, 5, 5]
    assert counting_sort([], key_max=10) == []
    assert radix_sort_lsd([0]) == [0]
    single = [42]
    heap_sort(single)
    assert single == [42]

    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    assert merge_sort(pairs, key=lambda p: p[0]) == sorted(pairs, key=lambda p: p[0])

    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        expected = sorted(a)
        assert merge_sort(a) == expected
        assert counting_sort(a, key_max=999) == expected
        assert radix_sort_lsd(a) == expected
        buf = list(a)
        heap_sort(buf)
        assert buf == expected
        assert quick_sort(a) == expected
        
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100
WIDE_KEY_MAX = 10**9


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):
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
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом."""
    fn(list(data))
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted()", sorted),
    ]
    
    plot_data = {name: {dist: [] for dist in ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]} 
                 for name, _ in algorithms}

    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                
                t = bench(fn, data)
                plot_data[algo_name][dist_name].append((n, t))
                print(f"    {algo_name:>18}: t = {t:.6f} c")

    try:
        import matplotlib.pyplot as plt
        for algo_name in plot_data:
            plt.figure(figsize=(10, 6))
            for dist_name in plot_data[algo_name]:
                ns = [x[0] for x in plot_data[algo_name][dist_name]]
                ts = [x[1] for x in plot_data[algo_name][dist_name]]
                plt.loglog(ns, ts, marker='o', label=dist_name)
            plt.title(f"Performance: {algo_name}")
            plt.xlabel("n (log scale)")
            plt.ylabel("Time, s (log scale)")
            plt.legend()
            plt.grid(True, which="both", ls="--")
            plt.savefig(f"bench_{algo_name}.png")
            plt.close()
        print("\nГрафики успешно сохранены в файлы bench_*.png")
    except ImportError:
        print("\n[Предупреждение] matplotlib не установлен. Графики не построены.")


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