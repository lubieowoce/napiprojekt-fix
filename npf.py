import sys
import os
import shutil

from collections import namedtuple

from typing import Any, Dict, Sequence

from npf_utils import (
	default_cmdline_options,
	cmdline_options_to_internal_options,

	SHOULD_BE_FIXED_props,
	file_has_properties_detailed,

	indent,
	impossible,
	IO_,
)


# def o_encode(text: str, encoding) -> Optional[bytes]
# def o_decode(bts: bytes, encoding) -> Optional[str]





# 





def fix_unsafe(text: str) -> str:
	return text.encode('windows-1252').decode('windows-1250')

def fix(text: str) -> str:
	return text \
			.encode('windows-1252', errors='replace') \
			.decode('windows-1250', errors='replace')





def main():
	args = sys.argv[1:]
	print("args: " + str.join(' ', args))

	cmdline_options = default_cmdline_options

	mode    = cmd_args_to_mode(args)
	options = cmdline_options_to_internal_options(cmdline_options)

	print("Working in directory " + os.getcwd())
	print("Mode: " + mode.name)

	if mode.id == MODE_SINGLE_FILE:
		filename = mode.args
		print("Selected file: " + filename)
		print()

		# ****************************
		process_file(filename, options)
		# ****************************

	elif mode.id == MODE_SINGLE_DIR:
		dirname = mode.args
		print("Selected dir: " + dirname)
		dir_item_names = (os.path.join(dirname, name) for name in os.listdir(dirname))
		dir_files = [name for name in dir_item_names if os.path.isfile(name)]

		if len(dir_files) == 0:
			print()
			print("Dir is empty.")
		else:
			print()
			for filename in dir_files:
				# ****************************
				process_file(filename, options)
				# ****************************
				print()

	elif mode.id == MODE_INVALID_ARGS:
		error = mode.args
		print()		
		print(error)

	else:
		impossible("Unrecognized mode: " + str(mode))






def process_file(filename: str, options: Dict[str, Any]) -> IO_[None]:
	should_fix_file, reasons = file_has_properties_detailed(
							   		filename,  SHOULD_BE_FIXED_props,
									options['show_file_processing_reasons'])
	print(filename)
	print(str.join('\n', map(lambda s: indent(s, 4),  reasons) ))

	if should_fix_file:
		print("Fixing " + filename)

		if options['backup']:
			shutil.copy(filename, filename+'.bak')


		# ****************************
		file = open(filename, mode='r+', encoding='utf-8-sig')

		text = file.read()


		fixed = fix(text)


		file.seek(0)
		n_bytes = file.write(fixed)
		file.close()
		# ****************************


		if n_bytes > 0:
			print('Success')
		elif n_bytes == 0:
			print('No bytes written.')
		else:
			print('Error: could not write to file')

	else:
		print("Not fixing.")
		# print("Done.")



Mode = namedtuple("Mode", ["id", "name", "args"])
MODE_SINGLE_FILE = 0; MODE_SINGLE_DIR = 1; MODE_CURRENT_DIR = 2; MODE_INVALID_ARGS = 3; MODE_NPF_ERROR = 4;
ModeSingleFile =  lambda filename: Mode(MODE_SINGLE_FILE,  'single file',       filename)
ModeSingleDir  =  lambda dirname:  Mode(MODE_SINGLE_DIR,   'single directory',  dirname)
# ModeCurrentDir =  lambda:          Mode(MODE_CURRENT_DIR,  'current directory', None)
ModeInvalidArgs = lambda error:    Mode(MODE_INVALID_ARGS, 'invalid args',      error)
ModeNPFError    = lambda error:    Mode(MODE_NPF_ERROR,    'error',             error)


def cmd_args_to_mode(args: Sequence[str]) -> Mode:
	if len(args) == 0:
		mode = ModeSingleDir( os.getcwd() )
	elif len(args) == 1:
		arg = args[0]
		if not os.path.exists(arg):
			mode = ModeInvalidArgs("Error: no such file or directory: " + arg)
		elif os.path.isfile(arg):
			mode = ModeSingleFile(arg)
		elif os.path.isdir(arg):
			mode = ModeSingleDir(arg)
		else:
			mode = ModeNPFError("Unkown error: " + str(args))
	else:
		mode = ModeInvalidArgs("Error: invalid arguments: " + str.join(' ', args))

	return mode





if __name__ == '__main__':
	main()
	