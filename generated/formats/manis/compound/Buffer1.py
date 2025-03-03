from source.formats.base.basic import fmt_member
import numpy
from generated.array import Array
from generated.context import ContextReference
from generated.formats.base.basic import ZString
from generated.formats.base.compound.PadAlign import PadAlign


class Buffer1:

	context = ContextReference()

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		self._context = context
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.bone_hashes = numpy.zeros((self.arg,), dtype=numpy.dtype('uint32'))
		self.bone_names = Array((self.arg,), ZString, self.context, 0, None)

		# ?
		self.bone_pad = PadAlign(self.context, 4, self.bone_names)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.bone_hashes = numpy.zeros((self.arg,), dtype=numpy.dtype('uint32'))
		self.bone_names = Array((self.arg,), ZString, self.context, 0, None)
		self.bone_pad = PadAlign(self.context, 4, self.bone_names)

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
		instance.bone_hashes = stream.read_uints((instance.arg,))
		instance.bone_names = stream.read_zstrings((instance.arg,))
		instance.bone_pad = PadAlign.from_stream(stream, instance.context, 4, instance.bone_names)

	@classmethod
	def write_fields(cls, stream, instance):
		stream.write_uints(instance.bone_hashes)
		stream.write_zstrings(instance.bone_names)
		PadAlign.to_stream(stream, instance.bone_pad)

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
		return f'Buffer1 [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += f'\n	* bone_hashes = {fmt_member(self.bone_hashes, indent+1)}'
		s += f'\n	* bone_names = {fmt_member(self.bone_names, indent+1)}'
		s += f'\n	* bone_pad = {fmt_member(self.bone_pad, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
