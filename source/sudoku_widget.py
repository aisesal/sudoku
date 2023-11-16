import tkinter as tk
from itertools import product

from sudoku_state import SudokuState


class SudokuWidget(tk.Frame):
    _MARGIN = 10
    _CELL_SIZE = 70
    _WIDGET_SIZE = _MARGIN*2 + _CELL_SIZE*9

    _USER_HINTS_OFFSETS = (
        (10, 17), (35, 17), (60, 17),
        (10, 37), (35, 37), (60, 37),
        (10, 57), (35, 57), (60, 57))
    
    _USER_HINTS_FONT = ('Courier', '12')
    _NUMBERS_FONT = ('Courier', '24')
    _VICTORY_FONT = ('Courier', '48', 'bold')

    _SELECTION_COLOR = ('aqua', 'lime')
    _INVALID_REGION_COLOR = 'gray'

    def __init__(self, parent) -> None:
        super().__init__(parent, borderwidth=0, highlightthickness=0)

        canvas = tk.Canvas(
            self, width=self._WIDGET_SIZE, height=self._WIDGET_SIZE,
            borderwidth=0, highlightthickness=0)
        canvas.pack(fill='both')
        canvas.bind('<Button-1>', self._on_click)
        canvas.bind('<Key>', self._on_key)
        canvas.focus_set()

        hint_mode = tk.BooleanVar(self, False)
        hint_mode.trace_add('write', self._on_hint_mode_change)

        self._canvas = canvas
        self._hint_mode = hint_mode
        self._state: SudokuState = None
        self._sel_x = 4
        self._sel_y = 4
    
    def is_hint_mode(self) -> bool:
        return self._hint_mode.get()
    
    def set_state(self, state: SudokuState):
        self._state = state
        self._draw()
    
    def reset(self):
        self._state.reset()
        self._draw()
        

    def _on_hint_mode_change(self, *args):
        self.event_generate('<<OnHintModeChange>>')
        self._draw()

    def _on_click(self, event):
        if self._state.is_solved:
            return
        x, y = event.x, event.y
        if not (self._MARGIN < x < self._WIDGET_SIZE-self._MARGIN and
                self._MARGIN < y < self._WIDGET_SIZE-self._MARGIN):
            return
        
        self._canvas.focus_set()
        self._sel_x = (x-self._MARGIN)//self._CELL_SIZE
        self._sel_y = (y-self._MARGIN)//self._CELL_SIZE
        self._draw()

    def _on_key(self, event):
        if self._state.is_solved:
            return
        if event.char == ' ':
            self._hint_mode.set(not self._hint_mode.get())
        elif event.keysym == 'Delete':
            self._state.set_value(self._sel_x, self._sel_y, 0)
        elif event.char in '123456789':
            value = int(event.char)
            if self._hint_mode.get():
                self._state.toggle_user_hints(self._sel_x, self._sel_y, value)
            else:
                if self._state.get_value(self._sel_x, self._sel_y) == value:
                    value = 0
                self._state.set_value(self._sel_x, self._sel_y, value)
        else:
            return
        self._draw()

    def _draw(self):
        self._canvas.delete('all')
        self._draw_invalid_regions()
        self._draw_selection()
        self._draw_numbers()
        self._draw_user_hints()
        self._draw_grid_lines()
        self._draw_victory()
    
    def _draw_invalid_regions(self):
        for x, y, w, h in self._state.iter_invalid_ranges():
            self._draw_rectangle(x, y, w, h, self._INVALID_REGION_COLOR)

    def _draw_selection(self):
        self._draw_rectangle(
            self._sel_x, self._sel_y, 1, 1,
            self._SELECTION_COLOR[self._hint_mode.get()])

    def _draw_numbers(self):
        for y, x in product(range(9), repeat=2):
            value = self._state.get_value(x, y)
            if value == 0:
                continue

            color = 'red' if self._state.is_invalid(x, y) else 'black'
            font = self._NUMBERS_FONT
            if self._state.is_fixed(x, y):
                font = font + ('bold', )
            
            self._canvas.create_text(
                self._CELL_SIZE*(x+0.5) + self._MARGIN,
                self._CELL_SIZE*(y+0.5) + self._MARGIN + 5,
                text=str(value), fill=color, font=font)

    def _draw_user_hints(self):
        for y, x in product(range(9), repeat=2):
            sx = self._CELL_SIZE*x + self._MARGIN
            sy = self._CELL_SIZE*y + self._MARGIN
            for n in self._state.get_user_hints(x, y):
                off = self._USER_HINTS_OFFSETS[n-1]
                self._canvas.create_text(
                    sx+off[0], sy+off[1],
                    text=str(n), fill='black',
                    font=self._USER_HINTS_FONT)

    def _draw_grid_lines(self):
        x = y0 = self._MARGIN
        y1 = self._WIDGET_SIZE - self._MARGIN
        for width in (2, 1, 1, 2, 1, 1, 2, 1, 1, 2):
            self._canvas.create_line(x, y0, x, y1, fill='black', width=width)
            self._canvas.create_line(y0, x, y1, x, fill='black', width=width)
            x += self._CELL_SIZE
    
    def _draw_rectangle(self, x: int, y: int, w: int, h: int, color: str):
        x0 = self._CELL_SIZE*x + self._MARGIN
        y0 = self._CELL_SIZE*y + self._MARGIN
        x1 = self._CELL_SIZE*w + x0
        y1 = self._CELL_SIZE*h + y0
        self._canvas.create_rectangle(x0, y0, x1, y1, fill=color)
    
    def _draw_victory(self):
        if self._state.is_solved:
            self._canvas.create_text(
                self._WIDGET_SIZE//2, self._WIDGET_SIZE//2,
                text='Victory', fill='yellow', font=self._VICTORY_FONT)
