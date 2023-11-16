from dataclasses import dataclass
from itertools import product
from typing import Iterator, Type


@dataclass(frozen=True)
class InvalidGridRange:
    index: int
    def bbox(self) -> tuple[int, int, int, int]:
        raise NotImplementedError()

@dataclass(frozen=True)
class InvalidGridRow(InvalidGridRange):
    def bbox(self) -> tuple[int, int, int, int]:
        return 0, self.index, 9, 1

@dataclass(frozen=True)
class InvalidGridCol(InvalidGridRange):
    def bbox(self) -> tuple[int, int, int, int]:
        return self.index, 0, 1, 9
    
@dataclass(frozen=True)
class InvalidGridBox(InvalidGridRange):
    def bbox(self) -> tuple[int, int, int, int]:
        return self.index%3*3, self.index//3*3, 3, 3


class SudokuState:
    def __init__(self, grid: list[list[int]]) -> None:
        self._fixed_grid = grid
        self._grid = [x[::] for x in grid]

        self._is_solved = False
        self._invalid_ranges = set[InvalidGridRange]()
        self._invalid_cells = set[tuple[int, int]]()
        self._user_hints = [[set[int]() for _ in range(9)]
                            for _ in range(9)]
    
    def reset(self) -> None:
        self._grid = [x[::] for x in self._fixed_grid]
        self._is_solved = False
        self._invalid_ranges.clear()
        self._invalid_cells.clear()
        for y, x in product(range(3), repeat=2):
            self._user_hints[y][x].clear()
    

    @property
    def is_solved(self) -> bool:
        return self._is_solved
    
    def iter_invalid_ranges(self) -> Iterator[tuple[int, int, int, int]]:
        return map(lambda x: x.bbox(), self._invalid_ranges)
    
    def is_fixed(self, x: int, y: int) -> bool:
        return self._fixed_grid[y][x] != 0
    
    def is_invalid(self, x: int, y: int) -> bool:
        return (x, y) in self._invalid_cells
    
    
    def get_value(self, x: int, y: int) -> int:
        return self._grid[y][x]
    
    def set_value(self, x: int, y: int, value: int) -> None:
        if not self.is_fixed(x, y):
            self._grid[y][x] = value
            self._user_hints[y][x].clear()
            if value != 0:
                self._fix_user_hints(x, y, value)
            self._check()

    
    def get_user_hints(self, x: int, y: int) -> list[int]:
        return sorted(self._user_hints[y][x])
    
    def toggle_user_hints(self, x: int, y: int, value: int) -> None:
        if not self.is_fixed(x, y) and self.get_value(x, y) == 0:
            hints = self._user_hints[y][x]
            (hints.add, hints.remove)[value in hints](value)

    
    def _fix_user_hints(self, x: int, y: int, value: int) -> None:
        bx, by = x//3*3, y//3*3
        for i in range(9):
            self._user_hints[y][i].discard(value)
            self._user_hints[i][x].discard(value)
            self._user_hints[by+i//3][bx+i%3].discard(value)
    
    def _check(self) -> None:
        self._is_solved = True
        self._invalid_ranges.clear()
        self._invalid_cells.clear()

        for i in range(9):
            self._check_any(i, self._get_row_iter(i), InvalidGridRow)
            self._check_any(i, self._get_col_iter(i), InvalidGridCol)
            self._check_any(i, self._get_box_iter(i), InvalidGridBox)
    
    def _check_any(self,
                   index: int,
                   data: Iterator[tuple[int, int, int]],
                   range_type: Type[InvalidGridRange]) -> None:
        indices = [None]*9
        for x, y, val in data:
            if val == 0:
                self._is_solved = False
                continue
            if indices[val-1] is None:
                indices[val-1] = (x, y)
            else:
                self._is_solved =  False
                self._invalid_cells.add(indices[val-1])
                self._invalid_cells.add((x, y))
                self._invalid_ranges.add(range_type(index))
    
    
    def _get_row_iter(self, y: int):
        for x in range(9):
            yield x, y, self.get_value(x, y)
    
    def _get_col_iter(self, x: int):
        for y in range(9):
            yield x, y, self.get_value(x, y)
    
    def _get_box_iter(self, b: int):
        sx, sy = b%3*3, b//3*3
        for y, x in product(range(sy, sy+3), range(sx, sx+3)):
            yield x, y, self.get_value(x, y)
