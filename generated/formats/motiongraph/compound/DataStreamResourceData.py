from source.formats.base.basic import fmt_member
import generated.formats.base.basic
from generated.formats.motiongraph.compound.CurveData import CurveData
from generated.formats.ovl_base.compound.MemStruct import MemStruct
from generated.formats.ovl_base.compound.Pointer import Pointer


class DataStreamResourceData(MemStruct):

	"""
	56 bytes
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.curve_type = 0
		self.curve = CurveData(self.context, 0, None)
		self.ds_name = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.type = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.bone_i_d = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.location = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.curve_type = 0
		self.curve = CurveData(self.context, 0, None)
		self.ds_name = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.type = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.bone_i_d = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		self.location = Pointer(self.context, 0, generated.formats.base.basic.ZString)

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
		instance.curve_type = stream.read_uint64()
		instance.ds_name = Pointer.from_stream(stream, instance.context, 0, generated.formats.base.basic.ZString)
		instance.type = Pointer.from_stream(stream, instance.context, 0, generated.formats.base.basic.ZString)
		instance.bone_i_d = Pointer.from_stream(stream, instance.context, 0, generated.formats.base.basic.ZString)
		instance.location = Pointer.from_stream(stream, instance.context, 0, generated.formats.base.basic.ZString)
		instance.curve = CurveData.from_stream(stream, instance.context, 0, None)
		instance.ds_name.arg = 0
		instance.type.arg = 0
		instance.bone_i_d.arg = 0
		instance.location.arg = 0

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		stream.write_uint64(instance.curve_type)
		Pointer.to_stream(stream, instance.ds_name)
		Pointer.to_stream(stream, instance.type)
		Pointer.to_stream(stream, instance.bone_i_d)
		Pointer.to_stream(stream, instance.location)
		CurveData.to_stream(stream, instance.curve)

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
		return f'DataStreamResourceData [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* curve_type = {fmt_member(self.curve_type, indent+1)}'
		s += f'\n	* ds_name = {fmt_member(self.ds_name, indent+1)}'
		s += f'\n	* type = {fmt_member(self.type, indent+1)}'
		s += f'\n	* bone_i_d = {fmt_member(self.bone_i_d, indent+1)}'
		s += f'\n	* location = {fmt_member(self.location, indent+1)}'
		s += f'\n	* curve = {fmt_member(self.curve, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
