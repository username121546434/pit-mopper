from tkinter import *
from squares import Square, PickleSquare
import random
from functools import partial
from tkinter import messagebox


class ButtonGrid:
    def __init__(self, grid_size: tuple[int, int], window: Tk | Toplevel, grid: list[list[PickleSquare]] | None = None, dark_mode:bool = False, num_mines:int = -1):
        self.grid_size = grid_size
        self.root = window
        self.dark_mode = dark_mode
        if num_mines == 0 or num_mines == 1:
            messagebox.showerror('Mines are too low', "You can't have 0 or 1 mine on a game")
            window.destroy()
            return None
        self.num_mines = num_mines
        if grid == None:
            self.grid = self.button_grid()
        else:
            self.grid = self.setup_grid(grid)

    def button_grid(self) -> list[list[Square]]:
        Grid.rowconfigure(self.root, 2, weight=1)
        Grid.columnconfigure(self.root, 1, weight=1)
        grid = []
        blank = "  " * 3
        button_pressed = Variable(self.root, None)
        # Create & Configure frame
        frame = Frame(self.root)
        frame.grid(row=2, column=1, sticky=N+S+E+W)
        for row_index in range(self.grid_size[0]):
            Grid.rowconfigure(frame, row_index, weight=1)
            row = []
            for col_index in range(self.grid_size[1]):
                Grid.columnconfigure(frame, col_index, weight=1)
                # create a button inside frame
                btn = Square(master=frame, text=blank)
                btn.grid(row=row_index, column=col_index, sticky=N+S+E+W)
                if self.dark_mode:
                    btn.switch_theme()
                # Store row and column indices as a Button attribute
                btn.position = (row_index, col_index)
                btn.config(command=partial(button_pressed.set, btn.position))
                row.append(btn)
            grid.append(row)


        self.grid = grid
        self.root.wait_variable(button_pressed)
        coordinates = button_pressed.get()

        corners = (
            (0, 0),
            (self.grid_size[0] - 1, self.grid_size[1] - 1),
            (self.grid_size[0] - 1, 0),
            (0, self.grid_size[1] - 1)
        )
        if self.num_mines != -1:
            mines_so_far = 0
            while mines_so_far < self.num_mines:
                for row in grid:
                    row_num = grid.index(row)
                    for square in row:
                        col_num = row.index(square)
                        dice = random.randint(1, 9)
                        coor = (row_num, col_num)
                        if dice == 2 and square not in self.around_square(*coordinates) and coor not in corners and coor != coordinates and mines_so_far < self.num_mines:
                            mines_so_far += 1
                            square.category = 'mine'
        else:
            for row in grid:
                row_num = grid.index(row)
                for square in row:
                    col_num = row.index(square)
                    dice = random.randint(1, 9)
                    coor = (row_num, col_num)
                    if dice == 2 and square not in self.around_square(*coordinates) and coor not in corners and coor != coordinates:
                        square.category = 'mine'

        self.grid = grid

        for row in grid:
            row_num = grid.index(row)
            for square in row:
                if square.category != 'mine':
                    num_mines = 0
                    col_num = row.index(square)
                    around_squares = self.around_square(row_num, col_num)
                    for around_square in around_squares:
                        if around_square.category == 'mine':
                            num_mines += 1
                    if num_mines == 0:
                        square.category == 'blank'
                    else:
                        square.num = num_mines

        return grid
    
    def setup_grid(self, grid: list[list[PickleSquare]]) -> list[list[Square]]:
        Grid.rowconfigure(self.root, 1, weight=1)
        Grid.columnconfigure(self.root, 1, weight=1)
        new_grid = []
        # Create & Configure frame
        frame = Frame(self.root)
        frame.grid(row=1, column=1, sticky=N+S+E+W)
        for row_index in range(self.grid_size[0]):
            Grid.rowconfigure(frame, row_index, weight=1)
            row = grid[row_index]
            new_row = []
            for col_index in range(self.grid_size[1]):
                btn = row[col_index]
                new_btn = btn.to_square(frame)
                Grid.columnconfigure(frame, col_index, weight=1)
                new_btn.grid(row=row_index, column=col_index, sticky=N+S+E+W)
                if new_btn.flaged:
                    new_btn.flag()
                elif new_btn.clicked_on:
                    new_btn.clicked()
                new_row.append(new_btn)
            new_grid.append(new_row)
        return new_grid

    def around_square(self, row_num: int, col_num: int, print_=False) -> list[Square]:
        around = []
        coors = []

        coors.append((row_num + 1, col_num))  # Adds the square above
        coors.append((row_num - 1, col_num))  # Adds the square below
        coors.append((row_num, col_num + 1))  # Adds the square to the right
        coors.append((row_num, col_num - 1))  # Adds the square to the left
        coors.append((row_num + 1, col_num + 1))  # Adds the top right corner
        coors.append((row_num + 1, col_num - 1))  # Adds the top left corner
        coors.append((row_num - 1, col_num - 1))  # Adds the bottum left corner
        coors.append((row_num - 1, col_num + 1))  # Adds the bottum right corner
        
        filtered_coors = []
        for coor in coors:
            row, col = coor
            try:
                _ = self.grid[row][col]
            except IndexError:
                pass
            else:
                if coor[0] >= 0 and coor[1] >= 0:
                    filtered_coors.append(coor)
        
        if print_:
            print(f'\nFor y:{row_num} x:{col_num}\n{filtered_coors}')

        for coor in filtered_coors:
            row, col = coor
            try:
                around.append(self.grid[row][col])
            except IndexError:
                pass

        return around


class PickleButtonGrid:
    """Same as `ButtonGrid` but is used to pickle and save data"""

    def __init__(self, grid_size: int, grid: list[list[PickleSquare]]) -> None:
        self.grid_size = grid_size
        self.grid = grid

    def to_grid(self, window) -> ButtonGrid:
        return ButtonGrid(self.grid_size, window, self.grid)

    @classmethod
    def from_grid(cls, button_grid: ButtonGrid):
        grid = [
            [PickleSquare.from_square(square) for square in row]
            for row in button_grid.grid
        ]

        return cls(button_grid.grid_size, grid)


if __name__ == '__main__':
    ButtonGrid((10, 10), Tk()).root.mainloop()
