import math
import maya.cmds as cmds


class Edge:
    def __init__(self, _v1, _v2):
        self.m_v1 = _v1
        self.m_v2 = _v2
        self.m_mayaEdge = ""

    def calcLength(self):
        result = object()
        result.x = self.m_v1.getX() - self.m_v2.getX()
        result.y = self.m_v1.getY() - self.m_v2.getY()
        result.z = self.m_v1.getZ() - self.m_v2.getZ()
        return math.sqrt(result.x * result.x + result.y * result.y + result.z * result.z)

    def draw(self):
        self.m_mayaEdge = cmds.curve(ep=[self.m_v1.getVec3(), self.m_v2.getVec3()], d=1)

    def getMayaEdge(self):
        return self.m_mayaEdge
