# START_GLOBALS
import logging
import math
import numpy as np

from generated.formats.ms2.compound.packing_utils import FUR_OVERHEAD, remap
from plugin.utils.tristrip import triangulate

# END_GLOBALS


class MeshData:

	# START_CLASS

	# @property
	def get_stream_index(self):
		# logging.debug(f"Using stream {self.stream_index}")
		return self.stream_index

	def assign_stream(self, buffer_infos):
		self.stream_info = buffer_infos[self.get_stream_index()]

	def populate(self, ms2_file, base=512, last_vertex_offset=0, sum_uv_dict={}):
		self.sum_uv_dict = sum_uv_dict
		self.last_vertex_offset = last_vertex_offset
		self.end_of_vertices = 0
		self.assign_stream(ms2_file.buffer_infos)
		# print(self)
		self.base = base
		self.shapekeys = None
		self.read_verts()
		self.read_tris()
		# self.validate_tris()
		return self.end_of_vertices

	def pack_verts(self):
		pass

	def write_data(self):
		# write to the stream_info that has been assigned to mesh
		self.vertex_offset = self.stream_info.verts.tell()
		self.tri_offset = self.stream_info.tris.tell()
		self.vertex_count = len(self.verts_data)
		self.tri_index_count = len(self.tri_indices) * self.shell_count
		# write vertices
		self.stream_info.verts.write(self.verts_data.tobytes())
		# write tris
		tri_bytes = self.tri_indices.tobytes()
		# extend tri array according to shell count
		logging.debug(f"Writing {self.shell_count} shells of {len(self.tri_indices)} triangles")
		for shell in range(self.shell_count):
			self.stream_info.tris.write(tri_bytes)

	@property
	def tris_address(self):
		return self.stream_info.vertex_buffer_size + self.tri_offset

	def read_tris(self):
		# read all tri indices for this mesh, but only as many as needed if there are shells
		self.stream_info.stream.seek(self.tris_address)
		index_count = self.tri_index_count // self.shell_count
		logging.debug(f"Reading {index_count} indices at {self.stream_info.stream.tell()}")
		self.tri_indices = np.empty(dtype=np.uint16, shape=index_count)
		self.stream_info.stream.readinto(self.tri_indices)
		# check if there's no empty value left in the array
		# if len(self.tri_indices) != index_count:
		# 	raise BufferError(f"{len(self.tri_indices)} were read into tri index buffer, should have {index_count}")

	@property
	def lod_index(self, ):
		try:
			lod_i = int(math.log2(self.poweroftwo))
		except:
			lod_i = 0
			logging.warning(f"math domain for lod {self.poweroftwo}")
		return lod_i

	@lod_index.setter
	def lod_index(self, lod_i):
		self.poweroftwo = int(math.pow(2, lod_i))

	def update_shell_count(self):
		# 853 in aardvark is a shell mesh, but has no tri shells
		if hasattr(self, "flag") and hasattr(self.flag, "repeat_tris") and self.flag.repeat_tris:
			self.shell_count = 6
		else:
			self.shell_count = 1

	@property
	def tris(self, ):
		if hasattr(self.flag, "stripify") and self.flag.stripify:
			return triangulate((self.tri_indices,))
		else:
			# create non-overlapping tris from flattened tri indices
			tris_raw = np.reshape(self.tri_indices, (len(self.tri_indices)//3, 3))
			# reverse each tri to account for the flipped normals from mirroring in blender
			return np.flip(tris_raw, axis=-1)

	@tris.setter
	def tris(self, b_tris):
		# cast to uint16
		raw_tris = np.array(b_tris, dtype=np.uint16)
		# reverse tris
		raw_tris = np.flip(raw_tris, axis=-1)
		# flatten array
		self.tri_indices = np.reshape(raw_tris, len(raw_tris)*3)

	def validate_tris(self):
		"""See if all tri indices point into the vertex buffer, raise an error if they don't"""
		# this is fairly costly (10 % of total loading time), so don't do it by default
		# max_ind = np.max(self.tri_indices)
		# if max_ind >= len(self.verts_data):
		for max_ind in self.tri_indices:
			if max_ind >= len(self.verts_data):
				raise IndexError(f"Tri index {max_ind} does not point into {len(self.verts_data)} vertices")
		logging.debug("All tri indices are valid")

	def import_fur_as_weights(self, fur):
		# get max of fur length value for all verts
		self.fur_length = np.max(fur[:, 0]) * FUR_OVERHEAD
		# fur length can be set to 0 for the whole mesh, so make sure we don't divide in that case
		if self.fur_length:
			# normalize with some overhead
			fur[:, 0] /= self.fur_length
		# value range of fur width is +-16 - squash it into 0 - 1
		fur[:, 1] = remap(fur[:, 1], -16, 16, 0, 1)
		for fur_vert, weights_vert in zip(fur, self.weights):
			weights_vert.append(("fur_length", fur_vert[0]))
			weights_vert.append(("fur_width", fur_vert[1]))

	@staticmethod
	def quantize_bone_weights(bone_weights):
		# normalize weights so that they sum to 1.0
		sw = sum(bone_weights)
		bone_weights = [x / sw for x in bone_weights]
		# round is essential so the float is not truncated
		bone_weights = list(round(w * 255) for w in bone_weights)
		# additional double check
		d = np.sum(bone_weights) - 255
		bone_weights[0] -= d
		assert np.sum(bone_weights) == 255
		return bone_weights
