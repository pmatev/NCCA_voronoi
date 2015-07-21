import maya.cmds as cmds
import random

import cornercube as cc


class TilingGrid:
    def __init__(self, _width, _height, _depth):
        self.m_width = _width
        self.m_height = _height
        self.m_depth = _depth
        self.m_baseTiles = []
        self.m_grid = [[[0 for x in range(self.m_depth)] for x in range(self.m_height)] for x in range(self.m_width)]

    def generateBaseTiles(self):
        for i in range(256):
            binStr = bin(i)[2:]
            binStr = binStr.zfill(8)
            iCube = cc.CornerCube()
            self.m_baseTiles.append(iCube)
            iCube.markCorners(binStr)           # mark the corners based on the binary code
            iCube.setName("Cube%s" % (binStr))

    def getBaseTiles(self):
        return self.m_baseTiles

    def drawBaseTiles(self):
        for i in self.m_baseTiles:
            i.draw()
        for i in range(len(cubes)):
            name = cubes[i].getName()
            cmds.move(i, 0, 0, name)

    def arrangeTiles(self, _startCubeID):

        self.m_grid[0][0][0] = self.m_baseTiles[_startCubeID]

        for i in range(self.m_width):
            for j in range(self.m_height):
                for k in range(self.m_depth):
                    # first one has been filled already
                    if(i == 0 and j == 0 and k == 0):
                        continue
                    else:
                        possibleCubes = []

                        for cube in self.m_baseTiles:
                            match_i = False
                            match_j = False
                            match_k = False
                            trialCubeID = cube.getBinaryCode()

                            #check in i
                            if(i > 0):
                                prevCubeID = self.m_grid[i - 1][j][k].getBinaryCode()
                                if(trialCubeID[0] == prevCubeID[3] and
                                        trialCubeID[1] == prevCubeID[2] and
                                        trialCubeID[5] == prevCubeID[6] and
                                        trialCubeID[4] == prevCubeID[7]
                                   ):
                                    match_i = True
                            else:
                                match_i = True

                            #check in j
                            if(j > 0):
                                prevCubeID = self.m_grid[i][j - 1][k].getBinaryCode()
                                if(trialCubeID[0] == prevCubeID[1] and
                                        trialCubeID[3] == prevCubeID[2] and
                                        trialCubeID[7] == prevCubeID[6] and
                                        trialCubeID[4] == prevCubeID[5]
                                   ):
                                    match_j = True
                            else:
                                match_j = True

                            #check in k
                            if(k > 0):
                                prevCubeID = self.m_grid[i][j][k - 1].getBinaryCode()
                                if(trialCubeID[0] == prevCubeID[4] and
                                        trialCubeID[3] == prevCubeID[7] and
                                        trialCubeID[2] == prevCubeID[6] and
                                        trialCubeID[1] == prevCubeID[5]
                                   ):
                                    match_k = True
                            else:
                                match_k = True

                            # if it matches all axes then we have found a valid tile
                            if(match_i and match_j and match_k):
                                possibleCubes.append(cube)

                        # choose random valid tile
                        randID = random.randint(0, len(possibleCubes) - 1)
                        # print i, j, k, len(possibleCubes), randID
                        self.m_grid[i][j][k] = possibleCubes[randID]

    def drawGrid(self):
        for i in range(self.m_width):
            for j in range(self.m_height):
                for k in range(self.m_depth):
                    self.m_grid[i][j][k].setPos((i, j, k))
                    self.m_grid[i][j][k].draw()
