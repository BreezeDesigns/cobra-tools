from source.formats.base.basic import fmt_member
import generated.formats.base.basic
import generated.formats.motiongraph.compound.PtrList
import generated.formats.motiongraph.compound.TransStructArray
from generated.formats.ovl_base.compound.MemStruct import MemStruct
from generated.formats.ovl_base.compound.Pointer import Pointer


class Transition(MemStruct):

	"""
	40 bytes
	only used if transition is in 'id'
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.count_0 = 0
		self.count_1 = 0
		self.count_2 = 0
		self.ptr_0 = Pointer(self.context, self.count_1, generated.formats.motiongraph.compound.PtrList.PtrList)
		self.ptr_1 = Pointer(self.context, self.count_2, generated.formats.motiongraph.compound.TransStructArray.TransStructArray)
		self.id = Pointer(self.context, 0, generated.formats.base.basic.ZString)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.count_0 = 0
		self.count_1 = 0
		self.count_2 = 0
		self.ptr_0 = Pointer(self.context, self.count_1, generated.formats.motiongraph.compound.PtrList.PtrList)
		self.ptr_1 = Pointer(self.context, self.count_2, generated.formats.motiongraph.compound.TransStructArray.TransStructArray)
		self.id = Pointer(self.context, 0, generated.formats.base.basic.ZString)

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
		instance.count_0 = stream.read_uint()
		instance.count_1 = stream.read_uint()
		instance.ptr_0 = Pointer.from_stream(stream, instance.context, instance.count_1, generated.formats.motiongraph.compound.PtrList.PtrList)
		instance.count_2 = stream.read_uint64()
		instance.ptr_1 = Pointer.from_stream(stream, instance.context, instance.count_2, generated.formats.motiongraph.compound.TransStructArray.TransStructArray)
		instance.id = Pointer.from_stream(stream, instance.context, 0, generated.formats.base.basic.ZString)
		instance.ptr_0.arg = instance.count_1
		instance.ptr_1.arg = instance.count_2
		instance.id.arg = 0

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		stream.write_uint(instance.count_0)
		stream.write_uint(instance.count_1)
		Pointer.to_stream(stream, instance.ptr_0)
		stream.write_uint64(instance.count_2)
		Pointer.to_stream(stream, instance.ptr_1)
		Pointer.to_stream(stream, instance.id)

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
		return f'Transition [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* count_0 = {fmt_member(self.count_0, indent+1)}'
		s += f'\n	* count_1 = {fmt_member(self.count_1, indent+1)}'
		s += f'\n	* ptr_0 = {fmt_member(self.ptr_0, indent+1)}'
		s += f'\n	* count_2 = {fmt_member(self.count_2, indent+1)}'
		s += f'\n	* ptr_1 = {fmt_member(self.ptr_1, indent+1)}'
		s += f'\n	* id = {fmt_member(self.id, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
