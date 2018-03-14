from random import randint
from BaseAI_3 import BaseAI
from Grid_3 import Grid
from PlayerAI_3 import PlayerAI

grid = Grid()
grid.map = [
[4, 64, 8, 4],
[32, 8, 64, 8],
[256, 512, 32, 4],
[4, 8, 4, 2]]

moves = [1,2,3,4]
print(moves)
moves[2] =7
print(moves)

print(len(grid.getAvailableCells()))
print(grid.map)
print(PlayerAI.is_state_terminal(grid, 'min'))


