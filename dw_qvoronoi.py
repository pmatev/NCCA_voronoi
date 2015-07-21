import os
import subprocess
import maya.OpenMaya as om
import maya.cmds as cmds

from .matev_voronoi import draw_hull_from_file


class Maya_QVoronoi(object):
    def __init__(self, qHull_bin_dir, tmp_dir):
        '''
        (str)qHull_bin_dir - directory where the qHull .exes are located
        (str)tmp_dir - where to store all the temporary files that are used by the qHull exes

        this class will create a voronio diagram of mesh objects from a list of MPoints using qHull
        qHull - http://www.qhull.org/
        each method can be used individually as long as the class is initiated with valid directories
        '''
        # paths
        self.qvoronoi_exe = os.path.normpath(os.path.join(qHull_bin_dir, "qvoronoi"))
        self.qconvex_exe = os.path.normpath(os.path.join(qHull_bin_dir, "qconvex"))
        self.qhull_exe = os.path.normpath(os.path.join(qHull_bin_dir, "qhull"))
        self.points_file = os.path.normpath(os.path.join(tmp_dir, "input_points.txt"))
        self.qvoronoi_output_file = os.path.normpath(os.path.join(tmp_dir, "qvoronoi_output.off"))
        self.tmp_cell_dir = os.path.normpath(os.path.join(tmp_dir, "tmp_cells"))
        self.tmp_convex_output = os.path.normpath(os.path.join(tmp_dir, "tmp_convex_output.off"))

        self.limits = [10, -10, 10, -10, 10, -10]

        # output from subprocesses
        self.qvoronoi_stdout = None
        self.qconvex_stdout = None

    def voronoi_from_points(self, points):
        '''
        (list)points - MPoint list
        (list)limits - limits voronoi cells to a bounding box [x,-x, y,-y, z,-z]

        pass in a list of MPoints and get a voronoi diagram!
        '''

        self.points_to_file(points=points, file_path=self.points_file)
        self.qvoronoi(self.vim, self.qvoronoi_output_file)
        self.process_qvoronoi_output_file()
        off_files = os.listdir(self.tmp_cell_dir)
        for f in off_files:
            full_path = os.path.join(self.tmp_cell_dir, f)
            print full_path
            draw_hull_from_file(full_path)

    def points_to_file(self, points, file_path):
        points_file = open(file_path, "w")
        file_content = "3\r\n"
        file_content += str(len(points)) + "\r\n"
        for p in points:
            file_content += str(p.x) + " " + str(p.y) + " " + str(p.z) + "\r\n"
        try:
            points_file.write(file_content)
        finally:
            points_file.close()
            return True
        return False

    def qvoronoi(self, input_file, output_file):
        args = [
            self.qvoronoi_exe,
            "o",
            "TI",
            input_file,
            "TO",
            output_file
        ]
        subprocess.call(args, shell=False)

    def process_qvoronoi_output_file(self):
        '''
        splits each cell of qvoronoi results into seperate files to be processed by qconvex
        must pass in a directory to dump the results into
        limits list will prevent any voronoi cell with a vertex outside of the limits to not be created
        limits list structure: [x, -x, y, -y, z, -z]
        '''
        if not os.path.exists(self.tmp_cell_dir):
            os.makedirs(self.tmp_cell_dir)
        try:
            qvoronoi_output = open(self.qvoronoi_output_file, "r")
        except IOError:
            print "couldn't open %s" % self.qvoronoi_output_file

        num_verts, num_faces = 0, 0
        verts = []
        file_count = 0
        for i, l in enumerate(qvoronoi_output):
            # first line defines num verts and num faces
            if i == 1:
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
                # if int(tmp[1]) == 0:
                # pass#continue
                # test if the cell has all its verts within the limits
                # skip = False
                # for t in tmp:
                # 	vert_tmp = verts[int(t)].strip().split()
                # 	if float(vert_tmp[0])> self.limits[0] or float(vert_tmp[0])< self.limits[1]:
                # 		skip = True
                # 	if float(vert_tmp[1])> self.limits[2] or float(vert_tmp[1])< self.limits[3]:
                # 		skip = True
                # 	if float(vert_tmp[2])> self.limits[4] or float(vert_tmp[2])< self.limits[5]:
                # 		skip = True
                # if skip:
                # 	continue

                try:
                    fp = os.path.join(self.tmp_cell_dir, str(file_count) + ".off")
                    print fp
                    file = open(fp, "w")
                except IOError:
                    print "couldn't open %s" % fp
                file_count += 1
                text = "3\r\n"
                text += tmp.pop(0) + "\r\n"
                for t in tmp:
                    text += verts[int(t)]
                file.write(text)
                file.close()

    # def convex_hull_from_file(self, off_file):
    # 	'''
    # 	creates a polygon from a .off file
    # 	'''
    # 	args = [
    # 	self.qhull_exe,
    # 	"TI",
    # 	off_file,
    # 	"o",
    # 	"TO",
    # 	self.tmp_convex_output
    # 	]
    # 	subprocess.call(args, shell=False)

    # 	try:
    # 		convex_output = open(self.tmp_convex_output, "r")
    # 	except IOError:
    # 		print "couldn't open %s" % tmp_convex_output
    # 	num_verts, num_faces, num_face_connects = 0, 0, 0
    # 	verts, face_counts, face_connects  = [], [], []
    # 	for i,l in enumerate(convex_output):
    # 		if i == 1:
    # 			tmp = l.strip().split()
    # 			num_verts = int(tmp[0])
    # 			num_faces = int(tmp[1])
    # 		if i>1 and i<num_verts+2:
    # 			tmp = l.strip().split()
    # 			verts.append((float(tmp[0]), float(tmp[1]), float(tmp[2])))
    # 		if i>=num_verts+2:
    # 			tmp = l.strip().split()
    # 			for j, t in enumerate(tmp):
    # 				t = int(t)
    # 				if j==0: face_counts.append(t); num_face_connects+=t
    # 				if j>0: face_connects.append(t)

    # 	points_om = om.MFloatPointArray()
    # 	points_om.setLength(num_verts)
    # 	for i, v in enumerate(verts):
    # 		vtx = om.MFloatPoint(v[0], v[1], v[2])
    # 		points_om.set(vtx, i)

    # 	face_connects_om = om.MIntArray()
    # 	face_connects_om.setLength(num_face_connects)
    # 	for i, c in enumerate(face_connects):
    # 		face_connects_om.set(c, i);

    # 	face_counts_om = om.MIntArray()
    # 	face_counts_om.setLength(num_faces)
    # 	for i, c in enumerate(face_counts):
    # 		face_counts_om.set(c,i)

    # 	fn_mesh= om.MFnMesh()
    # 	fn_mesh.create(num_verts, num_faces, points_om, face_counts_om, face_connects_om)


def main(qhull_dir, tmp_dir):
    sel = cmds.ls(sl=1)
    points = []
    for s in sel:
        points.append(om.MPoint(*cmds.getAttr(s + ".t")[0]))

    vor = Maya_QVoronoi(qhull_dir, tmp_dir)
    vor.voronoi_from_points(points)
