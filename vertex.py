import maya.cmds as cmds
import random

from point import Point


class Vertex:
    def __init__(self, _x, _y, _z):
        self.m_x = _x
        self.m_y = _y
        self.m_z = _z
        self.m_marked = 0  # default unmarked color is blue

        self.m_grid = [[[[] for x in range(3)] for x in range(3)] for x in range(3)]

        self.createRedBlueShaders()  # create the red and blue shaders
        self.m_mayaSphere = ""

    def getX(self):
        return self.m_x

    def getY(self):
        return self.m_y

    def getZ(self):
        return self.m_z

    def getVec3(self):
        return (self.m_x, self.m_y, self.m_z)

    def isMarked(self):
        return self.m_marked

    def setMarked(self, _bool):
        self.m_marked = _bool

    def scatterPoints(self, _numPoints):
        for i in range(_numPoints):
            x = random.uniform(-3, 3)
            y = random.uniform(-3, 3)
            z = random.uniform(-3, 3)

            p = Point(x, y, z)

            # partition the space

            x_id, y_id, z_id = 0, 0, 0

            if x <= -1:
                x_id = 0
            elif x >= 1:
                x_id = 2
            else:
                x_id = 1

            if y <= -1:
                y_id = 0
            elif y >= 1:
                y_id = 2
            else:
                y_id = 1

            if z <= -1:
                z_id = 0
            elif z >= 1:
                z_id = 2
            else:
                z_id = 1

            self.m_grid[x_id][y_id][z_id].append(p)

    def getPointsInRegion(self, _i, _j, _k):
        return self.m_grid[_i][_j][_k]

    def createRedBlueShaders(self):
        if(not cmds.objExists("red")):

            red = cmds.shadingNode('lambert', asShader=True)
            blue = cmds.shadingNode('lambert', asShader=True)

            cmds.rename(red, 'red')
            cmds.rename(blue, 'blue')

            cmds.setAttr('blue.color', 0, 0, 1, type='double3')
            cmds.setAttr('red.color', 1, 0, 0, type='double3')

            print cmds.sets(r=True, nss=True, empty=True, name="redSG")
            print cmds.sets(r=True, nss=True, empty=True, name="blueSG")
            cmds.connectAttr("red.outColor", "redSG.surfaceShader")
            cmds.connectAttr("blue.outColor", "blueSG.surfaceShader")

    def draw(self):
        self.m_mayaSphere = cmds.polySphere(r=0.5, sx=4, sy=4)[0]
        cmds.move(self.m_x, self.m_y, self.m_z, self.m_mayaSphere)

        if(self.m_marked):
            cmds.sets(self.m_mayaSphere, e=True, forceElement="redSG")
        else:
            cmds.sets(self.m_mayaSphere, e=True, forceElement="blueSG")

        for i in self.m_grid:
            for j in i:
                for k in j:
                    for l in k:
                        l.draw()

    def getMayaSphere(self):
        return self.m_mayaSphere
