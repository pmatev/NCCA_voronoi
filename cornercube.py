import maya.cmds as cmds
from .vertex import Vertex
from .edge import Edge


class CornerCube:
    def __init__(self):
        self.m_verts = [Vertex(0, 0, 0),  # 0
                        Vertex(0, 1, 0),   # 1
                        Vertex(1, 1, 0),   # 2
                        Vertex(1, 0, 0),   # 3
                        Vertex(0, 0, 1),   # 4
                        Vertex(0, 1, 1),   # 5
                        Vertex(1, 1, 1),   # 6
                        Vertex(1, 0, 1)    # 7
                        ]
        self.m_edges = [Edge(self.m_verts[0], self.m_verts[1]),
                        Edge(self.m_verts[1], self.m_verts[2]),
                        Edge(self.m_verts[2], self.m_verts[3]),
                        Edge(self.m_verts[3], self.m_verts[0]),  # front face
                        Edge(self.m_verts[4], self.m_verts[5]),
                        Edge(self.m_verts[5], self.m_verts[6]),
                        Edge(self.m_verts[6], self.m_verts[7]),
                        Edge(self.m_verts[7], self.m_verts[4]),  # back face
                        Edge(self.m_verts[0], self.m_verts[4]),
                        Edge(self.m_verts[1], self.m_verts[5]),
                        Edge(self.m_verts[2], self.m_verts[6]),
                        Edge(self.m_verts[3], self.m_verts[7])  # inbetweens
                        ]
        self.m_name = ""
        self.m_pos = (0, 0, 0)

    def getVerts(self):
        return self.m_verts

    def getEdges(self):
        return self.m_edges

    def markCorners(self, _ids):
        for i in range(len(_ids)):
            self.m_verts[i].setMarked(int(_ids[i]))

    def getBinaryCode(self):
        binStr = ""
        for i in self.m_verts:
            binStr += "%d" % (int(i.isMarked()))
        return binStr

    def setName(self, _name):
        self.m_name = _name

    def getName(self):
        return self.m_name

    def setPos(self, _pos):
        self.m_pos = _pos

    def drawVerts(self):
        mayaVerts = []
        for i in self.m_verts:
            i.draw()
            mayaVerts.append(i.getMayaSphere())
        return mayaVerts

    def drawEdges(self):
        mayaEdges = []
        for i in self.m_edges:
            i.draw()
            mayaEdges.append(i.getMayaEdge())
        return mayaEdges

    def draw(self):
        mayaVerts = self.drawVerts()
        mayaEdges = self.drawEdges()

        grp = cmds.group(em=True, n=self.m_name)
        cmds.parent(mayaVerts, mayaEdges, grp)
        cmds.move(self.m_pos[0], self.m_pos[1], self.m_pos[2], grp)
