from source.formats.base.basic import fmt_member
from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember


class Caps2(BasicBitfield):
	reserved_1 = BitfieldMember(pos=0, mask=0x1ff, return_type=int)
	cubemap = BitfieldMember(pos=9, mask=0x200, return_type=int)
	cubemap_pos_x = BitfieldMember(pos=10, mask=0x400, return_type=int)
	cubemap_neg_x = BitfieldMember(pos=11, mask=0x800, return_type=int)
	cubemap_pos_y = BitfieldMember(pos=12, mask=0x1000, return_type=int)
	cubemap_neg_y = BitfieldMember(pos=13, mask=0x2000, return_type=int)
	cubemap_pos_z = BitfieldMember(pos=14, mask=0x4000, return_type=int)
	cubemap_neg_z = BitfieldMember(pos=15, mask=0x8000, return_type=int)
	reserved_2 = BitfieldMember(pos=16, mask=0x1f0000, return_type=int)
	volume = BitfieldMember(pos=21, mask=0x200000, return_type=int)

	def set_defaults(self):
		pass

	def read(self, stream):
		self._value = stream.read_uint()

	def write(self, stream):
		stream.write_uint(self._value)

	@classmethod
	def from_stream(cls, stream, context=None, arg=0, template=None):
		return cls.from_value(stream.read_uint())

	@classmethod
	def to_stream(cls, stream, instance):
		stream.write_uint(instance._value)
