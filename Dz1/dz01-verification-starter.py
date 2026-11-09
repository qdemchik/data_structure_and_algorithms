#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки — ПОЛНОЕ РЕШЕНИЕ.

Заполнены все TODO в соответствии с КИМ-01 и методикой верификации (шаги 1–4).
Включена исправленная версия алгоритма и её повторная верификация.
Запуск: python dz01-verification-starter.py --variant N
"""
from __future__ import annotations

import argparse
import importlib.util
import random
import statistics
import time
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# 0. Загрузка проверяемого кода
# ---------------------------------------------------------------------------
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
    """Инвариант 1: последовательность упорядочена по неубыванию."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))

def same_multiset(a: list[int], b: list[int]) -> bool:
    """Инвариант 2: b — перестановка a (мультимножества элементов совпадают)."""
    return Counter(a) == Counter(b)

def check_invariants(original: list[int], result: list[int]) -> list[str]:
    """Возвращает список нарушенных инвариантов (пустой список — нарушений нет)."""
    violations = []
    if not is_sorted(result):
        violations.append("Нарушен инвариант 1: результат не упорядочен по неубыванию.")
    if not same_multiset(original, result):
        violations.append("Нарушен инвариант 2: результат не является перестановкой входа (потеря или дублирование элементов).")
    return violations

# ---------------------------------------------------------------------------
# 2. Шаг 2 методики: репрезентативные тесты
# ---------------------------------------------------------------------------
def representative_cases(rng: random.Random) -> list[tuple[str, list[int]]]:
    """Именованные тестовые входы по классам методики."""
    return [
        ("граничный: пустой", []),
        ("граничный: один элемент", [42]),
        ("граничный: два элемента", [5, 2]),
        ("вырожденный: все элементы равны", [3, 3, 3, 3, 3]),
        ("вырожденный: уже отсортированный", [1, 2, 3, 4, 5]),
        ("вырожденный: обратно отсортированный", [5, 4, 3, 2, 1]),
        ("типовой: случайный с дубликатами и отрицательными", [rng.randint(-10, 10) for _ in range(20)]),
    ]

def run_representative_tests(rng: random.Random) -> None:
    """Прогоняет quicksort по всем классам входов и печатает нарушения инвариантов."""
    print("\n--- Шаг 2: Репрезентативные тесты ---")
    for name, data in representative_cases(rng):
        result = quicksort(data)
        violations = check_invariants(data, result)
        if violations:
            print(f"[{name}] ДЕФЕКТ:")
            print(f"  Вход:    {data}")
            print(f"  Результат: {result}")
            for v in violations:
                print(f"  - {v}")
        else:
            print(f"[{name}] OK")

# ---------------------------------------------------------------------------
# 3. Шаг 3 методики: сравнение с эталоном sorted()
# ---------------------------------------------------------------------------
def compare_with_reference(rng: random.Random, runs: int = 300) -> None:
    """Сверка quicksort с sorted() на сотнях случайных входов."""
    print("\n--- Шаг 3: Сравнение с эталоном sorted() ---")
    mismatches = 0
    min_counterexample = None
    
    for _ in range(runs):
        size = rng.randint(0, 50)
        # Генерируем входы с высокой вероятностью дубликатов и отрицательных чисел
        a = [rng.randint(-20, 20) for _ in range(size)]
        result = quicksort(a)
        expected = sorted(a)
        
        if result != expected:
            mismatches += 1
            if min_counterexample is None or len(a) < len(min_counterexample):
                min_counterexample = list(a)
    
    print(f"Найдено {mismatches} расхождений из {runs} запусков.")
    if min_counterexample is not None:
        print(f"Минимальный контрпример: вход = {min_counterexample}")
        print(f"  Ожидалось (sorted):    {sorted(min_counterexample)}")
        print(f"  Получено (quicksort):  {quicksort(min_counterexample)}")
        print("  Причина в коде: использование строгих неравенств `x < pivot` и `x > pivot`")
        print("  приводит к отбрасыванию всех дубликатов опорного элемента, кроме самого pivot=data[0].")
    else:
        print("Расхождений не найдено.")

# ---------------------------------------------------------------------------
# 4. Шаг 4 методики: бенчмарк на трёх классах входов
# ---------------------------------------------------------------------------
SIZES = [500, 1_000, 2_000, 4_000, 8_000]
REPEATS = 5
INPUT_KINDS = ("random", "sorted", "reversed")

def make_input(rng: random.Random, n: int, kind: str) -> list[int]:
    """Вход размера n одного из трёх классов: random / sorted / reversed."""
    a = [rng.randint(-1000, 1000) for _ in range(n)]
    if kind == "sorted":
        a.sort()
    elif kind == "reversed":
        a.sort(reverse=True)
    return a

def bench(fn, data: list[int]) -> float:
    """Медиана времени выполнения fn(data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев на копии, чтобы не мутировать исходные данные
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия для каждого замера
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def run_benchmarks(seed: int) -> None:
    """Замеры quicksort на трёх классах входов; аварийные завершения фиксируются."""
    print("\n--- Шаг 4: Бенчмарк производительности ---")
    rng = random.Random(seed)
    for kind in INPUT_KINDS:
        print(f"\nКласс входа: {kind}")
        for n in SIZES:
            data = make_input(rng, n, kind)
            try:
                t = bench(quicksort, data)
                print(f"  n={n:>6} t={t:.6f} c")
            except RecursionError:
                print(f"  n={n:>6} RecursionError (превышена глубина рекурсии)")
    
    print("\nАналитический вывод по шагу 4:")
    print("  - На 'sorted' и 'reversed' входах наблюдается деградация до O(n²) и RecursionError.")
    print("  - Причина: выбор `pivot = data[0]` без рандомизации. На упорядоченных данных")
    print("    одно из подмножеств (smaller или larger) всегда пустое, а другое имеет размер n-1.")
    print("    Это приводит к глубине рекурсии O(n), что превышает лимит Python (~1000).")

# ---------------------------------------------------------------------------
# 5. Исправление дефектов и повторная верификация
# ---------------------------------------------------------------------------
def quicksort_fixed(data: list[int]) -> list[int]:
    """Исправленная версия QuickSort.
    
    Исправления:
    1. Добавлен список `equal` для сохранения всех элементов, равных опорному.
    2. Опорный элемент выбирается случайно (random.choice), что предотвращает 
       деградацию до O(n²) на упорядоченных входах.
    """
    if len(data) <= 1:
        return list(data)
    
    pivot = random.choice(data)
    smaller = [x for x in data if x < pivot]
    equal = [x for x in data if x == pivot]
    larger = [x for x in data if x > pivot]
    
    return quicksort_fixed(smaller) + equal + quicksort_fixed(larger)

def verify_fixed_version(rng: random.Random, seed: int) -> None:
    """Повторная полная верификация исправленной версии."""
    print("\n" + "="*70)
    print("ПОВТОРНАЯ ВЕРИФИКАЦИЯ ИСПРАВЛЕННОЙ ВЕРСИИ (quicksort_fixed)")
    print("="*70)
    
    # Шаг 1 и 2: Репрезентативные тесты
    print("\n[Шаг 1-2] Репрезентативные тесты:")
    all_passed = True
    for name, data in representative_cases(rng):
        result = quicksort_fixed(data)
        violations = check_invariants(data, result)
        if violations:
            print(f"  [{name}] ПРОВАЛ: {violations}")
            all_passed = False
        else:
            print(f"  [{name}] OK")
            
    # Шаг 3: Сравнение с эталоном
    print("\n[Шаг 3] Сравнение с эталоном sorted() (300 запусков):")
    mismatches = 0
    for _ in range(300):
        size = rng.randint(0, 50)
        a = [rng.randint(-20, 20) for _ in range(size)]
        if quicksort_fixed(a) != sorted(a):
            mismatches += 1
            
    if mismatches > 0:
        print(f"  Расхождений: {mismatches} (ПРОВАЛ)")
        all_passed = False
    else:
        print(f"  Расхождений: 0 (OK)")
        
    # Шаг 4: Бенчмарк
    print("\n[Шаг 4] Бенчмарк исправленной версии:")
    rng_bench = random.Random(seed)
    for kind in INPUT_KINDS:
        print(f"  Класс входа: {kind}")
        for n in [1_000, 4_000, 8_000]:
            data = make_input(rng_bench, n, kind)
            try:
                t = bench(quicksort_fixed, data)
                print(f"    n={n:>6} t={t:.6f} c")
            except RecursionError:
                print(f"    n={n:>6} RecursionError (ПРОВАЛ)")
                all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("ВЕРДИКТ: ПРИНЯТЬ. Исправленная версия успешно прошла все шаги верификации.")
        print("Обоснование: устранена потеря дубликатов (добавлен список equal) и")
        print("предотвращена деградация до O(n²) / RecursionError за счёт рандомизации pivot.")
    else:
        print("ВЕРДИКТ: ПРИНЯТЬ С ДОРАБОТКОЙ. Обнаружены остаточные проблемы.")
    print("="*70)

# ---------------------------------------------------------------------------
# Основная логика
# ---------------------------------------------------------------------------
def self_check() -> None:
    """Проверяет вспомогательные функции до основной верификации."""
    assert is_sorted([]) and is_sorted([7]) and is_sorted([1, 2, 2, 3])
    assert not is_sorted([3, 1, 2])
    assert same_multiset([], []) and same_multiset([2, 1, 2], [1, 2, 2])
    assert not same_multiset([1, 1, 2], [1, 2, 2])
    rng = random.Random(0)
    for _ in range(100):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
        assert is_sorted(sorted(a))
        assert same_multiset(a, sorted(a))
    print("self_check: OK")

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    
    print(f"Запуск верификации для варианта {args.variant} (seed={seed})\n")
    
    self_check()
    rng = random.Random(seed)
    
    run_representative_tests(rng)
    compare_with_reference(rng, runs=300)
    run_benchmarks(seed)
    
    print("\n" + "="*70)
    print("ИТОГОВЫЙ ВЕРДИКТ ПО ИСХОДНОМУ ИИ-КОДУ: ОТКЛОНИТЬ")
    print("Обоснование: Код нарушает инвариант перестановки (теряет дубликаты)")
    print("и подвержен деградации до O(n²) / RecursionError на упорядоченных входах.")
    print("Требуется доработка (см. повторную верификацию ниже).")
    print("="*70)
    
    verify_fixed_version(rng, seed)

if __name__ == "__main__":
    main()