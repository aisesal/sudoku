import tkinter as tk
import tkinter.simpledialog

from sudoku_generator import RandomSudokuGenerator
from sudoku_widget import SudokuWidget

ABOUT_MESSAGE = """Use mouse to select a cell.
"Spacebar" key changes between fill in and hint mode.
To put a number in press keys 1 to 9.
"Delete" key removes a numbers from cell.
"""

class SettingsDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, value):
        self.value = value
        self._value = tk.IntVar(value=value)
        super().__init__(parent, 'Settings')
    
    def body(self, frame):
        tk.Label(frame, text='How many empty cells').pack()
        tk.Scale(
            frame, from_=1, to_=80,
            orient='horizontal', variable=self._value
        ).pack()
    
    def apply(self):
        self.value = self._value.get()

class MainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.generator = RandomSudokuGenerator()
        self.num_remove = 45
        self.init_ui()
    
    def init_ui(self):
        self.master.title('Sudoku')

        self.sudoku_widget = SudokuWidget(self)
        self.sudoku_widget.set_state(self.generator(self.num_remove))
        self.sudoku_widget.pack(fill='both')
        self.sudoku_widget.bind('<<OnHintModeChange>>', self.on_mode_change)

        frame = tk.Frame(self)
        left = tk.Frame(frame)
        right = tk.Frame(frame)

        tk.Button(
            left, text='New Game', command=self.new_game
        ).pack(side='left')
        tk.Button(
            left, text='Reset Grid', command=self.reset_grid
        ).pack(side='left')
        tk.Button(
            left, text='Settings', command=self.show_settings
        ).pack(side='left')
        tk.Button(
            left, text='About', command=self.show_about
        ).pack(side='left')

        self.mode_lbl = tk.StringVar(value='Current mode: Fill')
        tk.Label(
            right, textvariable=self.mode_lbl
        ).pack(side='right', padx=10)

        left.pack(side='left', padx=10)
        right.pack(side='right', padx=10)
        frame.pack(fill='x')
        self.pack()
    
    def new_game(self):
        self.sudoku_widget.set_state(self.generator(self.num_remove))
    
    def reset_grid(self):
        self.sudoku_widget.reset()
    
    def show_settings(self):
        dialog = SettingsDialog(self, self.num_remove)
        self.num_remove = dialog.value

    def show_about(self):
        tk.messagebox.showinfo('About', ABOUT_MESSAGE)

    def on_mode_change(self, event):
        mode = 'Hint' if self.sudoku_widget.is_hint_mode() else 'Fill'
        self.mode_lbl.set('Current mode:' + mode)

def main():
    root = tk.Tk()
    root.resizable(False, False)
    window = MainWindow(root)
    window.mainloop()

if __name__ == '__main__':
    main()
