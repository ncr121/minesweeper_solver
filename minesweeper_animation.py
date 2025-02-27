import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.signal import convolve2d

class Minesweeper:
    colours = ['w', 'b', 'g', 'r', 'navy', 'maroon', 'c', 'k', 'gray']
    
    def __init__(self, size=(16, 30), num_mines=99):
        self.mines = np.random.permutation([1] * num_mines + [0] * (np.prod(size) - num_mines)).reshape(size)
        self.numbers = np.pad(convolve2d(self.mines, [[1, 1, 1], [1, 0, 1], [1, 1, 1]], mode='same'), 1, 'constant')
        self.covered = np.pad(np.full(size, 1), 1, 'constant')

        fig, self.ax = plt.subplots(num=1)
        self.ax.matshow(self.covered, cmap=ListedColormap(['b']))
        self.ax.tick_params(top=False, left=False, bottom=False, labeltop=False, labelleft=False)
        self.ax.set_xticks(range(size[1] + 1))
        self.ax.set_yticks(range(size[0] + 1))
        self.ax.set_xlim(0, size[1])
        self.ax.set_ylim(size[0], 0)
        self.ax.grid()

        self.uncover()
        while np.any(self.covered) and not np.any(self.covered == 10):
            for _ in range(5):
                for i, j in zip(*np.where((self.covered == 0) & (self.numbers > 0))):
                    self.flag_cells(i, j)
                    self.uncover_cells(i, j)

            self.uncover()
            plt.pause(0.3)

    def uncover(self, cell=None):
        if cell is None:
            cell = sorted(zip(*np.where(self.covered == 1)), key=lambda x: np.random.random())[0]

        if self.mines[cell[0] - 1, cell[1] - 1]:
            for i, j in zip(*np.where((self.mines == 1) & (self.covered[1:-1, 1:-1] == 1))):
                self.fill(i, j, 'gray')
                self.ax.add_artist(plt.Circle((j + 0.5, i + 0.5), 0.25, color='k'))

            self.covered[cell[0], cell[1]] = 10
            self.ax.add_artist(plt.Circle((cell[1] - 0.5, cell[0] - 0.5), 0.25, color='r'))
        else:
            self.uncover_cell(*cell)

    def uncover_cell(self, i, j, pause=True):
        if self.covered[i, j]:
            self.covered[i, j] = 0
            self.fill(i - 1, j - 1, 'w')
            self.ax.text(j - 0.5, i - 0.5, self.numbers[i, j], color=self.colours[self.numbers[i, j]],
                         ha='center', va='center')

        if not self.numbers[i, j]:
            for i_, j_ in zip(*np.where(self.adjacent(i, j) == 1)):
                self.uncover_cell(i + i_ - 1, j + j_ - 1, pause=False)

        if pause:
            plt.pause(0.3)

    def fill(self, i, j, color):
        self.ax.fill(j + np.array([0, 0, 1, 1]), i + np.array([0, 1, 1, 0]), color)

    def adjacent(self, i, j):
        return self.covered[i - 1: i + 2, j - 1: j + 2]

    def true_number(self, i, j):
        return self.numbers[i, j] - np.sum(self.adjacent(i, j) == -1)

    def flag_cells(self, i, j):
        if self.true_number(i, j) == np.sum(self.adjacent(i, j) == 1) > 0:
            for i_, j_ in zip(*np.where(self.adjacent(i, j) == 1)):
                self.covered[i + i_ -1, j + j_ -1] = -1
                self.ax.plot(j + j_ - 1.5, i + i_ - 1.5, 'r<')
                plt.pause(0.3)

    def uncover_cells(self, i, j):
        if not self.true_number(i, j) and np.sum(self.adjacent(i, j) == 1):
            for i_, j_ in zip(*np.where(self.adjacent(i, j) == 1)):
                self.uncover_cell(i + i_ - 1, j + j_ - 1)


solver = Minesweeper()
