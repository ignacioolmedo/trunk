# encoding: utf-8
"""
Export (not only) geometry to various formats.
"""

from yade.wrapper import *
from yade import utils,Matrix3,Vector3

#textExt===============================================================
def textExt(filename, format='x_y_z_r', comment='',mask=-1):
	"""Save sphere coordinates and other parameters into a text file in specific format. Non-spherical bodies are silently skipped. Users can add here their own specific format, giving meaningful names. The first file row will contain the format name. Be sure to add the same format specification in ymport.textExt.

	:param string filename: the name of the file, where sphere coordinates will be exported.
	:param string format: the name of output format. Supported 'x_y_z_r'(default), 'x_y_z_r_matId'
	:param string comment: the text, which will be added as a comment at the top of file. If you want to create several lines of text, please use '\\\\n#' for next lines.
	:param int mask: export only spheres with the corresponding mask export only spheres with the corresponding mask
	:return: number of spheres which were written.
	:rtype: int
	"""
	O=Omega()
	
	try:
		out=open(filename,'w')
	except:
		raise RuntimeError("Problem to write into the file")
	
	count=0
	
	out.write('#format ' + format + '\n')
	if (comment):
		out.write('# ' + comment + '\n')
	for b in O.bodies:
		try:
			if (isinstance(b.shape,Sphere) and ((mask<0) or ((mask&b.mask)>0))):
				if (format=='x_y_z_r'):
					out.write('%g\t%g\t%g\t%g\n'%(b.state.pos[0],b.state.pos[1],b.state.pos[2],b.shape.radius))
				elif (format=='x_y_z_r_matId'):
					out.write('%g\t%g\t%g\t%g\t%d\n'%(b.state.pos[0],b.state.pos[1],b.state.pos[2],b.shape.radius,b.material.id))
				elif (format=='id_x_y_z_r_matId'):
					out.write('%d\t%g\t%g\t%g\t%g\t%d\n'%(b.id,b.state.pos[0],b.state.pos[1],b.state.pos[2],b.shape.radius,b.material.id))
				else:
					raise RuntimeError("Please, specify a correct format output!");
				count+=1
		except AttributeError:
			pass
	out.close()
	return count

#VTKWriter===============================================================
class VTKWriter:
	"""
	USAGE:
	create object vtk_writer = VTKWriter('base_file_name'),
	add to engines PyRunner with command='vtk_writer.snapshot()'
	"""
	def __init__(self,baseName='snapshot',startSnap=0):
		self.snapCount = startSnap
		self.baseName=baseName

	def snapshot(self):
		import xml.dom.minidom
		#import xml.dom.ext # python 2.5 and later		

		positions=[]; radii=[]

		for b in Omega().bodies:
			if b.mold.name=='Sphere':
				positions.append(b.phys['se3'][0])
				radii.append(b.mold['radius'])

		# Document and root element
		doc = xml.dom.minidom.Document()
		root_element = doc.createElementNS("VTK", "VTKFile")
		root_element.setAttribute("type", "UnstructuredGrid")
		root_element.setAttribute("version", "0.1")
		root_element.setAttribute("byte_order", "LittleEndian")
		doc.appendChild(root_element)

		# Unstructured grid element
		unstructuredGrid = doc.createElementNS("VTK", "UnstructuredGrid")
		root_element.appendChild(unstructuredGrid)

		# Piece 0 (only one)
		piece = doc.createElementNS("VTK", "Piece")
		piece.setAttribute("NumberOfPoints", str(len(positions)))
		piece.setAttribute("NumberOfCells", "0")
		unstructuredGrid.appendChild(piece)

		### Points ####
		points = doc.createElementNS("VTK", "Points")
		piece.appendChild(points)

		# Point location data
		point_coords = doc.createElementNS("VTK", "DataArray")
		point_coords.setAttribute("type", "Float32")
		point_coords.setAttribute("format", "ascii")
		point_coords.setAttribute("NumberOfComponents", "3")
		points.appendChild(point_coords)

		string = str()
		for x,y,z in positions:
			string += repr(x) + ' ' + repr(y) + ' ' + repr(z) + ' '
		point_coords_data = doc.createTextNode(string)
		point_coords.appendChild(point_coords_data)

		#### Cells ####
		cells = doc.createElementNS("VTK", "Cells")
		piece.appendChild(cells)

		# Cell locations
		cell_connectivity = doc.createElementNS("VTK", "DataArray")
		cell_connectivity.setAttribute("type", "Int32")
		cell_connectivity.setAttribute("Name", "connectivity")
		cell_connectivity.setAttribute("format", "ascii")		
		cells.appendChild(cell_connectivity)

		# Cell location data
		connectivity = doc.createTextNode("0")
		cell_connectivity.appendChild(connectivity)

		cell_offsets = doc.createElementNS("VTK", "DataArray")
		cell_offsets.setAttribute("type", "Int32")
		cell_offsets.setAttribute("Name", "offsets")
		cell_offsets.setAttribute("format", "ascii")				
		cells.appendChild(cell_offsets)
		offsets = doc.createTextNode("0")
		cell_offsets.appendChild(offsets)

		cell_types = doc.createElementNS("VTK", "DataArray")
		cell_types.setAttribute("type", "UInt8")
		cell_types.setAttribute("Name", "types")
		cell_types.setAttribute("format", "ascii")				
		cells.appendChild(cell_types)
		types = doc.createTextNode("1")
		cell_types.appendChild(types)

		#### Data at Points ####
		point_data = doc.createElementNS("VTK", "PointData")
		piece.appendChild(point_data)

		# Particle radii
		if len(radii) > 0:
			radiiNode = doc.createElementNS("VTK", "DataArray")
			radiiNode.setAttribute("Name", "radii")
			radiiNode.setAttribute("type", "Float32")
			radiiNode.setAttribute("format", "ascii")
			point_data.appendChild(radiiNode)

			string = str()
			for r in radii:
				string += repr(r) + ' '
			radiiData = doc.createTextNode(string)
			radiiNode.appendChild(radiiData)

		#### Cell data (dummy) ####
		cell_data = doc.createElementNS("VTK", "CellData")
		piece.appendChild(cell_data)

		# Write to file and exit
		outFile = open(self.baseName+'%04d'%self.snapCount+'.vtu', 'w')
#		xml.dom.ext.PrettyPrint(doc, file)
		doc.writexml(outFile, newl='\n')
		outFile.close()
		self.snapCount+=1
		
def text(filename,mask=-1):
	"""Save sphere coordinates into a text file; the format of the line is: x y z r. Non-spherical bodies are silently skipped. Example added to examples/regular-sphere-pack/regular-sphere-pack.py

	:param string filename: the name of the file, where sphere coordinates will be exported.
	:param int mask: export only spheres with the corresponding mask
	:return: number of spheres which were written.
	:rtype: int
	"""
	return (textExt(filename=filename, format='x_y_z_r',mask=mask))



#VTKExporter===============================================================

class VTKExporter:
	"""Class for exporting data to VTK Simple Legacy File (for example if, for some reason, you are not able to use VTKRecorder). Export of spheres and facets is supported.

	USAGE:
	create object vtkExporter = VTKExporter('baseFileName'),
	add to engines PyRunner with command='vtkExporter.exportSomething(params)'

	Example: :ysrc:`examples/test/vtk-exporter/vtkExporter.py`, :ysrc:`examples/test/unv-read/unvReadVTKExport.py`.

	:param string baseName: name of the exported files. The files would be named baseName-spheres-snapNb.vtk or baseName-facets-snapNb.vtk
	:param int=0 startSnap: the numbering of files will start form startSnap
	"""
	def __init__(self,baseName,startSnap=0):
		self.spheresSnapCount = startSnap
		self.facetsSnapCount = startSnap
		self.baseName = baseName

	def exportSpheres(self,ids='all',what=[],comment="comment",numLabel=None):
		"""exports spheres (positions and radius) and defined properties.

		:param ids: if dd "all", then export all spheres, otherwise only spheres from integer list
		:type ids: [int] | "all"
		:param what: what other than then position and radius export. parameter is list of couple (name,command). Name is string under which it is save to vtk, command is string to evaluate. Node that the bodies are labeled as b in this function. Scalar, vector and tensor variables are supported. For example, to export velocity (with name particleVelocity) and the distance form point (0,0,0) (named as dist) you should write: ... what=[('particleVelocity','b.state.vel'),('dist','b.state.pos.norm()', ...
		:type what: [tuple(2)]
		:param string comment: comment to add to vtk file
		:param int numLabel: number of file (e.g. time step), if unspecified, the last used value + 1 will be used
		"""
		allIds = False
		if ids=='all':
			ids=xrange(len(O.bodies))
			allIds = True
		bodies = []
		for i in ids:
			b = O.bodies[i]
			if not b: continue
			if b.shape.__class__.__name__!="Sphere":
				if not allIds: print "Warning: body %d is not Sphere"%(i)
				continue
			bodies.append(b)
		n = len(bodies)
		outFile = open(self.baseName+'-spheres-%04d'%self.spheresSnapCount+'.vtk', 'w')
		outFile.write("# vtk DataFile Version 3.0.\n%s\nASCII\n\nDATASET POLYDATA\nPOINTS %d double\n"%(comment,n))
		for b in bodies:
			pos = b.state.pos
			outFile.write("%g %g %g\n"%(pos[0],pos[1],pos[2]))
		outFile.write("\nPOINT_DATA %d\nSCALARS radius double 1\nLOOKUP_TABLE default\n"%(n))
		for b in bodies:
			outFile.write("%g\n"%(b.shape.radius))
		for name,command in what:
			test = eval(command)
			if isinstance(test,Matrix3):
				outFile.write("\nTENSORS %s double\n"%(name))
				for b in bodies:
					t = eval(command)
					outFile.write("%g %g %g\n%g %g %g\n%g %g %g\n\n"%(t[0,0],t[0,1],t[0,2],t[1,0],t[1,1],t[1,2],t[2,0],t[2,1],t[2,2]))
			elif isinstance(test,Vector3):
				outFile.write("\nVECTORS %s double\n"%(name))
				for b in bodies:
					v = eval(command)
					outFile.write("%g %g %g\n"%(v[0],v[1],v[2]))
			elif isinstance(test,(int,float)):
				outFile.write("\nSCALARS %s double 1\nLOOKUP_TABLE default\n"%(name))
				for b in bodies:
					outFile.write("%g\n"%(eval(command)))
			else:
				print 'WARNING: export.VTKExporter.exportSpheres: wrong `what` parameter, vtk output might be corrupted'
		outFile.close()
		self.spheresSnapCount += 1

	def exportFacets(self,ids='all',what=[],comment="comment",numLabel=None):
		"""
		exports facets (positions) and defined properties. Facets are exported with multiplicated nodes

		:param [int]|"all" ids: if "all", then export all facets, otherwise only facets from integer list
		:param [tuple(2)] what: see exportSpheres
		:param string comment: comment to add to vtk file
		:param int numLabel: number of file (e.g. time step), if unspecified, the last used value + 1 will be used
		"""
		allIds = False
		if ids=='all':
			ids=xrange(len(O.bodies))
			allIds = True
		bodies = []
		for i in ids:
			b = O.bodies[i]
			if not b: continue
			if b.shape.__class__.__name__!="Facet":
				if not allIds: print "Warning: body %d is not Facet"%(i)
				continue
			bodies.append(b)
		n = len(bodies)
		outFile = open(self.baseName+'-facets-%04d'%self.facetsSnapCount+'.vtk', 'w')
		outFile.write("# vtk DataFile Version 3.0.\n%s\nASCII\n\nDATASET POLYDATA\nPOINTS %d double\n"%(comment,3*n))
		for b in bodies:
			p = b.state.pos
			o = b.state.ori
			s = b.shape
			pt1 = p + o*s.vertices[0]
			pt2 = p + o*s.vertices[1]
			pt3 = p + o*s.vertices[2]
			outFile.write("%g %g %g\n"%(pt1[0],pt1[1],pt1[2]))
			outFile.write("%g %g %g\n"%(pt2[0],pt2[1],pt2[2]))
			outFile.write("%g %g %g\n"%(pt3[0],pt3[1],pt3[2]))
		outFile.write("\nPOLYGONS %d %d\n"%(n,4*n))
		i = 0
		for b in bodies:
			outFile.write("3 %d %d %d\n"%(i,i+1,i+2))
			i += 3
		if what:
			outFile.write("\nCELL_DATA %d"%(n))
		for name,command in what:
			test = eval(command)
			if isinstance(test,Matrix3):
				outFile.write("\nTENSORS %s double\n"%(name))
				for b in bodies:
					t = eval(command)
					outFile.write("%g %g %g\n%g %g %g\n%g %g %g\n\n"%(t[0,0],t[0,1],t[0,2],t[1,0],t[1,1],t[1,2],t[2,0],t[2,1],t[2,2]))
			if isinstance(test,Vector3):
				outFile.write("\nVECTORS %s double\n"%(name))
				for b in bodies:
					v = eval(command)
					outFile.write("%g %g %g\n"%(v[0],v[1],v[2]))
			else:
				outFile.write("\nSCALARS %s double 1\nLOOKUP_TABLE default\n"(name))
				for b in bodies:
					outFile.write("%g\n"%(eval(command)))
		outFile.close()
		self.facetsSnapCount += 1

	def exportFacetsAsMesh(self,ids='all',connectivityTable=None,what=[],comment="comment",numLabel=None):
		"""
		exports facets (positions) and defined properties. Facets are exported as mesh (not with multiplicated nodes). Therefore additional parameters connectivityTable is needed

		:param [int]|"all" ids: if "all", then export all facets, otherwise only facets from integer list
		:param [tuple(2)] what: see exportSpheres
		:param string comment: comment to add to vtk file
		:param int numLabel: number of file (e.g. time step), if unspecified, the last used value + 1 will be used
		:param [(float,float,float)|Vector3] nodes: list of coordinates of nodes
		:param [(int,int,int)] connectivityTable: list of node ids of individual elements (facets)
		"""
		allIds = False
		if ids=='all':
			ids=xrange(len(O.bodies))
			allIds = True
		bodies = []
		for i in ids:
			b = O.bodies[i]
			if not b: continue
			if b.shape.__class__.__name__!="Facet":
				if not allIds: print "Warning: body %d is not Facet"%(i)
				continue
			bodies.append(b)
		ids = xrange(len(bodies))
		n = len(bodies)
		if connectivityTable is None:
			print "ERROR: 'connectivityTable' not specified"
			return
		if n != len(connectivityTable):
			print "ERROR: length of 'connectivityTable' does not match length of 'ids', no export"
			return
		nodes = [Vector3.Zero for i in xrange(max(max(e) for e in connectivityTable)+1)]
		for id,e in zip(ids,connectivityTable):
			b = bodies[id]
			p = b.state.pos
			o = b.state.ori
			s = b.shape
			pt1 = p + o*s.vertices[0]
			pt2 = p + o*s.vertices[1]
			pt3 = p + o*s.vertices[2]
			nodes[e[0]] = pt1
			nodes[e[1]] = pt2
			nodes[e[2]] = pt3
		outFile = open(self.baseName+'-facets-%04d'%self.facetsSnapCount+'.vtk', 'w')
		outFile.write("# vtk DataFile Version 3.0.\n%s\nASCII\n\nDATASET POLYDATA\nPOINTS %d double\n"%(comment,len(nodes)))
		gg = 0
		for n in nodes:
			outFile.write("%g %g %g\n"%(n[0],n[1],n[2]))
		outFile.write("\nPOLYGONS %d %d\n"%(len(connectivityTable),4*len(connectivityTable)))
		for e in connectivityTable:
			outFile.write("3 %d %d %d\n"%e)
		if what:
			outFile.write("\nCELL_DATA %d"%(n))
		for name,command in what:
			test = eval(command)
			if isinstance(test,Matrix3):
				outFile.write("\nTENSORS %s double\n"%(name))
				for b in bodies:
					t = eval(command)
					outFile.write("%g %g %g\n%g %g %g\n%g %g %g\n\n"%(t[0,0],t[0,1],t[0,2],t[1,0],t[1,1],t[1,2],t[2,0],t[2,1],t[2,2]))
			if isinstance(test,Vector3):
				outFile.write("\nVECTORS %s double\n"%(name))
				for b in bodies:
					v = eval(command)
					outFile.write("%g %g %g\n"%(v[0],v[1],v[2]))
			else:
				outFile.write("\nSCALARS %s double 1\nLOOKUP_TABLE default\n"(name))
				for b in bodies:
					outFile.write("%g\n"%(eval(command)))
		outFile.close()
		self.facetsSnapCount += 1

#gmshGeoExport===============================================================
def gmshGeo(filename, comment='',mask=-1,accuracy=-1):
	"""Save spheres in geo-file for the following using in GMSH (http://www.geuz.org/gmsh/doc/texinfo/) program. The spheres can be there meshed.

	:param string filename: the name of the file, where sphere coordinates will be exported.
	:param int mask: export only spheres with the corresponding mask export only spheres with the corresponding mask
	:param float accuracy: the accuracy parameter, which will be set for the poinst in geo-file. By default: 1./10. of the minimal sphere diameter.
	:return: number of spheres which were exported.
	:rtype: int
	"""
	O=Omega()
	
	try:
		out=open(filename,'w')
	except:
		raise RuntimeError("Problem to write into the file")
	
	count=0
	#out.write('#format \n')
	# Find the minimal diameter
	if (accuracy<0.0):
		dMin = -1.0
		for b in O.bodies:
			try:
				if (isinstance(b.shape,Sphere) and ((mask<0) or ((mask&b.mask)>0))):
					if (((dMin>0.0) and (dMin>b.shape.radius*2.0)) or (dMin<0.0)):
						dMin = b.shape.radius*2.0
			except AttributeError:
				pass
		accuracy = dMin/10.0
	# Export bodies
	PTS = 0
	CRS = 0
	out.write('Acc = %g;\n'%(accuracy))
	for b in O.bodies:
		try:
			if (isinstance(b.shape,Sphere) and ((mask<0) or ((mask&b.mask)>0))):
				r = b.shape.radius
				x = b.state.pos[0]
				y = b.state.pos[1]
				z = b.state.pos[2]
				out.write('Rad = %g;\n'%(r))
				out.write('Point(%d) = {%g, %g, %g, Acc};\n\
Point(%d) = {%g, %g, %g, Acc};\n\
Point(%d) = {%g, %g, %g, Acc};\n\
Point(%d) = {%g, %g, %g, Acc};\n\
Point(%d) = {%g, %g, %g, Acc};\n\
Point(%d) = {%g, %g, %g, Acc};\n\
Point(%d) = {%g, %g, %g, Acc};\n\n'%(
				PTS+1, x, y, z, 
				PTS+2, r+x, y, z, 
				PTS+3, -r+x, y, z, 
				PTS+4, x, y, r+z, 
				PTS+5, x, y, -r+z, 
				PTS+6, x, r+y, z, 
				PTS+7, x, -r+y, z
				))
				out.write('\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n\
Circle(%d) = {%d, %d, %d};\n'%(
				CRS+1, PTS+4, PTS+1, PTS+6,
				CRS+2, PTS+6, PTS+1, PTS+5,
				CRS+3, PTS+6, PTS+1, PTS+3,
				CRS+4, PTS+3, PTS+1, PTS+7,
				CRS+5, PTS+7, PTS+1, PTS+5,
				CRS+6, PTS+7, PTS+1, PTS+2,
				CRS+7, PTS+2, PTS+1, PTS+6,
				CRS+8, PTS+7, PTS+1, PTS+4,
				CRS+9, PTS+2, PTS+1, PTS+5,
				CRS+10, PTS+5, PTS+1, PTS+3,
				CRS+11, PTS+3, PTS+1, PTS+4,
				CRS+12, PTS+4, PTS+1, PTS+2,
				))
				
				out.write('\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\
Line Loop(%d) = {%d, %d, %d}; Ruled Surface(%d) = {%d};\n\n\
'%(
				(CRS+13), +(CRS+1), -(CRS+7), -(CRS+12), (CRS+14), (CRS+13),
				(CRS+15), +(CRS+7), +(CRS+2), -(CRS+9), (CRS+16), (CRS+15),
				(CRS+17), +(CRS+2), +(CRS+10), -(CRS+3), (CRS+18), (CRS+17),
				(CRS+19), +(CRS+3), +(CRS+11), +(CRS+1), (CRS+20), (CRS+19),
				(CRS+21), +(CRS+8), +(CRS+12), -(CRS+6), (CRS+22), (CRS+21),
				(CRS+23), +(CRS+4), +(CRS+8), -(CRS+11), (CRS+24), (CRS+23),
				(CRS+25), +(CRS+5), +(CRS+10), (CRS+4), (CRS+26), (CRS+25),
				(CRS+27), +(CRS+6), +(CRS+9), -(CRS+5), (CRS+28), (CRS+27),
				))
				PTS+=7
				CRS+=28
				
				count+=1
		except AttributeError:
			pass
	out.close()
	return count
