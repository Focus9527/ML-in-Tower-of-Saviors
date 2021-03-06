import numpy as np
import time
import sys
import copy

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk


# w = 5
# h = 6


class Tos(object):      # class Tos(tk.TK, object):
    def __init__(self):
        print('Initialize the environment.')
        self.debugMode = False
        self.w, self.h = 5, 6
        self.action_space = ['u', 'd', 'l', 'r', 'e']  # up:0, down:1, left:2, right:3, empty:4(do nothing)
        self.n_actions = len(self.action_space)  # num of actions
        self.last_action = 4  # init = empty
        self.cur_pos = [0, 0]  # init position = (0, 0)
        self.path = []  # record path
        self.element = np.zeros((6, 1), dtype=int)  # record each element number
        self.combo = 0  # total combo
        self.max_combo = 0  # current table can format max combo number
        self.reward = 0  # total reward
        self.build_tos()

    def build_tos(self):
        # build table
        print('Build tos.')
        self.table = [[0 for x in range(self.w)] for y in range(self.h)]

    def reset(self):
        # reset the table (random or select case) and calculate max combo
        print('Reset.')
        # random
        # for i in range(self.h):
        #     for j in range(self.w):
        #         self.table[i][j] = np.random.randint(0, 6)
        # ============================================================
        # case 1
        self.table = [[2, 2, 1, 2, 2],
                      [0, 5, 1, 2, 2],
                      [5, 5, 1, 2, 5],
                      [0, 0, 1, 2, 1],
                      [0, 0, 1, 3, 5],
                      [1, 1, 1, 1, 1]]
        # ============================================================
        # case 2
        # self.table = [[3, 3, 3, 2, 1],
        #               [3, 1, 3, 3, 3],
        #               [3, 5, 1, 5, 5],
        #               [2, 2, 1, 1, 4],
        #               [2, 1, 1, 1, 4],
        #               [2, 2, 2, 1, 4]]

        for i in range(self.h):
            for j in range(self.w):
                self.element[self.table[i][j]] += 1
        # 要在計算同色 > 18 的 case
        self.max_combo = 0
        for i in range(6):
            if self.element[i] >= 27:
                self.max_combo += 1
            elif self.element[i] >= 24:
                self.max_combo += 2
            elif self.element[i] >= 21:
                self.max_combo += 3
            elif self.element[i] >= 18:
                self.max_combo += 4
            else:
                self.max_combo = self.max_combo + int(np.floor(self.element[i]/3))
        print("max_combo :", self.max_combo)

    def step(self, action):
        # move
        print('Step.')
        x, y = self.cur_pos[0], self.cur_pos[1]
        # if action == self.last_action:
        #     print("do not go back.")
        #     return
        if action == 0:  # up
            if self.cur_pos[0] - 1 >= 0:
                self.table[x][y], self.table[x - 1][y] = self.swap(self.table[x][y], self.table[x - 1][y])
                self.cur_pos[0] -= 1
            else:
                print("over the top edge.")
                return
        if action == 1:  # down
            if self.cur_pos[0] + 1 <= self.h - 1:
                self.table[x][y], self.table[x + 1][y] = self.swap(self.table[x][y], self.table[x + 1][y])
                self.cur_pos[0] = self.cur_pos[0] + 1
            else:
                print("over the bot edge.")
                return
        if action == 2:  # left
            if self.cur_pos[1] - 1 >= 0:
                self.table[x][y], self.table[x][y - 1] = self.swap(self.table[x][y], self.table[x][y - 1])
                self.cur_pos[1] -= 1
            else:
                print("over the left edge.")
                return
        if action == 3:  # right
            if self.cur_pos[1] + 1 <= self.w - 1:
                self.table[x][y], self.table[x][y + 1] = self.swap(self.table[x][y], self.table[x][y + 1])
                self.cur_pos[1] += 1
            else:
                print("over the right edge.")
                return
        if action == 4:  # do nothing
            print("didn't move.")
            self.table, self.combo = self.run(self.table)
            return

        self.table, self.combo = self.run(self.table)

    def render(self):
        print('Render.')
        for i in self.table:
            print(i)
        print("current combo:", self.combo)
        # do something

    def swap(self, a, b):
        tmp = a
        a = b
        b = tmp
        return a, b

    def run(self, table):
        w, h = self.w, self.h
        tmpTable = [[0 for x in range(self.w)] for y in range(self.h)]  # for DFS
        localTable = [[(y * 5 + x + 100) for x in range(self.w)] for y in range(self.h)]  # DFS marked
        direction = [[0, 1], [-1, 0], [0, -1], [1, 0]]  # y,x for DFS direction
        combo = 0

        # function
        def DFS(table, targetValue, nowY, nowX):
            tmpTable[nowY][nowX] = -1
            localTable[nowY][nowX] = -1
            for i in range(len(direction)):
                newDir = direction[i]  # y,x
                newY = nowY + newDir[0]
                newX = nowX + newDir[1]
                if 0 <= newX < w and 0 <= newY < h:
                    if table[newY][newX] == targetValue and tmpTable[newY][newX] != -1:
                        DFS(table, targetValue, newY, newX)

        def Iscombo(table):
            debugMode = False  # print process message
            # delete row--------------------------------------
            h = len(table)  # update h
            w = len(table[0])  # update w
            if debugMode:
                print(h, w, 'localTable')
                for row in table:
                    print(row)
            tmpTable = [[0 for x in range(w)] for y in range(h)]  # update tmpTable
            for row in range(0, h):
                tmpQ = []
                for col in range(0, w - 1):
                    try:
                        tmp = table[row][col]
                        tmpQ.append(col)
                    except:
                        if debugMode:
                            print("if table[{0}][{1}] == tmp, out of list, break".format(row, col + 1))
                        break

                    try:
                        if table[row][col + 1] == tmp:
                            tmpQ.append(col + 1)
                        else:
                            tmpQ = []
                    except:
                        if debugMode:
                            print("if table[{0}][{1}] == tmp, out of list, break".format(row, col + 1))
                        break

                    if len(tmpQ) >= 3:
                        for idx in tmpQ:
                            tmpTable[row][idx] = -1

            # delete col--------------------------------------
            for col in range(0, w):
                tmpQ = []
                for row in range(0, h - 1):
                    try:
                        tmp = table[row][col]
                        tmpQ.append(row)
                    except:
                        if debugMode:
                            print("tmp = table[{0}][{1}], out of index, continue".format(row, col))
                        continue

                    try:
                        if table[row + 1][col] == tmp:
                            tmpQ.append(row + 1)
                        else:
                            tmpQ = []
                    except:
                        if debugMode:
                            print("table[{0}][{1}] == tmp, out of index, continue".format(row + 1, col))
                        tmpQ = []
                        continue

                    if len(tmpQ) >= 3:
                        for idx in tmpQ:
                            tmpTable[idx][col] = -1
            if debugMode:
                print('delete done')
                print('tmpTable')
                for row in range(0, h):
                    print(tmpTable[row])

            # update new table
            newT = []
            flag = 0
            for row in range(0, h):
                newL = []
                for col in range(0, w):
                    if tmpTable[row][col] == -1:
                        flag = 1
                        continue
                    else:
                        try:
                            newL.append(table[row][col])
                        except:
                            if debugMode:
                                print("newL.append(table[{0}][{1}]), isEmpty".format(row, col))
                while len(newL) < 5:
                    newL.append(row * 5 + len(newL) + 100)
                newT.append(newL)
            if flag:  # update new table
                table = newT

            if debugMode:
                print('table')
                for row in range(0, h):
                    print(table[row])

            if flag:
                if debugMode:
                    print('return 1')
                return 1
            else:
                if debugMode:
                    print('return 0')
                return 0
            if debugMode:
                print('====================================')
                print('done')
                print('====================================')

        def OrganizeTable(table):
            debugMode = False  # print process message
            # delete row--------------------------------------
            h = len(table)  # update h
            w = len(table[0])  # update w
            if debugMode:
                print(h, w)
            tmpTable = [[0 for x in range(w)] for y in range(h)]  # update tmpTable
            for row in range(0, h):
                tmpQ = []
                for col in range(0, w - 1):
                    try:
                        tmp = table[row][col]
                        tmpQ.append(col)
                    except:
                        if debugMode:
                            print("if table[{0}][{1}] == tmp, out of list, break".format(row, col + 1))
                        break

                    try:
                        if table[row][col + 1] == tmp:
                            tmpQ.append(col + 1)
                        else:
                            tmpQ = []
                    except:
                        if debugMode:
                            print("if table[{0}][{1}] == tmp, out of list, break".format(row, col + 1))
                        break

                    if len(tmpQ) >= 3:
                        for idx in tmpQ:
                            tmpTable[row][idx] = -1

            # delete col--------------------------------------
            for col in range(0, w):
                tmpQ = []
                for row in range(0, h - 1):
                    try:
                        tmp = table[row][col]
                        tmpQ.append(row)
                    except:
                        if debugMode:
                            print("tmp = table[{0}][{1}], out of index, continue".format(row, col))
                        continue

                    try:
                        if table[row + 1][col] == tmp:
                            tmpQ.append(row + 1)
                        else:
                            tmpQ = []
                    except:
                        if debugMode:
                            print("table[{0}][{1}] == tmp, out of index, continue".format(row + 1, col))
                        tmpQ = []
                        continue

                    if len(tmpQ) >= 3:
                        for idx in tmpQ:
                            tmpTable[idx][col] = -1

            if debugMode:
                print('delete done')
                print('tmpTable')
                for row in range(0, h):
                    print(tmpTable[row])

            # update new table
            newT = []
            flag = 0
            for row in range(0, h):
                newL = []
                for col in range(0, w):
                    if tmpTable[row][col] == -1:
                        flag = 1
                        continue
                    else:
                        try:
                            newL.append(table[row][col])
                        except:
                            if debugMode:
                                print("newL.append(table[{0}][{1}]), isEmpty".format(row, col))
                while len(newL) < 5:
                    newL.append(row * 5 + len(newL) + 100)
                newT.append(newL)
            if flag:  # update new table
                table = newT

            if debugMode:
                print('table')
                for row in range(0, h):
                    print(table[row])
                print('OrganizeTable')
            return table

            if debugMode:
                print('====================================')
                print('done')
                print('====================================')

        while Iscombo(table.copy()):
            for y in range(0, h):
                for x in range(0, w):
                    if tmpTable[y][x] != -1:
                        DFS(table.copy(), table[y][x], y, x)
                        if self.debugMode:
                            print('localTable ==========================')
                            for i in localTable:
                                print(i)
                            print('combo check ==========================')

                        for row in range(h):
                            for col in range(w):
                                if localTable[row][col] == -1:
                                    localTable[row][col] = table[row][col]
                        if self.debugMode:
                            print('before func')
                            for row in localTable:
                                print(row)
                        combo = combo + Iscombo(localTable.copy())

                        if self.debugMode:
                            print('current combo\t', combo, 'Iscombo\t', Iscombo(localTable.copy()))
                            print('reset localTable==========================')
                        localTable = [[(y * 5 + x + 100) for x in range(w)] for y in range(h)]
            table = OrganizeTable(table.copy())
            tmpTable = [[0 for x in range(w)] for y in range(h)]

            print('loop =============================================\=============================================')
        print('\nOrgTable')
        for i in range(0, h):
            print(table[i])
        print()

        print('Organize table')
        for row in table:
            tmpL = []
            for iteam in row:
                if iteam < 100:
                    tmpL.append(iteam)
            print(tmpL)
        print()

        print(combo, "\tcombo")

        return table, combo


tos = Tos()
tos.reset()
tos.render()
tos.step(4)
tos.render()