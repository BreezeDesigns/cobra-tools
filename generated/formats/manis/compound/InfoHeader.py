from source.formats.base.basic import fmt_member
from generated.array import Array
from generated.formats.base.basic import ZString
from generated.formats.manis.compound.Buffer1 import Buffer1
from generated.formats.manis.compound.KeysReader import KeysReader
from generated.formats.manis.compound.ManiInfo import ManiInfo
from generated.formats.manis.compound.SizedStrData import SizedStrData
from generated.formats.ovl_base.compound.GenericHeader import GenericHeader


class InfoHeader(GenericHeader):

	"""
	Custom header struct
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.mani_count = 0
		self.names = Array((self.mani_count,), ZString, self.context, 0, None)
		self.header = SizedStrData(self.context, 0, None)
		self.mani_infos = Array((self.mani_count,), ManiInfo, self.context, 0, None)
		self.name_buffer = Buffer1(self.context, int(self.header.hash_block_size / 4), None)
		self.keys_buffer = KeysReader(self.context, self.mani_infos, None)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.mani_count = 0
		self.names = Array((self.mani_count,), ZString, self.context, 0, None)
		self.header = SizedStrData(self.context, 0, None)
		self.mani_infos = Array((self.mani_count,), ManiInfo, self.context, 0, None)
		self.name_buffer = Buffer1(self.context, int(self.header.hash_block_size / 4), None)
		self.keys_buffer = KeysReader(self.context, self.mani_infos, None)

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
		instance.mani_count = stream.read_uint()
		instance.names = stream.read_zstrings((instance.mani_count,))
		instance.header = SizedStrData.from_stream(stream, instance.context, 0, None)
		instance.mani_infos = Array.from_stream(stream, (instance.mani_count,), ManiInfo, instance.context, 0, None)
		instance.name_buffer = Buffer1.from_stream(stream, instance.context, int(instance.header.hash_block_size / 4), None)
		instance.keys_buffer = KeysReader.from_stream(stream, instance.context, instance.mani_infos, None)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		stream.write_uint(instance.mani_count)
		stream.write_zstrings(instance.names)
		SizedStrData.to_stream(stream, instance.header)
		Array.to_stream(stream, instance.mani_infos, (instance.mani_count,), ManiInfo, instance.context, 0, None)
		Buffer1.to_stream(stream, instance.name_buffer)
		KeysReader.to_stream(stream, instance.keys_buffer)

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
		return f'InfoHeader [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* mani_count = {fmt_member(self.mani_count, indent+1)}'
		s += f'\n	* names = {fmt_member(self.names, indent+1)}'
		s += f'\n	* header = {fmt_member(self.header, indent+1)}'
		s += f'\n	* mani_infos = {fmt_member(self.mani_infos, indent+1)}'
		s += f'\n	* name_buffer = {fmt_member(self.name_buffer, indent+1)}'
		s += f'\n	* keys_buffer = {fmt_member(self.keys_buffer, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
