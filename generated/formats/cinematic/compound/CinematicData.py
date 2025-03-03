from source.formats.base.basic import fmt_member
import generated.formats.base.basic
import generated.formats.cinematic.compound.State
from generated.formats.ovl_base.compound.ArrayPointer import ArrayPointer
from generated.formats.ovl_base.compound.MemStruct import MemStruct
from generated.formats.ovl_base.compound.Pointer import Pointer


class CinematicData(MemStruct):

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.next_level_count = 0
		self.default_name = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.next_levels = ArrayPointer(self.context, self.next_level_count, generated.formats.cinematic.compound.State.State)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.next_level_count = 0
		self.default_name = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.next_levels = ArrayPointer(self.context, self.next_level_count, generated.formats.cinematic.compound.State.State)

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
		instance.default_name = Pointer.from_stream(stream, instance.context, 0, generated.formats.base.basic.ZString)
		instance.next_levels = ArrayPointer.from_stream(stream, instance.context, instance.next_level_count, generated.formats.cinematic.compound.State.State)
		instance.next_level_count = stream.read_uint64()
		instance.default_name.arg = 0
		instance.next_levels.arg = instance.next_level_count

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Pointer.to_stream(stream, instance.default_name)
		ArrayPointer.to_stream(stream, instance.next_levels)
		stream.write_uint64(instance.next_level_count)

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
		return f'CinematicData [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* default_name = {fmt_member(self.default_name, indent+1)}'
		s += f'\n	* next_levels = {fmt_member(self.next_levels, indent+1)}'
		s += f'\n	* next_level_count = {fmt_member(self.next_level_count, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
