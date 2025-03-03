import logging
import math

import bpy
import bmesh
import numpy as np
import mathutils
import plugin.utils.object

from plugin.modules_import.hair import get_tangent_space_mat


# changed to avoid clamping bug and squares on fins
X_START = -15.9993
Y_START = 0.999756


def get_ob_count(lod_collections):
	return sum(len(coll.objects) for coll in lod_collections)


def create_lods():
	"""Automatic LOD generator by NDP. Generates LOD objects and automatically decimates them for LOD0-LOD5"""
	msgs = []
	logging.info(f"Generating LOD objects")

	# Get active scene and root collection
	scn = bpy.context.scene
	col = scn.collection
	col_list = bpy.types.Collection(col).children

	# Make list of all LOD collections
	lod_collections = [col for col in col_list if col.name[:-1].endswith("LOD")]
	# Setup default lod ratio values
	lod_ratios = [1, 0.8, 0.56, 0.34, 0.2, 0.08]

	# Deleting old LODS
	for lod_coll in lod_collections[1:]:
		for ob in lod_coll.objects:
			# delete old target
			bpy.data.objects.remove(ob, do_unlink=True)

	for lod_index, (lod_coll, ratio) in enumerate(zip(lod_collections, lod_ratios)):
		if lod_index > 0:
			for ob_index, ob in enumerate(lod_collections[0].objects):
				# check if we want to copy this one
				if is_fin(ob) and lod_index > 1:
					continue
				obj1 = copy_ob(ob, f"{scn.name}_LOD{lod_index}")
				obj1.name = f"{scn.name}_lod{lod_index}_ob{ob_index}"

				# Decimating duplicated object
				decimate = obj1.modifiers.new("Decimate", 'DECIMATE')
				decimate.ratio = ratio

				# Changing shells to skin
				if is_shell(ob) and lod_index > 1:
					b_me = obj1.data
					# todo - actually toggle the flag on the bitfield to maintain the other bits
					b_me["flag"] = 565
					# remove shell material
					b_me.materials.pop(index=1)

	msgs.append("LOD objects generated succesfully")
	return msgs


def copy_ob(src_obj, lod_group_name):
	new_obj = src_obj.copy()
	new_obj.data = src_obj.data.copy()
	new_obj.name = src_obj.name + "_copy"
	new_obj.animation_data_clear()
	plugin.utils.object.link_to_collection(bpy.context.scene, new_obj, lod_group_name)
	bpy.context.view_layer.objects.active = new_obj
	return new_obj


def ob_processor_wrapper(func):
	msgs = []
	for lod_i in range(6):
		lod_group_name = f"LOD{lod_i}"
		coll = get_collection(lod_group_name)
		src_obs = [ob for ob in coll.objects if is_shell(ob)]
		trg_obs = [ob for ob in coll.objects if is_fin(ob)]
		if src_obs and trg_obs:
			msgs.append(func(src_obs[0], trg_obs[0]))
	return msgs


def create_fins_wrapper():
	return ob_processor_wrapper(build_fins)


def gauge_uv_scale_wrapper():
	return ob_processor_wrapper(gauge_uv_factors)


def get_collection(name):
	for coll in bpy.data.collections:
		if name in coll.name:
			return coll


def get_ob_from_lod_and_flags(coll, flags=(565,)):
	if coll:
		for ob in coll.objects:
			if "flag" in ob and ob.data["flag"] in flags:
				return ob


def build_fins(src_ob, trg_ob):
	try:
		uv_scale_x = src_ob["uv_scale_x"]
		uv_scale_y = src_ob["uv_scale_y"]
	except:
		raise AttributeError(f"{src_ob.name} has no UV scale properties. Run 'Gauge UV Scale' first!")

	lod_group_name = plugin.utils.object.get_lod(src_ob)
	ob = copy_ob(src_ob, lod_group_name)

	me = ob.data
	# data is per loop
	hair_directions, loop_vertices = build_tangent_table(src_ob.data)
	loop_coord_kd = fill_kd_tree_co(loop_vertices)

	# transfer the material
	me.materials.clear()
	me.materials.append(trg_ob.data.materials[0])
	# rename new object
	trg_name = trg_ob.name
	trg_ob.name += "dummy"
	ob.name = trg_name
	# delete old target
	bpy.data.objects.remove(trg_ob, do_unlink=True)

	# set up copy of normals from src mesh
	mod = ob.modifiers.new('DataTransfer', 'DATA_TRANSFER')
	mod.object = src_ob
	mod.use_loop_data = True
	mod.data_types_loops = {"CUSTOM_NORMAL", }

	# needed for custom normals
	me.use_auto_smooth = True
	# create uv1 layer for fins
	me.uv_layers.new(name="UV1")
	# Get a BMesh representation
	bm = bmesh.new()  # create an empty BMesh
	bm.from_mesh(me)  # fill it in from a Mesh
	edges_start_a = bm.edges[:]
	faces = bm.faces[:]
	bm.faces.ensure_lookup_table()
	# Extrude and create geometry on side 'b'
	normals = [v.normal for v in bm.verts]
	ret = bmesh.ops.extrude_edge_only(bm, edges=edges_start_a)
	geom_extrude = ret["geom"]
	verts_extrude = [ele for ele in geom_extrude if isinstance(ele, bmesh.types.BMVert)]

	# move each extruded verts out across the surface normal
	for v, n in zip(verts_extrude, normals):
		v.co += (n * 0.00001)

	# now delete all old faces, but only faces
	bmesh.ops.delete(bm, geom=faces, context="FACES_ONLY")

	# build uv1 coords
	build_uv(ob, bm, uv_scale_x, uv_scale_y, loop_coord_kd, hair_directions)

	# Finish up, write the bmesh back to the mesh
	bm.to_mesh(me)
	bm.free()  # free and prevent further access

	# remove fur_length vgroup
	for vg_name in ("fur_length", "fur_width"):
		if vg_name in ob.vertex_groups:
			vg = ob.vertex_groups[vg_name]
			ob.vertex_groups.remove(vg)
	me["flag"] = 565

	# remove the particle system, since we no longer have a fur length vertex group
	for mod in ob.modifiers:
		if mod.type == "PARTICLE_SYSTEM":
			ob.modifiers.remove(mod)

	return f'Generated fin geometry {trg_name} from {src_ob.name}'


def get_face_ring(face):
	strip = [face, ]
	for i in range(10):
		# get linked faces
		best_face = get_best_face(strip[-1])
		if best_face:
			strip.append(best_face)
		else:
			break
	return strip


def get_link_faces(bm_face):
	return [f for e in bm_face.edges for f in e.link_faces if not f.tag and f is not bm_face]


def get_best_face(current_face):
	link_faces = get_link_faces(current_face)
	# print(len(link_faces), len(set(link_faces)))
	if link_faces:
		# get the face whose orientation is most similar
		dots = [(abs(current_face.normal.dot(f.normal)), f) for f in link_faces]
		dots.sort(key=lambda x: x[0])
		# dot product = 0 -> vectors are orthogonal
		# we need parallel normals
		best_face = dots[-1][1]
		best_face.tag = True
		return best_face


def get_best_face_dir(current_face, hair_direction):
	link_faces = get_link_faces(current_face)
	# print(len(link_faces), len(set(link_faces)))
	if link_faces:
		# get the face whose orientation is most similar
		dots = [f.edges[0] for f in link_faces]
		# we need parallel normals
		best_face = dots[-1][1]
		best_face.tag = True
		return best_face


def build_uv(ob, bm, uv_scale_x, uv_scale_y, loop_coord_kd, hair_directions):
	# get vertex group index
	# this is stored in the object, not the BMesh
	group_index = ob.vertex_groups["fur_length"].index
	# print(group_index)

	psys_fac = ob.particle_systems[0].settings.hair_length

	# only ever one deform weight layer
	dvert_lay = bm.verts.layers.deform.active

	# get uv 1
	uv_lay = bm.loops.layers.uv["UV1"]

	# basically, the whole UV strip should be oriented so that its hair tilts in the same direction
	# start by looking at the vcol of this face's two base verts in the shell mesh's original tangent space
	# decide with which edge to continue
	# pick the adjoining face whose base edge's direction aligns best with the respective tangent space
	for current_face in bm.faces:
		# this face has not been processed
		if not current_face.tag:
			# current_face.tag = True
			# add tuple face, hair_dir, a/b
			# print("new strip")
			strip = [current_face, ]
			modes = []
			# base_edge corresponds to the original edge before extrusion
			while True:
				current_face = strip[-1]
				current_face.tag = True
				base_edge, edge_a, top_edge, edge_b = current_face.edges
				a, b = get_hair_angles(base_edge, edge_a, edge_b, hair_directions, loop_coord_kd)
				# print(a, b)
				# compare both angles
				if a < b:
					# print("at b")
					# hair direction at a is closer to a->b
					# so the hair points from a to b
					# so find next face at edge_b
					look_at_edge = edge_b
					modes.append(0)
				else:
					# hair direction at b is closer to b->a
					# continue equivalent to for the other case
					look_at_edge = edge_a
					# print("at a")
					modes.append(1)
				if len(strip) == 10:
					break
				next_face = get_best_angled_face(look_at_edge, hair_directions, loop_coord_kd)
				if not next_face:
					break
				strip.append(next_face)

			assert len(strip) == len(modes)
			# print("strip", len(strip), modes)
			# faces should be mapped so that hair direction points to the left in UV space
			# store the x position
			x_pos_dic = {}
			for face, mode in zip(strip, modes):
				# print(f"mode {mode}")
				# todo - may need to handle face according to mode
				# if mode == 0:
				# 	# mode 0 - put this face's edge a to the right, because hair points from a to b
				# 	pass
				# elif mode == 1:
				# 	# mode 1 - put this face's edge b to the right, because hair points from b to a
				# 	pass
				# update X coords
				base_edge, edge_a, top_edge, edge_b = current_face.edges
				length = base_edge.calc_length() * uv_scale_x
				# print(x_pos_dic)
				ind = face.loops[0].vert.index
				# print("ind", ind)
				if ind in x_pos_dic:
					# print("0 in, index", ind)
					left = (0, 3)
					right = (1, 2)
				else:
					# print("1 in, index", ind2)
					left = (1, 2)
					right = (0, 3)
				# fall back to start if top left vertex hasn't been keyed in the dict
				x_0 = x_pos_dic.get(face.loops[left[0]].vert.index, X_START)
				# left edges
				for i in left:
					loop = face.loops[i]
					loop[uv_lay].uv.x = x_0
					# print("left", loop.vert.index, x_0)
					x_pos_dic[loop.vert.index] = x_0
				# right edge
				for i in right:
					loop = face.loops[i]
					loop[uv_lay].uv.x = x_0 + length
					# print("right", loop.vert.index, x_0 + length)
					x_pos_dic[loop.vert.index] = x_0 + length

				# update Y coords
				# top edge
				# print(len(base_edge.link_loops), list(base_edge.link_loops), face.loops[:2])
				for loop in face.loops[:2]:
					loop[uv_lay].uv.y = Y_START
				# lower edge
				for loop in face.loops[2:]:
					vert = loop.vert
					dvert = vert[dvert_lay]
					if group_index in dvert:
						weight = dvert[group_index]
						loop[uv_lay].uv.y = Y_START - (weight * psys_fac * uv_scale_y)
	logging.info("Finished UV generation")


def get_best_angled_face(edge_b, hair_directions, loop_coord_kd):
	link_faces = [f for f in edge_b.link_faces if not f.tag]
	if not link_faces:
		return
	results = []
	for face in link_faces:
		f_base_edge, f_edge_a, f_top_edge, f_edge_b = face.edges
		a, b = get_hair_angles(f_base_edge, f_edge_a, f_edge_b, hair_directions, loop_coord_kd)
		results.append((a, b))
	# pick the faces with the lowest angle
	# 0 = a, 1 = b
	face_ind, mode = np.unravel_index(np.argmin(results, axis=None), (len(results), 2))
	# angle should be smaller than 90° to be considered ok
	best_angle = results[face_ind][mode]
	if best_angle > math.radians(90.0):
		logging.debug(f"Discarded best face with angle {math.degrees(best_angle)}°")
		return
	next_face = link_faces[face_ind]
	return next_face


def get_hair_angles(base_edge, edge_a, edge_b, hair_directions, loop_coord_kd):
	# get the base verts
	base_vert_a = [v for v in edge_a.verts if v in base_edge.verts][0]
	base_vert_b = [v for v in edge_b.verts if v in base_edge.verts][0]
	# check both edges
	a = hair_angle_for_verts(base_vert_a, base_vert_b, hair_directions, loop_coord_kd)
	b = hair_angle_for_verts(base_vert_b, base_vert_a, hair_directions, loop_coord_kd)
	return a, b


def hair_angle_for_verts(ref_vert, other_vert, hair_directions, loop_coord_kd):
	ref_to_other = other_vert.co - ref_vert.co
	# find the closest vertex in the original mesh
	loop_vert_co, loop_vert_i, dist = loop_coord_kd.find(ref_vert.co)
	if dist > 0.0:
		logging.warning(f"Could not find a perfect match in kd find")
	# this vector rests in the original vertex's tangent plane
	hair_direction = hair_directions[loop_vert_i]
	if hair_direction.length == 0.0:
		print(f"hair_direction_a is zero")
	elif ref_to_other.length == 0.0:
		print(f"ref_to_other is zero")
	else:
		angle_a = ref_to_other.angle(hair_direction)
		# print(f"angle {angle_a}")
		return angle_a


def gauge_uv_factors(src_ob, trg_ob):
	logging.info(f"Gauging UV scale for {trg_ob.name} from {src_ob.name}")
	vg = src_ob.vertex_groups["fur_length"]
	psys = src_ob.particle_systems[0]
	hair_length = psys.settings.hair_length

	# populate a KD tree with all verts from the base (shells) mesh
	src_me = src_ob.data
	kd = fill_kd_tree_co(src_me.vertices)

	x_facs = []
	y_facs = []
	trg_me = trg_ob.data
	for i, p in enumerate(trg_me.polygons):
		# print(p)
		base = []
		top = []
		for loop_index in p.loop_indices:
			uvs = [(layer.data[loop_index].uv.x, 1 - layer.data[loop_index].uv.y) for layer in trg_me.uv_layers]
			# print(uvs)
			# reindeer is an edge case and starts slightly lower
			if uvs[1][1] < 0.001:
				base.append(loop_index)
			else:
				top.append(loop_index)

		if len(base) == 2:
			# print(base)
			uv_verts = [trg_me.uv_layers[1].data[loop_index].uv.x for loop_index in base]
			uv_len = abs(uv_verts[1] - uv_verts[0])
			# print(uv_len)
			loops = [trg_me.loops[loop_index] for loop_index in base]
			me_verts = [trg_me.vertices[loop.vertex_index].co for loop in loops]
			v_len = (me_verts[1] - me_verts[0]).length
			# print(v_len)
			# print("Fac", uv_len/v_len)
			if v_len:
				x_facs.append(uv_len / v_len)

		if base and top:
			uv_verts = [trg_me.uv_layers[1].data[loop_index].uv.y for loop_index in (base[0], top[0])]
			uv_height = abs(uv_verts[1] - uv_verts[0])
			# print(uv_height)

			# find the closest vert on base shell mesh
			loop = trg_me.loops[base[0]]
			find_co = trg_me.vertices[loop.vertex_index].co
			co, index, dist = kd.find(find_co)
			vert = src_me.vertices[index]
			for vertex_group in vert.groups:
				vgroup_name = src_ob.vertex_groups[vertex_group.group].name
				if vgroup_name == "fur_length":
					base_fur_length = vertex_group.weight * hair_length
					if base_fur_length:
						y_facs.append(uv_height / base_fur_length)
				# if vgroup_name == "fur_width":
				# 	base_fur_width = vertex_group.weight
		# print("Close to center:", co, index, dist, find_co)
	#	 if i == 20:
	#		  break
	uv_scale_x = np.mean(x_facs)
	uv_scale_y = np.mean(y_facs)
	src_ob["uv_scale_x"] = uv_scale_x
	src_ob["uv_scale_y"] = uv_scale_y
	# print(base_fur_width, uv_scale_x/base_fur_width)
	return f"Found UV scale ({uv_scale_x}, {uv_scale_y})"


def build_tangent_table(me):
	"""Stores coord & direction"""
	me.calc_tangents()
	vcol_layer = me.vertex_colors[0].data
	hair_directions = []
	vertices = []
	for loop in me.loops:
		vertex = me.vertices[loop.vertex_index]
		tangent_space_mat = get_tangent_space_mat(loop)
		vcol = vcol_layer[loop.index].color
		r = (vcol[0] - 0.5)
		# g = (vcol[1] - 0.5)*FAC
		b = (vcol[2] - 0.5)
		vec = mathutils.Vector((r, -b, 0))

		hair_direction = tangent_space_mat @ vec
		hair_directions.append(hair_direction)
		vertices.append(vertex)
	return hair_directions, vertices


def fill_kd_tree_co(iterable):
	kd = mathutils.kdtree.KDTree(len(iterable))
	for i, v in enumerate(iterable):
		kd.insert(v.co, i)
	kd.balance()
	return kd


def is_fin(ob):
	if not ob.data.materials:
		raise AttributeError(f"{ob.name} has no materials!")
	for b_mat in ob.data.materials:
		if not b_mat:
			raise AttributeError(f"{ob.name} has an empty material slot!")
		if "_fur_fin" in b_mat.name.lower():
			return True


def is_shell(ob):
	if not ob.data.materials:
		raise AttributeError(f"{ob.name} has no materials!")
	for b_mat in ob.data.materials:
		if not b_mat:
			raise AttributeError(f"{ob.name} has an empty material slot!")
		if "_fur_shell" in b_mat.name.lower():
			return True


UP_VEC = mathutils.Vector((0, 0, 1))


def is_flipped(uv_layer, poly):
	"""Returns True if poly is flipped in uv_layer"""
	# from https://blenderartists.org/t/addon-flipped-uvs-selector/668111/5
	# order of polygon loop defines direction of face normal
	# and that same loop order is used in uv data.
	# With this knowladge we can easily say that cross product:
	# (v2.uv-v1.uv)x(v3.uv-v2.uv) gives us uv normal direction of part of the polygon. Further
	# this normal has to be used in dot product with up vector (0,0,1) and result smaller than zero
	# means uv normal is pointed in opposite direction than it should be (partial polygon v1,v2,v3 is flipped).

	# calculate uv differences between current and next face vertex for whole polygon
	diffs = []
	for l_i in poly.loop_indices:
		next_l = l_i + 1 if l_i < poly.loop_start + poly.loop_total - 1 else poly.loop_start

		next_v_uv = uv_layer[next_l].uv
		v_uv = uv_layer[l_i].uv

		diffs.append((next_v_uv - v_uv).to_3d())

	# go trough all uv differences and calculate cross product between current and next.
	# cross product gives us normal of the triangle. That normal then is used in dot product
	# with up vector (0,0,1). If result is negative we have found flipped part of polygon.
	for i, diff in enumerate(diffs):
		if i == len(diffs) - 1:
			break

		# as soon as we find partial flipped polygon we select it and finish search
		if diffs[i].cross(diffs[i + 1]) @ UP_VEC <= 0:
			return True
	return False
