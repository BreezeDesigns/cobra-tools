from source.formats.base.basic import fmt_member
from generated.context import ContextReference
from generated.formats.bnk.compound.MusicTrackInitialValues import MusicTrackInitialValues


class MusicTrack:

	context = ContextReference()

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		self._context = context
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# seen 114
		self.length = 0
		self.id = 0
		self.data = MusicTrackInitialValues(self.context, 0, None)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.length = 0
		self.id = 0
		self.data = MusicTrackInitialValues(self.context, 0, None)

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
		instance.length = stream.read_uint()
		instance.id = stream.read_uint()
		instance.data = MusicTrackInitialValues.from_stream(stream, instance.context, 0, None)

	@classmethod
	def write_fields(cls, stream, instance):
		stream.write_uint(instance.length)
		stream.write_uint(instance.id)
		MusicTrackInitialValues.to_stream(stream, instance.data)

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
		return f'MusicTrack [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += f'\n	* length = {fmt_member(self.length, indent+1)}'
		s += f'\n	* id = {fmt_member(self.id, indent+1)}'
		s += f'\n	* data = {fmt_member(self.data, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
