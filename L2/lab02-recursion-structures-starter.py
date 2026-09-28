#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 2. Рекурсивные функции; динамический массив, стек и дек.
Запуск: python lab02-recursion-structures-starter.py --variant N
"""
from __future__ import annotations

import argparse
import collections
import math
import random
import statistics
import time

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ---------------------------------------------------------------------------
# 1. Рекурсивные функции
# ---------------------------------------------------------------------------

CALLS = {"fib_naive": 0, "fib_memo": 0}

def factorial(n: int) -> int:
    """Факториал n >= 0 рекурсивно. Ожидаемая сложность: Θ(n)."""
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fib_naive(n: int) -> int:
    """n-е число Фибоначчи наивной рекурсией."""
    CALLS["fib_naive"] += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

def fib_memo(n: int, memo: dict[int, int] | None = None) -> int:
    """n-е число Фибоначчи с мемоизацией."""
    CALLS["fib_memo"] += 1  # Считаем ВХОД в функцию (до проверки кэша)
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n < 2:
        return n
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

def hanoi(n: int, src: str = "A", dst: str = "C", aux: str = "B") -> int:
    """Ханойские башни: вернуть число перемещений n дисков (src -> dst)."""
    if n == 0:
        return 0
    moves = hanoi(n - 1, src, aux, dst)
    moves += 1
    moves += hanoi(n - 1, aux, dst, src)
    return moves

# ---------------------------------------------------------------------------
# 2. Динамический массив с ручным управлением ёмкостью (рост x2)
# ---------------------------------------------------------------------------

class DynamicArray:
    INITIAL_CAPACITY = 4

    def __init__(self) -> None:
        self._capacity = self.INITIAL_CAPACITY
        self._size = 0
        self._buffer: list = [None] * self._capacity

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _grow(self) -> None:
        new_capacity = self._capacity * 2
        new_buffer = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[i]
        self._buffer = new_buffer
        self._capacity = new_capacity

    def append(self, value) -> None:
        if self._size == self._capacity:
            self._grow()
        self._buffer[self._size] = value
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise IndexError("pop from empty DynamicArray")
        self._size -= 1
        val = self._buffer[self._size]
        self._buffer[self._size] = None
        
        # Сжатие буфера при заполнении <= 1/4 (слайд 17 лекции)
        if self._size > 0 and self._size <= self._capacity // 4:
            new_capacity = self._capacity // 2
            new_buffer = [None] * new_capacity
            for i in range(self._size):
                new_buffer[i] = self._buffer[i]
            self._buffer = new_buffer
            self._capacity = new_capacity
            
        return val

    def get(self, index: int):
        if index < 0 or index >= self._size:
            raise IndexError("DynamicArray index out of bounds")
        return self._buffer[index]

    def set(self, index: int, value) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("DynamicArray index out of bounds")
        self._buffer[index] = value

# ---------------------------------------------------------------------------
# 3. Стек и дек на базе собственных структур
# ---------------------------------------------------------------------------

class Stack:
    def __init__(self) -> None:
        self._data = DynamicArray()

    def __len__(self) -> int:
        return len(self._data)

    def push(self, value) -> None:
        self._data.append(value)

    def pop(self):
        return self._data.pop()

    def peek(self):
        if len(self._data) == 0:
            raise IndexError("peek from empty stack")
        return self._data.get(len(self._data) - 1)

class _Node:
    __slots__ = ("value", "prev", "next")

    def __init__(self, value, prev=None, next=None) -> None:
        self.value = value
        self.prev = prev
        self.next = next

class Deque:
    def __init__(self) -> None:
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push_front(self, value) -> None:
        new_node = _Node(value)
        if self._size == 0:
            self._head = self._tail = new_node
        else:
            new_node.next = self._head
            self._head.prev = new_node
            self._head = new_node
        self._size += 1

    def push_back(self, value) -> None:
        new_node = _Node(value)
        if self._size == 0:
            self._head = self._tail = new_node
        else:
            new_node.prev = self._tail
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def pop_front(self):
        if self._size == 0:
            raise IndexError("pop from empty deque")
        val = self._head.value
        self._head = self._head.next
        if self._head is not None:
            self._head.prev = None
        else:
            self._tail = None  # КРИТИЧЕСКИ ВАЖНО: обнуление tail (слайд 24)
        self._size -= 1
        return val

    def pop_back(self):
        if self._size == 0:
            raise IndexError("pop from empty deque")
        val = self._tail.value
        self._tail = self._tail.prev
        if self._tail is not None:
            self._tail.next = None
        else:
            self._head = None  # КРИТИЧЕСКИ ВАЖНО: обнуление head
        self._size -= 1
        return val

# ---------------------------------------------------------------------------
# 4. Репрезентативные тесты и инварианты
# ---------------------------------------------------------------------------

def self_check() -> None:
    assert factorial(0) == 1
    for n in range(0, 12):
        assert factorial(n) == math.factorial(n)
    
    CALLS["fib_naive"] = CALLS["fib_memo"] = 0
    assert fib_naive(10) == 55
    assert fib_memo(10) == 55
    assert CALLS["fib_memo"] < CALLS["fib_naive"]
    
    for n in (0, 1, 3, 8):
        assert hanoi(n) == 2 ** n - 1

    arr, ref = DynamicArray(), []
    for i in range(100):
        arr.append(i * i)
        ref.append(i * i)
        assert len(arr) == len(ref) <= arr.capacity
    assert [arr.get(i) for i in range(len(arr))] == ref
    arr.set(0, -1)
    assert arr.get(0) == -1
    try:
        arr.get(len(arr))
        assert False, "ожидался IndexError"
    except IndexError:
        pass

    st, ref = Stack(), []
    for x in [1, 2, 3]:
        st.push(x)
        ref.append(x)
    assert st.peek() == ref[-1]
    while ref:
        assert st.pop() == ref.pop()
    assert len(st) == 0

    dq, ref = Deque(), collections.deque()
    dq.push_back(1); ref.append(1)
    dq.push_front(0); ref.appendleft(0)
    dq.push_back(2); ref.append(2)
    assert dq.pop_front() == ref.popleft() == 0
    assert dq.pop_back() == ref.pop() == 2
    assert dq.pop_front() == ref.popleft() == 1
    assert len(dq) == len(ref) == 0
    try:
        dq.pop_front()
        assert False, "ожидался IndexError"
    except IndexError:
        pass
    print("self_check: OK")

# ---------------------------------------------------------------------------
# 5. Замеры
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5

def bench(fn, *args) -> float:
    fn(*args)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def appends_dynamic_array(n: int) -> None:
    arr = DynamicArray()
    for i in range(n):
        arr.append(i)

def inserts_front_list(n: int) -> None:
    a: list[int] = []
    for i in range(n):
        a.insert(0, i)

def inserts_front_deque(n: int) -> None:
    d: collections.deque = collections.deque()
    for i in range(n):
        d.appendleft(i)

def inserts_front_my_deque(n: int) -> None:
    d = Deque()
    for i in range(n):
        d.push_front(i)

def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    _ = rng.random()
    
    print("\nСредняя стоимость append (DynamicArray), демонстрация амортизированной O(1):")
    amortized_times = []
    for n in SIZES:
        t = bench(appends_dynamic_array, n)
        t_per_op = t / n
        amortized_times.append(t_per_op)
        print(f"  n={n:>7}  всего t={t:.6f} c  на операцию t/n={t_per_op:.3e} c")
        
    print("\nВставка в начало: list.insert(0, x) против deque.appendleft и MyDeque.push_front:")
    for n in SIZES:
        if n > 30_000:
            continue
        t_list = bench(inserts_front_list, n)
        t_deque = bench(inserts_front_deque, n)
        t_my = bench(inserts_front_my_deque, n)
        print(f"  n={n:>7}  list={t_list:.6f} c  deque={t_deque:.6f} c  my_deque={t_my:.6f} c")
        
    if HAS_MATPLOTLIB:
        plt.figure(figsize=(8, 5))
        plt.plot(SIZES, amortized_times, marker='o', color='b')
        plt.title('Амортизированная стоимость append (t/n)')
        plt.xlabel('n (количество операций)')
        plt.ylabel('Время на одну операцию (сек)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('amortized_append.png', dpi=150)
        print("\n✅ График успешно сохранен в файл 'amortized_append.png'")
    else:
        print("\n⚠️ Библиотека matplotlib не установлена. График не построен.")
        print("Установите её командой: pip install matplotlib")

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