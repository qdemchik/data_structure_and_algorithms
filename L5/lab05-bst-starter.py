#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 5. Бинарное дерево поиска: обходы, вставка и удаление.

Реализация соответствует КИМ-05 и правилам использования генеративного ИИ.
Класс BST спроектирован чистым и переносимым для использования в ДЗ 2.

Запуск: python lab05-bst-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
from collections import deque

# ---------------------------------------------------------------------------
# 1. Бинарное дерево поиска (реализуется вручную, без сторонних библиотек)
# ---------------------------------------------------------------------------

class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""
    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    """Бинарное дерево поиска без дубликатов ключей.

    Инвариант: для каждого узла все ключи левого поддерева меньше key,
    все ключи правого — больше. 
    Ожидаемая сложность операций insert/search/delete: O(h), где h — высота дерева.
    На случайных данных h = O(log n), в худшем случае (вырожденное дерево) h = O(n).
    """

    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Вставка ключа; повторная вставка существующего ключа игнорируется."""
        if self.root is None:
            self.root = Node(key)
            return

        curr = self.root
        while True:
            if key < curr.key:
                if curr.left is None:
                    curr.left = Node(key)
                    return
                curr = curr.left
            elif key > curr.key:
                if curr.right is None:
                    curr.right = Node(key)
                    return
                curr = curr.right
            else:
                return  # Ключ уже существует, игнорируем

    def search(self, key: int) -> bool:
        """Возвращает True, если ключ есть в дереве."""
        curr = self.root
        while curr is not None:
            if key == curr.key:
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False

    def delete(self, key: int) -> None:
        """Удаление ключа. Обрабатывает все три случая через рекурсивный подход."""
        def _delete(node: Node | None, k: int) -> Node | None:
            if node is None:
                return None

            if k < node.key:
                node.left = _delete(node.left, k)
            elif k > node.key:
                node.right = _delete(node.right, k)
            else:
                # Случай 1 и 2: узел является листом или имеет одного ребёнка
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left

                # Случай 3: узел имеет двух детей
                # Находим преемника (минимум в правом поддереве)
                succ = node.right
                while succ.left is not None:
                    succ = succ.left

                # Заменяем ключ текущего узла на ключ преемника
                node.key = succ.key
                # Рекурсивно удаляем преемника из правого поддерева
                node.right = _delete(node.right, succ.key)

            return node

        self.root = _delete(self.root, key)

    # -- Обходы --------------------------------------------------------------

    def in_order(self) -> list[int]:
        """Симметричный обход (лево — узел — право): рекурсивно."""
        res = []
        def _in_order(node: Node | None):
            if node is None:
                return
            _in_order(node.left)
            res.append(node.key)
            _in_order(node.right)
        _in_order(self.root)
        return res

    def pre_order(self) -> list[int]:
        """Прямой обход (узел — лево — право): рекурсивно."""
        res = []
        def _pre_order(node: Node | None):
            if node is None:
                return
            res.append(node.key)
            _pre_order(node.left)
            _pre_order(node.right)
        _pre_order(self.root)
        return res

    def post_order(self) -> list[int]:
        """Обратный обход (лево — право — узел): рекурсивно."""
        res = []
        def _post_order(node: Node | None):
            if node is None:
                return
            _post_order(node.left)
            _post_order(node.right)
            res.append(node.key)
        _post_order(self.root)
        return res

    def level_order(self) -> list[int]:
        """Обход в ширину по уровням: итеративно через очередь (deque)."""
        if self.root is None:
            return []
        res = []
        q = deque([self.root])
        while q:
            node = q.popleft()
            res.append(node.key)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        return res

    # -- Характеристики дерева ----------------------------------------------

    def height(self) -> int:
        """Высота дерева: число рёбер на самом длинном пути от корня.
        Пустое дерево имеет высоту -1, дерево из одного узла — 0.
        """
        def _height(node: Node | None) -> int:
            if node is None:
                return -1
            return 1 + max(_height(node.left), _height(node.right))
        return _height(self.root)

    def size(self) -> int:
        """Число узлов в дереве."""
        def _size(node: Node | None) -> int:
            if node is None:
                return 0
            return 1 + _size(node.left) + _size(node.right)
        return _size(self.root)


# ---------------------------------------------------------------------------
# 2. Верификация: инвариант BST и сверка с эталоном (docs/ai-verification.md)
# ---------------------------------------------------------------------------

class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""

def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)

def build(keys) -> BST:
    """Дерево, полученное последовательной вставкой keys в пустое BST."""
    tree = BST()
    for k in keys:
        tree.insert(k)
    return tree

def expect_search(tree: BST, key: int, present: bool, where: str) -> None:
    """search(key) обязан вернуть именно True или False."""
    got = tree.search(key)
    expect(got is present, f"{where}: search({key}) вернул {got!r}, ожидалось {present}")

TRAVERSALS = ("in_order", "pre_order", "post_order", "level_order")

KNOWN_TREES = {
    (4, 2, 6, 1, 3, 5, 7): {
        "in_order": [1, 2, 3, 4, 5, 6, 7],
        "pre_order": [4, 2, 1, 3, 6, 5, 7],
        "post_order": [1, 3, 2, 5, 7, 6, 4],
        "level_order": [4, 2, 6, 1, 3, 5, 7],
        "height": 2,
        "size": 7,
    },
    (8, 3, 10, 1, 6, 14, 4, 7, 13): {
        "in_order": [1, 3, 4, 6, 7, 8, 10, 13, 14],
        "pre_order": [8, 3, 1, 6, 4, 7, 10, 14, 13],
        "post_order": [1, 4, 7, 6, 3, 13, 14, 10, 8],
        "level_order": [8, 3, 10, 1, 6, 14, 4, 7, 13],
        "height": 3,
        "size": 9,
    },
}

TWO_CHILDREN_CASES = [
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 3, [8, 4, 1, 6, 7, 10, 14, 13], [8, 1, 6, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 6, [8, 3, 1, 7, 4, 10, 14, 13], [8, 3, 1, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 8, [10, 3, 1, 6, 4, 7, 14, 13], [7, 3, 1, 6, 4, 10, 14, 13]),
    ((50, 30, 70, 60, 80, 65), 50, [60, 30, 70, 65, 80], [30, 70, 60, 65, 80]),
    ((50, 30, 70, 60, 80, 65), 70, [50, 30, 80, 60, 65], [50, 30, 65, 60, 80]),
]

def check_insert_search() -> None:
    tree = BST()
    expect_search(tree, 1, False, "пустое дерево")
    tree.insert(5)
    expect_search(tree, 5, True, "дерево из одного узла 5")
    expect_search(tree, 4, False, "дерево из одного узла 5")
    keys = [5, 2, 8, 1, 3, 9, 7]
    tree = build(keys)
    for k in range(11):
        expect_search(tree, k, k in keys, f"дерево из вставок {keys}")
    got = tree.in_order()
    expect(got == sorted(keys), f"in_order() после вставок {keys}: {got}, ожидалось {sorted(keys)}")
    tree.insert(5)
    tree.insert(1)
    got = tree.in_order()
    expect(got == sorted(keys), f"повторная вставка 5 и 1 изменила дерево: in_order() = {got}")

def check_traversals() -> None:
    empty = BST()
    for name in TRAVERSALS:
        got = getattr(empty, name)()
        expect(got == [], f"{name}() пустого дерева: {got}, ожидалось []")
    for keys, answer in KNOWN_TREES.items():
        tree = build(keys)
        for name in TRAVERSALS:
            got = getattr(tree, name)()
            expect(got == answer[name], f"{name}() дерева из вставок {list(keys)}: {got}, ожидалось {answer[name]}")

def check_height_size() -> None:
    cases = [("пустое дерево", (), -1, 0), ("один узел 5", (5,), 0, 1)]
    cases += [(f"дерево из вставок {list(keys)}", keys, answer["height"], answer["size"])
              for keys, answer in KNOWN_TREES.items()]
    cases.append(("ключи 1, 2, …, 50 по возрастанию (цепочка)", tuple(range(1, 51)), 49, 50))
    for where, keys, height, size in cases:
        tree = build(keys)
        got_h, got_s = tree.height(), tree.size()
        expect(got_h == height, f"{where}: height() = {got_h}, ожидалось {height}")
        expect(got_s == size, f"{where}: size() = {got_s}, ожидалось {size}")

def check_delete() -> None:
    tree = BST()
    tree.delete(1)
    got = tree.in_order()
    expect(got == [], f"delete(1) из пустого дерева: in_order() = {got}")
    keys = [5, 2, 8, 1, 3]
    tree = build(keys)
    left = set(keys)
    steps = [(1, "лист 1"), (2, "узел 2 с одним ребёнком"), (5, "корень 5 с двумя детьми"),
             (4, "отсутствующий ключ 4"), (3, "ключ 3"), (8, "последний ключ 8")]
    for k, what in steps:
        tree.delete(k)
        left.discard(k)
        where = f"дерево из вставок {keys}, удаление: {what}"
        got = tree.in_order()
        expect(got == sorted(left), f"{where}: in_order() = {got}, ожидалось {sorted(left)}")
        expect_search(tree, k, False, where)
        for rest in left:
            expect_search(tree, rest, True, where)
    got_h, got_s = tree.height(), tree.size()
    expect(got_h == -1 and got_s == 0, f"после удаления всех ключей: height() = {got_h}, size() = {got_s}, ожидалось -1 и 0")

def check_delete_two_children() -> None:
    for keys, k, by_successor, by_predecessor in TWO_CHILDREN_CASES:
        tree = build(keys)
        tree.delete(k)
        where = f"delete({k}) в дереве из вставок {list(keys)}"
        rest = sorted(set(keys) - {k})
        got = tree.in_order()
        expect(got == rest, f"{where}: in_order() = {got}, ожидалось {rest}")
        got = tree.pre_order()
        expect(got in (by_successor, by_predecessor),
               f"{where}: pre_order() = {got}; при замене преемником ожидалось {by_successor}, "
               f"предшественником — {by_predecessor}")

def check_against_reference() -> None:
    rng = random.Random(0)
    for run in range(1, 101):
        tree = BST()
        etalon: set[int] = set()
        for step in range(1, rng.randint(1, 80) + 1):
            k = rng.randint(-30, 30)
            if rng.random() < 0.6:
                tree.insert(k)
                etalon.add(k)
                op = f"insert({k})"
            else:
                tree.delete(k)
                etalon.discard(k)
                op = f"delete({k})"
            got = tree.in_order()
            expect(got == sorted(etalon), f"прогон {run}, команда №{step} {op}: "
                   f"in_order() = {got}, эталон {sorted(etalon)}")
        where = f"прогон {run}, итоговое дерево"
        for k in range(-30, 31):
            expect_search(tree, k, k in etalon, where)
        n = len(etalon)
        got = tree.size()
        expect(got == n, f"{where}: size() = {got}, эталон {n}")
        for name in TRAVERSALS[1:]:
            got = getattr(tree, name)()
            expect(sorted(got) == sorted(etalon), f"{where}: {name}() содержит не те ключи: {got}")
        got = tree.height()
        low, high = (-1, -1) if n == 0 else (n.bit_length() - 1, n - 1)
        expect(low <= got <= high, f"{where}: height() = {got} при {n} узлах, возможно от {low} до {high}")

def self_check() -> None:
    checks = (
        ("вставка и поиск", check_insert_search),
        ("обходы", check_traversals),
        ("высота и размер", check_height_size),
        ("удаление", check_delete),
        ("удаление узла с двумя детьми", check_delete_two_children),
        ("сверка с эталоном set/sorted", check_against_reference),
    )
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f" {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f" {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:
            print(f" {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f" {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")

# ---------------------------------------------------------------------------
# 3. Бенчмарк: поиск в BST против поиска в списке (docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
QUERIES = 1_000

def bench(fn) -> float:
    """Медиана времени выполнения fn() по REPEATS запускам, с прогревом."""
    fn()
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def run_benchmarks(seed: int) -> None:
    """Сравнение времени QUERIES поисков в BST и в списке (оператор in)."""
    rng = random.Random(seed)
    print(f"\n{'n':>8} {'h(BST)':>7} {'t_bst, c':>10} {'t_list, c':>10}")
    
    bench_data = {'n': [], 'h_bst': [], 't_bst': [], 't_list': []}
    
    for n in SIZES:
        keys = rng.sample(range(10 * n), n)
        queries = [rng.randint(0, 10 * n) for _ in range(QUERIES)]
        tree = BST()
        for k in keys:
            tree.insert(k)

        def search_bst() -> None:
            for q in queries:
                tree.search(q)

        def search_list() -> None:
            for q in queries:
                q in keys

        t_bst = bench(search_bst)
        t_list = bench(search_list)
        h = tree.height()
        
        bench_data['n'].append(n)
        bench_data['h_bst'].append(h)
        bench_data['t_bst'].append(t_bst)
        bench_data['t_list'].append(t_list)
        
        print(f"{n:>8} {h:>7} {t_bst:>10.6f} {t_list:>10.6f}")

    # Построение log-log графика для отчёта (выполняется, если установлен matplotlib)
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.loglog(bench_data['n'], bench_data['t_bst'], marker='o', label='BST Search (O(log n))')
        plt.loglog(bench_data['n'], bench_data['t_list'], marker='s', label='List Search (O(n))')
        plt.title("Сравнение времени поиска: BST vs Список (логарифмическая шкала)")
        plt.xlabel("Размер данных n (log scale)")
        plt.ylabel("Время выполнения, с (log scale)")
        plt.legend()
        plt.grid(True, which="both", ls="--")
        plt.savefig("bst_vs_list_benchmark.png")
        plt.close()
        print("\n[OK] График успешно сохранён в файл 'bst_vs_list_benchmark.png'")
    except ImportError:
        print("\n[Предупреждение] matplotlib не установлен. График не построен (установите: pip install matplotlib).")

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