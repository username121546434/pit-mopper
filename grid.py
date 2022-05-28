from tkinter import *
from squares import Square
import random

class ButtonGrid:
    def __init__(self, grid_size, window:Tk):
        self.grid_size = grid_size
        self.root = window
        self.grid = self.button_grid()

    def button_grid(self) -> list[list[Square]]:
        Grid.rowconfigure(self.root, 1, weight=1)
        Grid.columnconfigure(self.root, 1, weight=1)
        grid = []
        blank = "  " * 3
        #Create & Configure frame 
        frame=Frame(self.root)
        frame.grid(row=1, column=1, sticky=N+S+E+W)
        for row_index in range(self.grid_size):
            Grid.rowconfigure(frame, row_index, weight=1)
            row = []
            for col_index in range(self.grid_size):
                Grid.columnconfigure(frame, col_index, weight=1)
                btn = Square(master = frame, text = blank) #create a button inside frame 
                btn.grid(row=row_index, column=col_index, sticky=N+S+E+W)
                #Store row and column indices as a Button attribute
                btn.position = (col_index, row_index)
                row.append(btn)
            grid.append(row)

        for row in grid:
            row_num = grid.index(row)
            for square in row:
                col_num = row.index(square)
                dice = random.randint(1, 4)
                coor = (row_num, col_num)
                if dice == 2 and all(1 < num < self.grid_size - 1 for num in coor):
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

    def around_square(self, row_num:int, col_num:int, print_ = False) -> list[Square]:
        around = []
        coors = []

        coors.append((row_num + 1, col_num)) # Adds the square above
        coors.append((row_num - 1, col_num)) # Adds the square below
        coors.append((row_num, col_num + 1)) # Adds the square to the right
        coors.append((row_num, col_num - 1)) # Adds the square to the left
        coors.append((row_num + 1, col_num + 1)) # Adds the top right corner
        coors.append((row_num + 1, col_num - 1)) # Adds the top left corner
        coors.append((row_num - 1, col_num - 1)) # Adds the bottum left corner
        coors.append((row_num - 1, col_num + 1)) # Adds the bottum right corner

        if print_:
            print(f'\nFor y:{row_num} x:{col_num}\n{coors}')

        for coor in coors:
            row, col = coor
            try:
                around.append(self.grid[row][col])
            except IndexError:
                pass

        return around

if __name__ == '__main__':
    ButtonGrid(10, Tk()).root.mainloop()