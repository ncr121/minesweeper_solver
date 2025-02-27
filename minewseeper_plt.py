import random as rd
from functools import reduce
import matplotlib.pyplot as plt


colours = {0: 'w', 1: 'b', 2: 'g', 3: 'r', 4: 'navy', 5: 'maroon', 6: 'c', 7: 'k', 8: 'gray'}

def reduced(lists):
    """Concatenate a list of lists."""
    return reduce(lambda x, y: x + y, lists, [])


def adjacent(x, y):
    """Get (x, y) locations of adjacent cells."""
    adj = [(x + i, y + j) for i in range(- 1, 2) for j in range(- 1, 2)
           if x + i in range(x_dim) and y + j in range(y_dim)]
    adj.remove((x, y))
    
    return adj


def number(x, y):
    """Return the number of a cell (number of bombs in adjacent cells)."""
    return(sum([1 for sq in adjacent(x, y) if sq in bomb_locs]))


def colour(num):
    """Return the font colour of a cell."""
    colour = colours[num]
    
    return(colour)


def reveal(square=None):
    """
    Reveal cell(s). If the cell is a bomb, the game ends. If the cell is a zero,
    reveal all adjacent zeros and the borders of this group of zeros. If the cell
    is non-zero, reveal just that cell.
    """
    x, y = rd.choice(unrevealed) if square == None else square
    
    if (x, y) in bomb_locs:
        for i, j in set(bomb_locs) - set(flagged):
            ax.fill([i, i, i + 1, i + 1], [j, j + 1, j + 1, j], 'gray')
            ax.add_artist(plt.Circle((i + 0.5, j + 0.5), 0.3, color = 'k'))
        ax.add_artist(plt.Circle((x + 0.5, y + 0.5), 0.3, color = 'r'))
        game_over[0] = True        
    elif number(x, y) == 0:
        zeros = [(x, y)]
        counted = []
        
        while len(zeros) > len(counted):
            for sq in set(zeros) - set(counted):
                new = [sqq for sqq in adjacent(*sq) if number(*sqq) == 0 and sqq not in zeros]
                zeros.extend(new)
                counted.append(sq)
        
        all_zeros.append(zeros)
        adj = reduced([adjacent(*sq) for sq in zeros])
        squares = set(zeros + adj) & set(unrevealed)
        
        for i, j in squares:
            ax.fill([i, i, i + 1, i + 1], [j, j + 1, j + 1, j], 'w')
            ax.text(i + 0.4, j + 0.2, str(number(i, j)), fontsize = 6, color = colour(number(i, j)))
            unrevealed.remove((i, j))
    elif (x, y) in unrevealed:
        ax.fill([x, x, x + 1, x + 1], [y, y + 1, y + 1, y], 'w')
        ax.text(x + 0.4, y + 0.2, str(number(x, y)), fontsize = 6, color = colour(number(x, y)))
        unrevealed.remove((x, y))


def available(x, y):
    """Return adjacent cells that are still unrevealed."""
    return([sq for sq in adjacent(x, y) if sq in unrevealed])


def actual(x, y):
    """Return the actual number of a cell (number of unflagged bombs in adjacent cells)."""
    return(number(x, y) - sum([1 for sq in adjacent(x, y) if sq in flagged]))


def flag(x, y):
    """Flag a cell based on the assumption a bomb is in that cell."""
    if actual(x, y) == len(available(x, y)) > 0:
        for i, j in available(x, y):
            ax.fill([i + 0.7, i + 0.7, i + 0.3], [j + 0.2, j + 0.8, j + 0.5], 'r')
            unrevealed.remove((i, j))
            flagged.append((i, j))


def fill(x, y):
    """
    Reveal all adjacent cells if is determined there are no more bombs
    in the adjacent cells.
    """
    if actual(x, y) == 0 and len(available(x, y)) > 0:
        for sq in available(x, y):
            reveal(sq)


def two_one(x, y):
    """
    ? ? ?
    1 2 1
    0 0 0
    
    In the above 3x3 grid showing all adjacent cells of the '2', a flag is placed
    in the 1st and 3rd '?', and the 2nd '?' is revealed.
    """
    axes = [len(set(axis)) == 1 for axis in zip(*available(x, y))]
    axis = axes.index(1) if any(axes) else None
    
    if actual(x, y) == 2 and len(available(x, y)) == 3 and axis:
        shifts = [0, 0]
        shifts[1 - axis] = 1
        ones = [i for i in [- 1, 1] if actual(x + i * shifts[0], y + i * shifts[1]) == 1]
        
        for k in ones:
            i, j = available(x, y)[1 - k]
            ax.fill([i + 0.7, i + 0.7, i + 0.3], [j + 0.2, j + 0.8, j + 0.5], 'r')
            unrevealed.remove((i, j))
            flagged.append((i, j))
            
            for sq in set(available(x + k * shifts[0], y + k * shifts[1])) - set(available(x, y)):
                reveal(sq)


def inside(x, y):
    """
    ? ? ?
    ? 1 ?
    1 1 1
    
    In the above 3x3 grid showing, the top row of '?' is revealed since the
    set of adjacent '?' to the '1' in the middle of the bottom row is a subset
    of the set of adjacent '1' in the middle row.
    """
    revealed = set(adjacent(x, y)) - set(available(x, y))
    adj = [available(i, j) for i, j in revealed]
    supers = [(z, sqs) for z, sqs in zip(revealed, adj) if all(sq in sqs for sq in available(x, y))]
    
    if len(supers) == 1:
        (i, j), squares = supers[0]
        
        if actual(i, j) <= actual(x, y):
            for sq in set(squares) - set(available(x, y)):
                reveal(sq)


def solve():
    for sq in set(all_squares) - set(unrevealed) - set(flagged) - set(reduced(all_zeros)):
        flag(*sq)
        fill(*sq)
        two_one(*sq)
        inside(*sq)


x_dim, y_dim = (16, 30)
num_bombs = 99
all_squares = [(i, j) for i in range(x_dim) for j in range(y_dim)]
bomb_locs = rd.sample(all_squares, num_bombs)

board = plt.figure()
ax = board.add_subplot(111)
ax.set_xticks(range(x_dim + 1))
ax.set_yticks(range(y_dim + 1))
plt.grid()

for i, j in all_squares:
    ax.fill([i, i, i + 1, i + 1], [j, j + 1, j + 1, j], 'b')

unrevealed = all_squares.copy()
flagged = []
all_zeros = []
game_over = [False]

while not game_over[0] and len(flagged) < num_bombs:
    reveal()
    if not game_over[0] and len(flagged) < num_bombs:
        new, old = 0, 1
        while new < old:
            old = len(unrevealed)
            solve()
            new = len(unrevealed)
