
from collections import namedtuple
from typing import Any, Optional, Sequence, Tuple, List, Callable
from functools import partial

Fun = Callable






def uniontype(type_name: str, variant_specs: List[ Tuple[str, List[str]] ],
			  allow_no_constructors=False                             ) -> List[Any]:
	"""
	Analogous to the namedtuple function.


	Creating a type:

	Example: Foo{ r } | Bar{ x, y } | BazBaz {}
    - Foo has one attribute r,
    - Bar has two attributes x, y
    - BazBaz has no attributes

	>>> Example, \
		Foo, \
		Bar, \
		BazBaz, \
		\
		= uniontype(
			'Example', [
				 ('Foo',    ['r'     ]),
				 ('Bar',    ['x', 'y']),
				 ('BazBaz', [        ]),
			]
		  )
	>>> x  = Foo(5);    y  = Bar(2, 4);      z  = BazBaz()
	>>> x2 = Foo(r=5);  y2 = Bar(x=2, y=4);  z2 = BazBaz()
	>>>
	>>> x == x2  and  y == y2  and  z == z2
	True
	>>> type(x) == Example  and  type(y) == Example  and  type(z) == Example
	True
	>>>

	Pattern matching

	>>> a = Bar(1, 5)
	>>> if   a.is_Foo():
	>>>     r, = a.val
	>>> 	print('a is a Foo')
	>>> elif a.is_Bar():
	>>> 	x, y = a.val
	>>>     print('a is a Bar')
	>>> elif a.is_BazBaz():
	>>> 	print('a is a BazBaz')


a = Bar(1, 5)
if   a.is_Foo():
    r, = a.val
	print('a is a Foo')
elif a.is_Bar():
	x, y = a.val
    print('a is a Bar')
elif a.is_BazBaz():
	print('a is a BazBaz')

	"""
	if not allow_no_constructors and len(variant_specs) == 0:
		raise Exception("No variants specified for " + type_name)

	UserUnionType = namedtuple(type_name, ['id__', 'val__'])

	variant_names     = [name      for (name, val_names) in variant_specs]
	variant_attr_names = [val_names for (name, val_names) in variant_specs]
	variant_ids = range(len(variant_names))
	
	# string representation
	def __str__(x: UserUnionType):
		if x.id__ not in variant_ids:
			raise Exception("Illegal variant: Token(id={id}, val={val})"\
							 .format(**x._asdict()))
			

		for (variant_id, variant_name) in zip(variant_ids, variant_names):
			if x.id__ == variant_id:
				this_variant_attr_names = variant_attr_names[variant_id]
				attr_reprs = (name + '=' + value.__repr__()  for (name, value) in zip(this_variant_attr_names, x.val__))
				all_attrs_repr = str.join(', ', attr_reprs)
				return variant_name + '(' + all_attrs_repr + ')'

	UserUnionType.__str__ = __str__
	UserUnionType.__repr__ = __str__




	# add is_VariantName methods to UserUnionType

	def make_is_variant_name(variant_id):
		def is_variant_name(obj) -> bool:
			return obj.id__ == variant_id
		return is_variant_name

	for (variant_id, variant_name) in zip(variant_ids, variant_names):
		setattr(UserUnionType, ('is_' + variant_name), make_is_variant_name(variant_id))


	# add attribute getters for each Variant's val_names

	def make_variant_attr_name_property(variant_id, variant_name, attr_name):
		@property
		def attr_name_property(obj):
			if obj.id__ != variant_id:
				raise AttributeError("{type_name}.{variant_name} object has no attribute {attr_name}"\
							          .format(type_name=type_name, variant_name=variant_name, attr_name=attr_name))

			return getattr(obj.val__, attr_name)

		return attr_name_property

	for (variant_id, (variant_name, attr_names)) in zip(variant_ids, variant_specs):
		for attr_name in attr_names:
			setattr(UserUnionType, attr_name,
				    make_variant_attr_name_property(variant_id, variant_name, attr_name))


	# constructors

	def make_constructor(variant_id: int, variant_name: str, attr_names: List[str]):
		assert type(variant_id) == int and type(variant_name) == str and type(attr_names) == list
		# Each variant gets a VariantNameVal namedtuple to store the values
		backing_tuple_constructor = namedtuple(variant_name+"Val", attr_names)

		def constructor(*args, **kwargs):
			# error checking
			if len(attr_names) != len(args)+len(kwargs):
				raise Exception(type_name +'.'+variant_name + "'s constructor expected {e} args, got {g} "\
							     .format(e=len(attr_names), g=len(args)+len(kwargs)))
			for name in kwargs.keys():
				if name not in attr_names:
					raise Exception(type_name +'.'+variant_name + "'s constructor got unexpected keyword argument '{n}'" \
									 .format(n=name))
			# actual constructor
			return UserUnionType(id__=variant_id, val__=backing_tuple_constructor(*args, **kwargs))

		return constructor

	constructors = [make_constructor(variant_id, variant_name, attr_names)
					for (variant_id, (variant_name, attr_names) )  # correct, even though some syntax highlighters don't think so
					in zip(variant_ids, variant_specs)                     ]

	# add the constructors to the created union type so the user can write TypeName.VariantName(foo, bar)
	for (variant_name, constructor) in zip(variant_names, constructors):
		setattr(UserUnionType, variant_name, constructor)


	
	UserUnionType.is_same_variant = lambda obj1, obj2: obj1.id__ == obj2.id__
	UserUnionType.get_variant_name = lambda obj: variant_names[obj.id__]

	UserUnionType.as_tuple = lambda obj: tuple(obj.val__)
	UserUnionType.get_values = UserUnionType.as_tuple

	# reexport nameduple methods under different names
	UserUnionType.as_dict  = lambda obj: obj.val__._asdict()
	UserUnionType.replace  = lambda obj, **kwargs: obj._replace(val__=obj.val__._replace(**kwargs))
	# UserUnionType.__iter__ = lambda obj: obj.val__.__iter__() # can't do this - it breaks namedtuple's _asdict(), _replace(), _make(), and others
	# use as_tuple and iter over that instead.

	return [UserUnionType] + constructors




Example, \
		Foo,\
		Bar,\
		BazBaz, \
\
= uniontype(
	'Example', [
		 ('Foo',    ['r'     ]),
		 ('Bar',    ['x', 'y']),
		 ('BazBaz', [        ]),
	]
  )




# Token = namedtuple('Token', ['id', 'val'])
# STRING_TOKEN = 0; SHORT_SWITCH_TOKEN = 1; LONG_SWITCH_TOKEN = 2; # UNKNOWN_TOKEN = 3;
# StringToken      = lambda value:         Token(STRING_TOKEN,       value)
# ShortSwitchToken = lambda switch_letter: Token(SHORT_SWITCH_TOKEN, switch_letter)
# LongSwitchToken  = lambda switch_name:   Token(LONG_SWITCH_TOKEN,  switch_name)
# # UnknownToken     = lambda text:          Token(UNKNOWN_TOKEN,      text)
# def Token_str(token: Token) -> str:
# 	assert token.id in [STRING_TOKEN, SHORT_SWITCH_TOKEN, LONG_SWITCH_TOKEN], \
# 		"Illegal token type: Token(id={id}, val={val})".format(**token._asdict())

# 	if token.id   == STRING_TOKEN:
# 		return 'StringToken({})'.format(token.val.__repr__())
# 	elif token.id == SHORT_SWITCH_TOKEN:
# 		return 'ShortSwitchToken({})'.format(token.val.__repr__())
# 	elif token.id == LONG_SWITCH_TOKEN:
# 		return 'LongSwitchToken({})'.format(token.val.__repr__())