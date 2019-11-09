from BaseAI import BaseAI
import time
import sys
import math

inf = 1000000000000
timeLimit = 0.112
vecIndex = (UP, DOWN, LEFT, RIGHT) = range(4)
directionVectors = (UP_VEC, DOWN_VEC, LEFT_VEC, RIGHT_VEC) = ((-1, 0), (1, 0), (0, -1), (0, 1))
wightPows = [[0, 1, 2, 3],
             [7, 6, 5, 4],
             [8, 9, 10, 11],
             [15, 14, 13, 12]]

logBase = 2

class PlayerAI(BaseAI):
    def __init__(self):
        self.startTime = None
        sys.setrecursionlimit(10000)
        self.moves = 0
        self.lastMove = None

    def getMove(self, grid):
        self.startTime = time.clock()
        maxUtility = -inf
        nextMove = None
        moves = grid.getAvailableMoves()
        a = -inf
        b = inf
        for i in moves:
            child = grid.clone()
            child.move(i)
            util = self.minimaxab(child, a, b, False)
            if util > maxUtility:
                maxUtility = util
                nextMove = i
            a = max(a, maxUtility)
            if a >= b:
                break
        return nextMove

    def minimaxab(self, state, a, b, isMax):
        if self.terminal(state, isMax):
            return self.utility(state)
        elif isMax:
            bestUtil = a
            for child in self.getChildren(state, isMax):
                bestUtil = max(bestUtil, self.minimaxab(child, bestUtil, b, False))
                if bestUtil >= b:
                    break
            return bestUtil
        else:
            bestUtil = b
            children = self.getChildren(state, isMax)
            for child in children:
                bestUtil = min(bestUtil, self.minimaxab(child, a, bestUtil, True))
                if a >= bestUtil:
                    break
            return bestUtil

    def utility(self, state):
        rows = [0, 0]
        cols = [0, 0]
        smoothness = 0
        merges = 0
        empty = len(state.getAvailableCells()) * math.log(state.getMaxTile(), 2)
        for x in range(4):
            c = 0
            n = c+1
            while n < 4:
                while n < 4 and state.canInsert((x,n)):
                    n += 1
                if n >= 4: n -= 1
                curVal = state.getCellValue((x, c))
                if curVal:
                    curVal = math.log(curVal, logBase)
                nextVal = state.getCellValue((x, n))
                if nextVal:
                    nextVal = math.log(nextVal, logBase)
                smoothness -= math.fabs(curVal - nextVal)
                if curVal == nextVal: merges += 1
                elif curVal > nextVal: cols[0] += nextVal - curVal
                elif nextVal > curVal: cols[1] += curVal - nextVal
                c = n
                n += 1

        for y in range(4):
            c = 0
            n = c+1
            while n < 4:
                while n < 4 and state.canInsert((n, y)):
                    n += 1
                if n >= 4: n -= 1
                curVal = state.getCellValue((c, y))
                if curVal:
                    curVal = math.log(curVal, logBase)
                nextVal = state.getCellValue((n, y))
                if nextVal:
                    nextVal = math.log(nextVal, logBase)
                smoothness -= math.fabs(curVal - nextVal)
                if curVal == nextVal: merges += 1
                elif curVal > nextVal: rows[0] += nextVal - curVal
                elif nextVal > curVal: rows[1] += curVal - nextVal

                c = n
                n += 1
        heur = (max(rows) + max(cols)) * 6 + (smoothness * 0.2) + merges * 2 + empty
        return heur

    def terminal(self, state, isMax):
        if time.clock() - self.startTime > timeLimit: return True
        elif state.getMaxTile() == 2048: return True
        elif isMax and not state.canMove(): return True
        elif not isMax and not state.getAvailableCells(): return True
        else: return False

    def getChildren(self, state, isMax):
        if isMax:
            moves = state.getAvailableMoves()
            children = []
            for move in moves:
                child = state.clone()
                child.move(move)
                children.append(child)
            children.reverse()
            return children
        else:
            children = []
            bestCells = []
            cells = state.getAvailableCells()
            if len(cells) > 4:
                for cell in state.getAvailableCells():
                    bestCells.append((cell, pow(4, wightPows[cell[0]][cell[1]])))
                bestCells = sorted(bestCells, key=lambda tup: tup[1])
                for i in range(min(len(bestCells), 4)):
                    child = state.clone()
                    state.insertTile(bestCells[i][0], 2)
                    children.append(child)
            else:
                for cell in cells:
                    child = state.clone()
                    state.insertTile(cell, 2)
                    children.append(child)

            return children
