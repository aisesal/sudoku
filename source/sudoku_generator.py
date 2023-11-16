from random import sample

from sudoku_state import SudokuState


class RandomSudokuGenerator:
    def __call__(self, remove_cnt: int) -> SudokuState:
        self._grid = [[0]*9 for _ in range(9)]
        self._per_row = [set(range(1, 10)) for _ in range(9)]
        self._per_col = [set(range(1, 10)) for _ in range(9)]
        self._per_box = [set(range(1, 10)) for _ in range(9)]

        for i in range(0, 9, 3):
            self._fill_box(i, i)
        self._fill_rest(3, 0)

        for i in sample(range(81), k=remove_cnt):
            self._grid[i//9][i%9] = 0
        return SudokuState(self._grid)
    
    def _fill_box(self, x: int, y: int) -> None:
        box = sample(range(1, 10), k=9)
        for i in range(3):
            self._grid[y+i][x:x+3] = box[i*3:i*3+3]
            self._per_row[y+i] -= set(box[i*3:i*3+3])
            self._per_col[x+i] -= set(box[i::3])
        self._per_box[y//3*3 + x//3] = set()

    def _fill_rest(self, x: int, y: int) -> bool:
        while True:
            x, y = x%9, y+x//9
            if y == 9:
                return True
            if self._grid[y][x] == 0:
                break
            x += 3
        
        b = y//3*3 + x//3
        avail = self._per_row[y] & self._per_col[x] & self._per_box[b]
        
        for value in sample(sorted(avail), k=len(avail)):
            self._per_row[y].remove(value)
            self._per_col[x].remove(value)
            self._per_box[b].remove(value)
            self._grid[y][x] = value

            if self._fill_rest(x+1, y):
                return True
            
            self._per_row[y].add(value)
            self._per_col[x].add(value)
            self._per_box[b].add(value)
            self._grid[y][x] = 0
        
        return False
