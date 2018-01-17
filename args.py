import re

from collections import OrderedDict
from typing import Any, Optional, Tuple, Sequence
from uniontype import uniontype

# Fun = Callable
# Regex = str
# RegexPattern = type(re.compile(r'.+'))

Token, \
	ShortSwitchToken, \
	LongSwitchToken, \
	IntToken, \
	StringToken \
	\
= uniontype(
	'Token', [
    	('ShortSwitchToken', ['letter']),
    	('LongSwitchToken',  ['name'  ]),
    	('IntToken',         ['value' ]),
    	('StringToken',      ['value' ]),
    ]
)



mapping = OrderedDict([
	 (r'-([a-zA-Z])',   ShortSwitchToken),
	 (r'--([a-zA-Z]+)', LongSwitchToken),
	 (r'([0-9]+)', IntToken),
	 (r'(.+)',     StringToken),
	 # (r'(.*)', UnknownToken),
])

def tokenize_string(string: str) -> Optional[Token]:
	assert len(string) > 0, "Can't tokenize empty string"
	assert '\n' not in string, \
		"Args from sys.argv should not contain newlines. string: {}" \
		.format(string)

	for (regex_str, token_constructor) in mapping.items():
		regex = re.compile(regex_str)
		o_match = re.fullmatch(regex, string)
		if o_match != None:
			text = o_match.groups()[0]
			return token_constructor(text)


def tokenize_args(args: Sequence[str]) -> Sequence[Token]:
	return list(map(tokenize_string, args))



# note: ast doesn't really nest
# so it's not much of a tree...

AST, \
	(String, STRING), \
	(Int,    INT), \
	(NoArgSwitch,   NO_ARG_SWITCH), \
	(OneArgSwitch,  ONE_ARG_SWITCH), \
	(ManyArgSwitch, MANY_ARG_SWITCH) \
	\
= uniontype(
	'AST', [
		('String',  ['value']),
		('Int',     ['value']),
		('NoArgSwitch',   ['name'        ]),
		('OneArgSwitch',  ['name', 'arg' ]),
		('ManyArgSwitch', ['name', 'args']),
	]
  )

# ['--verbosity', '3', '--backup', '-o', 'Episode_1.txt']
#               v
# [('verbosity', 3) ('backup'), ('o')] , ['Episode_1.txt']

switch_id_to_texts = {
	'quiet':     ['q', 'quiet'],
	'verbose':   ['v', 'verbose'],
	'verbosity': ['V', 'vl', 'verbosity'],
	'backup':    ['b', 'backup'],
	'nobackup':  ['n', 'nobackup'],
	'file':      ['f', 'file'],
	'directory': ['d', 'dir', 'directory']
}

text_to_switch_id = { text: id
					  for (id, texts) in switch_id_to_texts.items()
					  	for text in texts } 

assert text_to_switch_id['d']         == 'directory'
assert text_to_switch_id['dir']       == 'directory'
assert text_to_switch_id['directory'] == 'directory'


ArgSpec, \
	(NoArgs,      NO_ARGS), \
	(OptionalArg, OPTIONAL_ARG), \
	(OneArg,      ONE_ARG), \
	(ManyArgs,    MANY_ARGS), \
= uniontype(
	'ArgSpec', [
		('NoArgs',      []),
		('OptionalArg') ['name', 'type']
		('OneArg',      ['name', 'type']),
		('ManyArgs',    ['name', 'type']),
	]
)



switch_id_to_arg_spec = {
	'quiet':     NoArgs(),
	'verbose':   NoArgs(),
	'verbosity': OneArg('level', int),
	'backup':   OptionalArg('directory', str),
	'nobackup': NoArgs(),
	'file':      ManyArgs('file', str),
	'directory': ManyArgs('directory', str),
}

arg_spec_type_to_AST = {
	int: Int,
	str: String,
}

# tokens_to_switches = {
# 	ShortSwitchToken('q'):    NoArgSwitch(name='quiet'),
# 	LongSwitchToken('quiet'): NoArgSwitch(name='quiet'),

# 	ShortSwitchToken('v'):      NoArgSwitch(name='verbose'),
# 	LongSwitchToken('verbose'): NoArgSwitch(name='verbose'),

# 	LongSwitchToken('verbosity'), StringToken(x) -> OneArgSwitch(name='verbosity', arg_and_val=('level', x)),
# }



# Args grammar

# We support many-parameter switches.
# But in a situation like this:
#   > npf --video-extensions avi mp4  videos
# there are two possible interpretations of the cmd-args:
#   > npf --video-extensions (avi mp4 videos) (.)        
#   "run npf in . , only consider files with formats (avi, mp4, videos) video files."
#     
#   > npf --video-extensions (avi mp4 )       (./videos)
#   "run npf in ./videos , only consider files with formats (avi, mp4) video files."
# So the last switch must have known parameter number, exactly 0 or exactly 1.
# 
# Args = 
#     (SwitchAppMaybeManyParameters* SwitchAppKnownParameters)? Literal<String>+
#   | SwitchAppMaybeManyParameters*

# SwitchAppKnownParameters =
# 	  NoArgSwitch
# 	| OneArgSwitch<Type>      Literal<Type>

# SwitchAppPossiblyManyParameters =
# 	  NoArgSwitch
# 	| OptionalArgSwitch<Type> Literal<Type>?
# 	| OneArgSwitch<Type>      Literal<Type>
# 	| ManyArgSwitch<Type>     Literal<Type>+

# checking arg_specs shouldn't be done at the parsing level,
# but after.




# def parse(tokens: Sequence[Token]) -> Sequence[AST]:
# 	ast = []
# 	for token in tokens:
# 		if token.id == 