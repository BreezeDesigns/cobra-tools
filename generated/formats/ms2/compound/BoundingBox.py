from source.formats.base.basic import fmt_member
import numpy
from generated.context import ContextReference
from generated.formats.ms2.compound.Matrix33 import Matrix33
from generated.formats.ms2.compound.Vector3 import Vector3


class BoundingBox:

	context = ContextReference()

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		self._context = context
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.rotation = Matrix33(self.context, 0, None)

		# center of the box
		self.center = Vector3(self.context, 0, None)

		# total width
		self.extent = Vector3(self.context, 0, None)

		# probably padding
		self.zeros = numpy.zeros((3,), dtype=numpy.dtype('uint32'))
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.rotation = Matrix33(self.context, 0, None)
		self.center = Vector3(self.context, 0, None)
		self.extent = Vector3(self.context, 0, None)
		if self.context.version == 32:
			self.zeros = numpy.zeros((3,), dtype=numpy.dtype('uint32'))

	def read(self, stream):
		self.io_start = stream.tell()
		self.read_fields(stream, self)
		self.io_size = stream.tell() - self.io_start

	def write(self, stream):
		self.io_start = stream.tell()
		self.write_fields(stream, self)
		self.io_size = stream.tell() - self.io_start

	@classmethod
	def read_fields(cls, stream, instance):
		instance.rotation = Matrix33.from_stream(stream, instance.context, 0, None)
		instance.center = Vector3.from_stream(stream, instance.context, 0, None)
		instance.extent = Vector3.from_stream(stream, instance.context, 0, None)
		if instance.context.version == 32:
			instance.zeros = stream.read_uints((3,))

	@classmethod
	def write_fields(cls, stream, instance):
		Matrix33.to_stream(stream, instance.rotation)
		Vector3.to_stream(stream, instance.center)
		Vector3.to_stream(stream, instance.extent)
		if instance.context.version == 32:
			stream.write_uints(instance.zeros)

	@classmethod
	def from_stream(cls, stream, context, arg=0, template=None):
		instance = cls(context, arg, template, set_default=False)
		instance.io_start = stream.tell()
		cls.read_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start
		return instance

	@classmethod
	def to_stream(cls, stream, instance):
		instance.io_start = stream.tell()
		cls.write_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start
		return instance

	def get_info_str(self, indent=0):
		return f'BoundingBox [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += f'\n	* rotation = {fmt_member(self.rotation, indent+1)}'
		s += f'\n	* center = {fmt_member(self.center, indent+1)}'
		s += f'\n	* extent = {fmt_member(self.extent, indent+1)}'
		s += f'\n	* zeros = {fmt_member(self.zeros, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
