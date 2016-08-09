#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

# Генерация случайной матрицы
X = np.random.normal(loc=1, scale=10, size=(5, 5))

print X

# Нормировка матрицы по столбцам
m = np.mean(X, axis=0)
print m
std = np.std(X, axis=0)
print std
X_norm = ((X - m)  / std)
print X_norm

# Выведите для заданной матрицы номера строк, сумма элементов в которых превосходит 10.
Z = np.array([[4, 5, 0], 
             [1, 9, 3],              
             [5, 1, 1],
             [3, 3, 3], 
             [9, 9, 9], 
             [4, 7, 1]])

r = np.sum(Z, axis=1)
print np.nonzero(r > 10)

# Сгенерируйте две единичные матрицы (т.е. с единицами на диагонали) размера 3x3. 
# Соедините две матрицы в одну размера 6x3.
A = np.eye(3)
B = np.eye(3)
AB = np.vstack((A, B))
print AB