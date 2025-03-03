from source.formats.base.basic import fmt_member
from generated.formats.ovl_base.compound.MemStruct import MemStruct


class TexBufferPc(MemStruct):

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.width = 0
		self.height = 0

		# may be depth
		self.array_size = 0

		# max mip in this buffer
		self.mip_index = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.width = 0
		self.height = 0
		if not (self.context.version == 17):
			self.array_size = 0
		self.mip_index = 0

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
		super().read_fields(stream, instance)
		instance.width = stream.read_ushort()
		instance.height = stream.read_ushort()
		if not (instance.context.version == 17):
			instance.array_size = stream.read_ushort()
		instance.mip_index = stream.read_ushort()

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		stream.write_ushort(instance.width)
		stream.write_ushort(instance.height)
		if not (instance.context.version == 17):
			stream.write_ushort(instance.array_size)
		stream.write_ushort(instance.mip_index)

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
		return f'TexBufferPc [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* width = {fmt_member(self.width, indent+1)}'
		s += f'\n	* height = {fmt_member(self.height, indent+1)}'
		s += f'\n	* array_size = {fmt_member(self.array_size, indent+1)}'
		s += f'\n	* mip_index = {fmt_member(self.mip_index, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
