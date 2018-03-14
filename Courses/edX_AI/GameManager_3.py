from Grid_3       import Grid
from ComputerAI_3 import ComputerAI
from PlayerAI_3   import PlayerAI
from Displayer_3  import Displayer
from random       import randint
import time
import numpy as np
import matplotlib.pyplot as plt

defaultInitialTiles = 2
defaultProbability = 0.9

actionDic = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}

(PLAYER_TURN, COMPUTER_TURN) = (0, 1)

# Time Limit Before Losing
timeLimit = 0.2
allowance = 0.05

class GameManager:
    def __init__(self, size = 4):
        self.grid = Grid(size)
        self.possibleNewTiles = [2, 4]
        self.probability = defaultProbability
        self.initTiles  = defaultInitialTiles
        self.computerAI = None
        self.playerAI   = None
        self.displayer  = None
        self.over       = False
        self.max_time_for_get_move = 0
        self.next_move_counter = 0
        self.MAX_NEXT_MOVE_COUNTER = 10000

    def setComputerAI(self, computerAI):
        self.computerAI = computerAI

    def setPlayerAI(self, playerAI):
        self.playerAI = playerAI

    def setDisplayer(self, displayer):
        self.displayer = displayer

    def updateAlarm(self, currTime):
        if currTime - self.prevTime > timeLimit + allowance:
            self.over = False
        else:
            while time.clock() - self.prevTime < timeLimit + allowance:
                pass

            self.prevTime = time.clock()

    def start(self):
        for i in range(self.initTiles):
            self.insertRandonTile()

        # self.grid.map = [[4, 128, 4, 2], [64, 4, 32, 4], [8, 64, 8, 16], [16, 4, 2, 2]]
        # self.grid.map = [[2, 32, 2, 4], [4, 256, 32, 8], [16, 64, 16, 0], [4, 16, 8, 4]]
        # self.grid.map = [[2, 32, 2, 4], [4, 256, 32, 8], [2, 32, 64, 16], [4, 0, 8, 4]]  # with utility_value (min) = -inf for move 0
        # self.grid.map = [[2, 32, 2, 4], [4, 256, 32, 8], [2, 32, 64, 16], [2, 4, 8, 4]]  # for move 0 => -inf - WHY

        self.displayer.display(self.grid)

        # Player AI Goes First
        turn = PLAYER_TURN
        maxTile = 0

        self.prevTime = time.clock()

        while not self.isGameOver() and not self.over:
            # Copy to Ensure AI Cannot Change the Real Grid to Cheat
            gridCopy = self.grid.clone()

            move = None

            if turn == PLAYER_TURN:
                print("Player's Turn:", end="")
                move = self.playerAI.getMove(gridCopy)

                if self.playerAI.run_time > self.max_time_for_get_move:
                    self.max_time_for_get_move = self.playerAI.run_time
                print(actionDic[move])

                # Validate Move
                if move != None and move >= 0 and move < 4:
                    if self.grid.canMove([move]):
                        self.grid.move(move)

                        # Update maxTile
                        maxTile = self.grid.getMaxTile()
                    else:
                        print("Invalid PlayerAI Move")
                        self.over = True
                else:
                    print("Invalid PlayerAI Move - 1")
                    self.over = True

                self.next_move_counter += 1
                if self.next_move_counter > self.MAX_NEXT_MOVE_COUNTER:
                    self.over = True
                    break
            else:
                print("Computer's turn:")
                move = self.computerAI.getMove(gridCopy)

                # Validate Move
                if move and self.grid.canInsert(move):
                    self.grid.setCellValue(move, self.getNewTileValue())
                else:
                    print("Invalid Computer AI Move")
                    self.over = True

            if not self.over:
                self.displayer.display(self.grid)

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.updateAlarm(time.clock())

            turn = 1 - turn

        print('maxTile = {0} - max_time_for_get_move = {1:5.4f} - number_players_moves = {2}'.format(maxTile, self.max_time_for_get_move, self.next_move_counter))

        self.plot_move_times()

    def plot_move_times(self):
        x = np.array([i for i in range(len(self.playerAI.run_time_list))])
        y = np.array(self.playerAI.run_time_list)
        plt.plot(x, y)
        plt.show()
        # plot with various axes scales
        plt.figure(1)
        # linear
        plt.subplot(221)
        plt.plot(x, y)
        plt.yscale('linear')
        plt.title('linear')
        plt.grid(True)

    def isGameOver(self):
        return not self.grid.canMove()

    def getNewTileValue(self):
        if randint(0,99) < 100 * self.probability:
            return self.possibleNewTiles[0]
        else:
            return self.possibleNewTiles[1];

    def insertRandonTile(self):
        tileValue = self.getNewTileValue()
        cells = self.grid.getAvailableCells()
        cell = cells[randint(0, len(cells) - 1)]
        self.grid.setCellValue(cell, tileValue)

def main():
    gameManager = GameManager()
    playerAI  	= PlayerAI()
    computerAI  = ComputerAI()
    displayer 	= Displayer()

    gameManager.setDisplayer(displayer)
    gameManager.setPlayerAI(playerAI)
    gameManager.setComputerAI(computerAI)

    gameManager.start()

if __name__ == '__main__':
    main()
