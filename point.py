import maya.cmds as cmds


class Point:

    def __init__(self, _x, _y, _z):
        self.m_x = _x
        self.m_y = _y
        self.m_z = _z

    def setX(self, _x):
        self.m_x = _x

    def setY(self, _y):
        self.m_y = _y

    def setZ(self, _z):
        self.m_z = _z

    def draw(self):
        a = cmds.spaceLocator(p=(0, 0, 0))
        cmds.move(self.m_x, self.m_y, self.m_z, a)
