import maya.cmds as cmds


def deleteAll():
    cmds.file(f=True, new=True)
