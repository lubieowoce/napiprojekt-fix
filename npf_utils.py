import os # getcwd
		  # os.path - exists, isdir, isfile
from typing import Any, Tuple, Sequence, Dict, Generic, TypeVar
A = TypeVar('A')
class IO_(Generic[A]):
	pass

from collections import namedtuple
from functools import partial
# from either import Either, Left, right



WINDOWS_DEFAULT = 'windows-1252'
EASTERN_EUROPE = 'windows-1250'

polish_lower_chars      = set('ąćęłńóśźż')
polish_upper_safe_chars = set('ĄĆĘŁŃÓŚŹŻ') - set('Ź')  # without 'Ź', which doesn't work
polish_chars = polish_lower_chars | polish_upper_safe_chars

misdecoded_polish_chars = { ch.encode(EASTERN_EUROPE).decode(WINDOWS_DEFAULT) for ch in polish_chars }

polish_chars_no_dup            = polish_chars - misdecoded_polish_chars # remove duplicates like 'ó'
misdecoded_polish_chars_no_dup = misdecoded_polish_chars - polish_chars # remove duplicates like 'ó'




def impossible(error_text):
	raise Exception("Internal error: " + error_text)


def any_in(xs: Sequence[A], needles: Sequence[A]) -> bool:
# def any_in(xs, needles) -> bool:
	if len(xs) == 0:
		return False

	if type(needles) != set:
		needles = set(needles)

	any_needle_found = False
	for x in xs:
		if x in needles:
			any_needle_found = True
			break
	return any_needle_found

def no_in(xs: Sequence[A], needles: Sequence[A]) -> bool:
	return not any_in(xs, needles)




# ===== Text Properties ======


TextProperty = namedtuple('TextProperty', ['true_text', 'false_text', 'pred'])


# IS_POLISH_TEXT = TextProperty('is a polish text',
# 							  'is not a polish text',
# 							  lambda text: any_in(text, polish_chars_no_dup) )
							  # we permit some symbols from `misdecoded`, like the pound symbol)
IS_MISDECODED_POLISH_TEXT = TextProperty('is a misdecoded polish text',
										 'is not a misdecoded polish text',
										 (lambda text: any_in(text, misdecoded_polish_chars_no_dup) \
										 			   and no_in(text, polish_chars_no_dup)           ) )



# ===== File Properties =====
video_exts    = set(['mp4', 'avi', 'mkv', 'rmvb', 'xvid'])
subtitle_exts = set(['txt', 'srt', 'sub', 'mpl'])


def file_contents(filename: str) -> IO_[str]:
	with open(filename, mode='r', encoding='utf-8-sig') as file:
		return file.read()

def file_ext(filename: str) -> str:
	name, dot_ext = os.path.splitext(filename)
	return dot_ext[1:]

def chain(*fs):
	"""
	returns a function that applies `fs` left to right.
	chain(f, g, h) == lambda x: h(g(f(x)))
	(reverse order than standard function composition)
	"""
	def chained(x):
		res = x
		for f in fs:
			res = f(res)
		return res
	return chained



FileProperty = namedtuple('FileProperty', ['true_text', 'false_text', 'pred'])



def text_prop_to_file_prop(tprop: TextProperty) -> FileProperty:
	return FileProperty (
		       tprop.true_text.replace('text', 'file'),
		       tprop.false_text.replace('text', 'file'),
		       chain(file_contents, tprop.pred)
		   )


IS_MISDECODED_POLISH_FILE = text_prop_to_file_prop(IS_MISDECODED_POLISH_TEXT)

# IS_POLISH_FILE = text_prop_to_file_prop(IS_POLISH_TEXT)


# os.path.abspath(path) # 
# os.path.exists(path)
# os.path.join


IS_SUBTITLE_FILE =  FileProperty(
	'is a subtitle file',
	'is not a subtitle file',
	lambda filename: file_ext(filename) in subtitle_exts
)

SHOULD_BE_FIXED_props = [IS_SUBTITLE_FILE, IS_MISDECODED_POLISH_FILE]
# def file_property_and(prop1: FileProperty, prop2: FileProperty) -> FileProperty:
# 	return FileProperty(
# 		prop1.name + ' and ' + prop2.name,
# 		lambda x: prop1.pred(x) and prop2.pred(x)
# 	)




# # def file_property_all(props: Sequence[FileProperty]) -> FileProperty:
# def file_property_all(props) -> FileProperty:
# 	return reduce(file_property_and, props)


ReasonOption = namedtuple("ReasonOption", ['id', 'name'])
AllReasons        = ReasonOption(0, 'all reasons')
ReasonsWhyOnly    = ReasonOption(2, 'only reasons why')
ReasonsWhyNotOnly = ReasonOption(1, 'only reasons why not')
NoReasons         = ReasonOption(3, 'no reasons')

# def file_has_properties(filename: str, props: Sequence[FileProperty]) -> bool:
def file_has_properties_detailed(filename: str, props: Sequence[FileProperty], reason_opt: ReasonOption) -> Tuple[bool, Sequence[str]]:
	pred_results = [prop.pred(filename) for prop in props]
	all_true = all(pred_results)

	if reason_opt == AllReasons:
		reasons = [ prop.true_text if prop_is_true else prop.false_text
					for (prop, prop_is_true) in zip(props, pred_results) ]
		return (all_true, reasons)

	elif reason_opt == ReasonsWhyOnly:
		reasons = [ prop.true_text
					for (prop, prop_is_true) in zip(props, pred_results) if prop_is_true ]
		return (all_true, reasons)

	elif reason_opt == ReasonsWhyNotOnly:
		reasons = [ prop.false_text
					for (prop, prop_is_true) in zip(props, pred_results) if not prop_is_true ]
		return (all_true, reasons)

	elif reason_opt == NoReasons:
		return (all_true, [])

	else:
		impossible("Invalid reason_opt: " + str(reason_opt))
	




default_cmdline_options = {
	'verbosity': 2,
	'backup': True,
}

# opts_mapping = {
# 	OptionVerbose: {'file_property_reporting': AllReasons},
# } 
def cmdline_options_to_internal_options(cmdline_options: Dict[str, Any]) -> Dict[str, Any]:
	opts = {}
	assert 'verbosity' in cmdline_options
	verbosity = cmdline_options['verbosity']
	if verbosity == 0:
		opts['show_file_processing_reasons'] = NoReasons
	elif verbosity == 1:
		opts['show_file_processing_reasons'] = ReasonsWhyNotOnly
	elif verbosity == 2:
		opts['show_file_processing_reasons'] = AllReasons
	else:
		impossible("unknown verbosity: " + str(cmdline_options['verbosity']))

	assert 'backup' in cmdline_options
	opts['backup'] = cmdline_options['backup']

	return opts





# def find_files_to_fix(dirname: str) -> Sequence[str]:
# 	dir_contents = os.listdir(dirname)
# 	return list(lambda filename: filter(SHOULD_BE_FIXED.pred, dir_contents))
# === Accompanying videos ===


IS_VIDEO_FILE =  FileProperty(
	'is a video file',
	'is not a video file',
	lambda filename: file_ext(filename) in video_exts
)


def has_accompanying_video_in_dir(filename: str, dirname: str) -> bool:
	episode_name, dot_ext = os.path.splitext(filename)
	return any( os.path.exists(os.path.join(dirname, episode_name + '.' + format))
				for format in video_exts )

get_HAS_ACCOMPANYING_VIDEO = \
	lambda dirname: \
		FileProperty(
			'has_accompanying_video',
			partial(has_accompanying_video_in_dir, dirname=dirname)
		)





def indent(string: str, indent: int) -> str:
	indent_n = indent
	assert indent_n > 0, "Indent value must be nonnegative (is {})".format(indent_n)
	return ' ' * indent_n + string






# pl = 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'
# en = 'acelnoszzACELNOSZZ'
# pl_to_en_map = {ord(pl_ch): ord(en_ch) for (pl_ch, en_ch) in zip(pl, en)}

# def to_ascii(s: str) -> str:
# 	return s \
# 			.translate(pl_to_en_map) \
# 			.encode('ascii', errors='replace') \
# 			.decode('ascii')