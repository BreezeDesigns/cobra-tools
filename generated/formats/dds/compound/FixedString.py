from source.formats.base.basic import fmt_member
from generated.context import ContextReference


class FixedString:

	"""
	The string "DDS ".
	"""

	context = ContextReference()

	def set_defaults(self):
		pass

	def __init__(self, context, arg=0, template=None):
		self.name = ''
		self._context = context
		# arg is byte count
		self.arg = arg
		self.template = template
		self.data = b""

	def read(self, stream):
		self.read_fields(stream, self)

	def write(self, stream):
		self.write_fields(stream, self)

	def __repr__(self):
		return str(self.data)

	@classmethod
	def read_fields(cls, stream, instance):
		instance.data = stream.read(instance.arg)

	@classmethod
	def write_fields(cls, stream, instance):
		stream.write(instance.data)

	@classmethod
	def from_stream(cls, stream, context, arg=0, template=None):
		instance = cls(context, arg, template)
		cls.read_fields(stream, instance)
		return instance

	@classmethod
	def to_stream(cls, stream, instance):
		cls.write_fields(stream, instance)
		return instance
