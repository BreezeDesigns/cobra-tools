from source.formats.base.basic import fmt_member
import generated.formats.specdef.compound.DataPtr
import generated.formats.specdef.compound.PtrList
import generated.formats.specdef.enum.SpecdefDtype
from generated.formats.ovl_base.compound.ArrayPointer import ArrayPointer
from generated.formats.ovl_base.compound.ForEachPointer import ForEachPointer
from generated.formats.ovl_base.compound.MemStruct import MemStruct
from generated.formats.ovl_base.compound.Pointer import Pointer


class SpecdefRoot(MemStruct):

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.attrib_count = 0
		self.flags = 0
		self.name_count = 0
		self.childspec_count = 0
		self.manager_count = 0
		self.script_count = 0
		self.attrib_dtypes = ArrayPointer(self.context, self.attrib_count, generated.formats.specdef.enum.SpecdefDtype.SpecdefDtype)
		self.attrib_names = Pointer(self.context, self.attrib_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.attrib_datas = ForEachPointer(self.context, self.attrib_dtypes, generated.formats.specdef.compound.DataPtr.DataPtr)
		self.names = Pointer(self.context, self.name_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.childspecs = Pointer(self.context, self.childspec_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.managers = Pointer(self.context, self.manager_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.scripts = Pointer(self.context, self.script_count, generated.formats.specdef.compound.PtrList.PtrList)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.attrib_count = 0
		self.flags = 0
		self.name_count = 0
		self.childspec_count = 0
		self.manager_count = 0
		self.script_count = 0
		self.attrib_dtypes = ArrayPointer(self.context, self.attrib_count, generated.formats.specdef.enum.SpecdefDtype.SpecdefDtype)
		self.attrib_names = Pointer(self.context, self.attrib_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.attrib_datas = ForEachPointer(self.context, self.attrib_dtypes, generated.formats.specdef.compound.DataPtr.DataPtr)
		self.names = Pointer(self.context, self.name_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.childspecs = Pointer(self.context, self.childspec_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.managers = Pointer(self.context, self.manager_count, generated.formats.specdef.compound.PtrList.PtrList)
		self.scripts = Pointer(self.context, self.script_count, generated.formats.specdef.compound.PtrList.PtrList)

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
		instance.attrib_count = stream.read_ushort()
		instance.flags = stream.read_ushort()
		instance.name_count = stream.read_ubyte()
		instance.childspec_count = stream.read_ubyte()
		instance.manager_count = stream.read_ubyte()
		instance.script_count = stream.read_ubyte()
		instance.attrib_dtypes = ArrayPointer.from_stream(stream, instance.context, instance.attrib_count, generated.formats.specdef.enum.SpecdefDtype.SpecdefDtype)
		instance.attrib_names = Pointer.from_stream(stream, instance.context, instance.attrib_count, generated.formats.specdef.compound.PtrList.PtrList)
		instance.attrib_datas = ForEachPointer.from_stream(stream, instance.context, instance.attrib_dtypes, generated.formats.specdef.compound.DataPtr.DataPtr)
		instance.names = Pointer.from_stream(stream, instance.context, instance.name_count, generated.formats.specdef.compound.PtrList.PtrList)
		instance.childspecs = Pointer.from_stream(stream, instance.context, instance.childspec_count, generated.formats.specdef.compound.PtrList.PtrList)
		instance.managers = Pointer.from_stream(stream, instance.context, instance.manager_count, generated.formats.specdef.compound.PtrList.PtrList)
		instance.scripts = Pointer.from_stream(stream, instance.context, instance.script_count, generated.formats.specdef.compound.PtrList.PtrList)
		instance.attrib_dtypes.arg = instance.attrib_count
		instance.attrib_names.arg = instance.attrib_count
		instance.attrib_datas.arg = instance.attrib_dtypes
		instance.names.arg = instance.name_count
		instance.childspecs.arg = instance.childspec_count
		instance.managers.arg = instance.manager_count
		instance.scripts.arg = instance.script_count

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		stream.write_ushort(instance.attrib_count)
		stream.write_ushort(instance.flags)
		stream.write_ubyte(instance.name_count)
		stream.write_ubyte(instance.childspec_count)
		stream.write_ubyte(instance.manager_count)
		stream.write_ubyte(instance.script_count)
		ArrayPointer.to_stream(stream, instance.attrib_dtypes)
		Pointer.to_stream(stream, instance.attrib_names)
		ForEachPointer.to_stream(stream, instance.attrib_datas)
		Pointer.to_stream(stream, instance.names)
		Pointer.to_stream(stream, instance.childspecs)
		Pointer.to_stream(stream, instance.managers)
		Pointer.to_stream(stream, instance.scripts)

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
		return f'SpecdefRoot [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* attrib_count = {fmt_member(self.attrib_count, indent+1)}'
		s += f'\n	* flags = {fmt_member(self.flags, indent+1)}'
		s += f'\n	* name_count = {fmt_member(self.name_count, indent+1)}'
		s += f'\n	* childspec_count = {fmt_member(self.childspec_count, indent+1)}'
		s += f'\n	* manager_count = {fmt_member(self.manager_count, indent+1)}'
		s += f'\n	* script_count = {fmt_member(self.script_count, indent+1)}'
		s += f'\n	* attrib_dtypes = {fmt_member(self.attrib_dtypes, indent+1)}'
		s += f'\n	* attrib_names = {fmt_member(self.attrib_names, indent+1)}'
		s += f'\n	* attrib_datas = {fmt_member(self.attrib_datas, indent+1)}'
		s += f'\n	* names = {fmt_member(self.names, indent+1)}'
		s += f'\n	* childspecs = {fmt_member(self.childspecs, indent+1)}'
		s += f'\n	* managers = {fmt_member(self.managers, indent+1)}'
		s += f'\n	* scripts = {fmt_member(self.scripts, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
