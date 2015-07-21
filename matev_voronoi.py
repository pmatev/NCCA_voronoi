import os
import subprocess
from sys import IOrror
import maya.OpenMaya as om
import maya.cmds as cmds


def get_selected_points():
    sel = cmds.ls(sl=1)
    points = []
    for s in sel:
        points.append(om.MPoint(*cmds.getAttr(s + ".t")[0]))
    return points


def points_to_file(_points, _filepath):
    points_file = open(_filepath, "w")
    file_content = """3\r\n"""
    file_content += str(len(_points)) + """\r\n"""
    for p in _points:
        file_content += str(p.x) + " " + str(p.y) + " " + str(p.z) + """\r\n"""
    try:
        points_file.write(file_content)
    except IOrror:
        return False
    finally:
        points_file.close()
        print "wrote maya points to file"
        return True


def qvoronoi(_qhull_dir, _input_file, _output_file):
    args = [
        os.path.join(_qhull_dir, "bin/qvoronoi"),
        "o",
        "TI",
        _input_file,
        "TO",
        _output_file
    ]
    subprocess.call(args, shell=False)
    print "wrote voronoi  points"


def qconvex(_qhull_dir, _input_file, _output_file):
    args = [
        os.path.join(_qhull_dir, "bin/qconvex"),
        "o",
        "TI",
        _input_file,
        "TO",
        _output_file
    ]
    subprocess.call(args, shell=False)
    print "wrote convex  points"


def qdelaunay(_qhull_dir, _input_file, _output_file):
    args = [
        os.path.join(_qhull_dir, "bin/qdelaunay"),
        "o",
        "TI",
        _input_file,
        "TO",
        _output_file
    ]
    subprocess.call(args, shell=False)
    print "wrote delaunay  points"


def process_qvoronoi_output(_tmp_dir, _input_file, _limits=[-6, 6, -6, 6, -6, 6]):
    '''
    splits each cell of qvoronoi results into seperate files to be processed by qconvex
    must pass in a directory to dump the results into
    limits list will prevent any voronoi cell with a vertex outside of the limits to not be created
    limits list structure: [x, -x, y, -y, z, -z]
    '''
    if not os.path.exists(_tmp_dir):
        os.makedirs(_tmp_dir)
    try:
        qvoronoi_output = open(_input_file, "r")
    except IOError:
        pass  # print "couldn't open %s" % _input_file)

    num_verts, num_faces = 0, 0
    verts = []
    file_count = 0
    for i, l in enumerate(qvoronoi_output):
        # first line defines num verts and num faces
        if i == 1:
            print i, l
            tmp = l.strip().split()
            num_verts = int(tmp[0])
            num_faces = int(tmp[1])
        # vert info
        if i > 1 and i < num_verts + 2:
            verts.append(l)
        # facet info
        if i >= num_verts + 2:
            tmp = l.strip().split()
            # if infinity vertex in facet
            if int(tmp[1]) == 0:
                pass  # continue
            # test if the cell has all its verts within the limits
            skip = False
            for t in tmp:
                vert_tmp = verts[int(t)].strip().split()
                if float(vert_tmp[0]) < _limits[0] or float(vert_tmp[0]) > _limits[1]:
                    skip = True
                if float(vert_tmp[1]) < _limits[2] or float(vert_tmp[1]) > _limits[3]:
                    skip = True
                if float(vert_tmp[2]) < _limits[4] or float(vert_tmp[2]) > _limits[5]:
                    skip = True
            if skip:
                continue

            fp = os.path.join(_tmp_dir, str(file_count) + ".off")
            try:
                # print fp
                file = open(fp, "w")
            except IOError:
                print "couldn't open %s" % fp
            file_count += 1
            text = """3\r\n"""
            text += tmp.pop(0) + """\r\n"""
            for t in tmp:
                text += verts[int(t)]
            file.write(text)
            file.close()


def draw_hull_from_file(filePath):
    try:
        meshPath = open(filePath, "r")
    except IOError:
        print "couldn't open %s" % filePath
    num_verts, num_faces, num_face_connects = 0, 0, 0
    verts, face_counts, face_connects = [], [], []
    for i, l in enumerate(meshPath):
        if i == 1:
            print i, l
            tmp = l.strip().split()
            num_verts = int(tmp[0])
            num_faces = int(tmp[1])
        if i > 1 and i < num_verts + 2:
            tmp = l.strip().split()
            verts.append((float(tmp[0]), float(tmp[1]), float(tmp[2])))
        if i >= num_verts + 2:
            tmp = l.strip().split()
            for j, t in enumerate(tmp):
                t = int(t)
                if j == 0:
                    face_counts.append(t)
                    num_face_connects += t
                if j > 0:
                    face_connects.append(t)

    points_om = om.MFloatPointArray()
    points_om.setLength(num_verts)
    for i, v in enumerate(verts):
        vtx = om.MFloatPoint(v[0], v[1], v[2])
        points_om.set(vtx, i)

    face_connects_om = om.MIntArray()
    face_connects_om.setLength(num_face_connects)
    for i, c in enumerate(face_connects):
        face_connects_om.set(c, i)

    face_counts_om = om.MIntArray()
    face_counts_om.setLength(num_faces)
    for i, c in enumerate(face_counts):
        face_counts_om.set(c, i)

    fn_mesh = om.MFnMesh()
    fn_mesh.create(num_verts, num_faces, points_om, face_counts_om, face_connects_om)


def main():
    qhull_dir = "~/qhull-2012.1/"
    dataFile = os.path.join(qhull_dir, "tmp/data.dat")

    points = get_selected_points()
    points_to_file(points, dataFile)
    qvoronoi(qhull_dir, dataFile, os.path.join(qhull_dir, "tmp/qvoronoi_output.off"))
    qdelaunay(qhull_dir, dataFile, os.path.join(qhull_dir, "tmp/qdelaunay_output.off"))
    qconvex(qhull_dir, dataFile, os.path.join(qhull_dir, "tmp/qconvex_output.off"))

    tmpDir = os.path.join(qhull_dir, "tmp/tmp_cells/")
    process_qvoronoi_output(tmpDir, os.path.join(qhull_dir, "tmp/qvoronoi_output.off"))

    outDir = os.path.join(qhull_dir, "tmp/out_polys/")
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    tmp_files = os.listdir(tmpDir)
    i = 0

    for f in tmp_files:
        tmp_full_path = os.path.join(tmpDir, f)
        poly_full_path = os.path.join(outDir, "poly%d.off" % i)
        qconvex(qhull_dir, tmp_full_path, poly_full_path)
        draw_hull_from_file(poly_full_path)
        i += 1

    # draw_hull_from_file(os.path.join(qhull_dir, "tmp/qvoronoi_output.off"))


main()
