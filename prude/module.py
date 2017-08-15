#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
import os
import copy
import inspect
import fnmatch
import re
import difflib
# Local import
from . import tools
from . import debug
from . import env
from . import english

generic_cpp_type = [
	"void",
	"float",
	"char",
	"char32_t",
	"int",
	"int8_t",
	"int16_t",
	"int32_t",
	"int64_t",
	"int128_t",
	"uint8_t",
	"uint16_t",
	"uint32_t",
	"uint64_t",
	"uint128_t",
	"const",
	"bool",
	"enum",
	"class",
	"namespace",
	"pragma",
	"struct",
	"NULL",
	"nullptr",
	"sizeof",
	# generic names:
	"openGL",
	"boolean",
	"TODO",
	"todo",
	"vec2",
	"vec3",
	"ivec2",
	"ivec3",
	"uvec2",
	"uvec3",
	"bvec2",
	"bvec3",
	"Edouard",
	"DUPIN"
]

tolerate_words = [
	"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
	"n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
	"min", "max", "fifo", "filo", "ascii",
	# generic variables:
	"iii", "jjj", "kkk", "xxx", "yyy", "zzz",
	"tmp", "it", "val", "pos", "nb",
	
	# classicle programation achronimes:
	"pc", "cpu", "gpio", "io", "proc", "ctrl", "rx", "tx", "msg", "async", "sync", "ack", "src", "freq",
	"ui", "params", "ip", "log", "udp", "tcp", "ftp",
	"unicode", "utf", "xml", "json", "bmp", "jpg", "jpeg", "tga", "gif", "http", "https",
	"sys", "arg", "args", "argc", "argv", "init", "main", "fnmatch", "env", "len", "desc", "str",
	"cmd", "dir", "bsy", "id", 
	#classical libraries
	"lua",
	
	#dxygen element
	"param",
	
	#language word:
	"ifdef", "ifndef","endif", "elif",
	
	# licences:
	"mpl", "bsd", "lgpl", "gpl", 
	
	# units:
	"hz", "khz", "mhz", "thz",
	"ms", "us", "ns", "min", "sec",
	
	# some hewxa values:
	"xf", "xff", "xfff", "xffff", "xfffff", "xffffff",
	"xffffffffull",
	"ll",
	"xll",
	#libc funtions
	"memcpy", "strncpy", "printf", "sprintf", "fopen", "malloc", "calloc", "kalloc",
	"noinline", "ramtext", "constexpr", "typename", "inline", "memet",
]

application_filter = None


def annalyse(filename):
	global application_filter
	debug.info("Annalyse: '" + filename + "'")
	data = tools.file_read_data(filename)
	if application_filter == None:
		application_filter = env.get_local_filter()
	line_id = 0
	number_of_error = 0
	# Annalyse in separate files:
	for line in data.split("\n"):
		# replace all \t with a "    "
		line = re.sub(r'\t',
		              r'    ',
		              line,
		              flags=re.DOTALL)
		# remove the hexa string ==> not able to parse it for now ...
		line = re.sub(r'0(x|X)[0-9a-fA-F]+(ull|ll)?', '', line)
		line_id += 1
		if len(line) == 0:
			continue;
		debug.verbose(filename + ":" + str(line_id) + " " + line)
		# List of all word:
		word_list = []
		current_word = ""
		position_in_line = 0
		start_word_pos = None
		if     len(line) >= 8 \
		   and line[:8] == "#include":
			# remove include handle ==> this is for later ...
			continue
		if     len(line) >= 9 \
		   and line[:9] == "# include":
			# remove include handle ==> this is for later ...
			continue
		if     len(line) >= 2 \
		   and line[:2] == "#!":
			# remove include handle ==> this is for later ...
			continue
		for elem in line:
			position_in_line += 1
			if elem in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_:":
				current_word += elem
				if start_word_pos == None:
					start_word_pos = position_in_line
				# this is to get the last word of the line
				if position_in_line != len(line):
					continue
			if current_word != "":
				# check if not a current Type:
				if current_word in generic_cpp_type:
					word_list.append({
					    "line":line,
					    "line-id":line_id,
					    "pos":start_word_pos,
					    "word":current_word,
					    "word-list":[[0,current_word]],
					    "generic-type":True,
					    "in-namespace":False
					    })
				else:
					# separate with camelCase and snake case:
					under_word_list = []
					current_sub_word = ""
					offset_in_word_count = 0
					offset_in_word = None
					in_namespace = False
					if len(current_word.split("::")) >= 2:
						in_namespace = True
					for elem_word in current_word:
						offset_in_word_count += 1
						if elem_word in "abcdefghijklmnopqrstuvwxyz:":
							current_sub_word += elem_word
							if offset_in_word == None:
								offset_in_word = offset_in_word_count - 1;
						elif elem_word in "0123456789":
							pass
						else:
							if current_sub_word != "":
								if elem_word in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
								   and current_sub_word[-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
									pass
								else:
									while     len(current_sub_word) > 0 \
									      and current_sub_word[-1] == ":":
										current_sub_word = current_sub_word[:-1]
									if current_sub_word != "":
										under_word_list.append([offset_in_word,current_sub_word])
									current_sub_word = ""
									offset_in_word = None
							if elem_word != "_":
								if offset_in_word == None:
									offset_in_word = offset_in_word_count - 1;
								current_sub_word += elem_word
					if current_sub_word != "":
						while     len(current_sub_word) > 0 \
						      and current_sub_word[-1] == ":":
							current_sub_word = current_sub_word[:-1]
						if current_sub_word != "":
							under_word_list.append([offset_in_word,current_sub_word])
					# add at minimal 1 word...
					if len(under_word_list) == 0:
						offset_in_word == 0
						under_word_list.append([offset_in_word,current_sub_word])
					word_list.append({
					    "line":line,
					    "line-id":line_id,
					    "pos":start_word_pos,
					    "word":current_word,
					    "word-list":under_word_list,
					    "generic-type":False,
					    "in-namespace":in_namespace
					    })
				current_word = ""
				start_word_pos = None
		
		
		for elem in word_list:
			debug.extreme_verbose("    " + str(elem["pos"]) + ":" + elem["word"])
			if len(elem["word-list"]) > 1:
				for elem_sub in elem["word-list"]:
					debug.extreme_verbose("    " + str(elem_sub))
					debug.extreme_verbose("    " + str(elem["pos"]) + "+" + str(elem_sub[0]) + ":    " + elem_sub[1])
		
		# check the files:
		for elem in word_list:
			if elem["generic-type"] == True:
				# nothing to parse ==> language basis...
				continue
			if elem["in-namespace"] == True:
				# nothing to parse ==> parse at the definition...
				continue
			if elem["word"] in application_filter[1]:
				# nothing to parse ==> parse at the definition...
				debug.extreme_verbose("reject global names " + elem["word"]);
				continue
			for elem_sub in elem["word-list"]:
				if application_filter[0]["check-capital"]:
					capital = True
					for elemmm in elem_sub[1]:
						if elemmm in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
							pass
						else:
							capital = False
							break
					if capital == True:
						continue
				tmp_elem = elem_sub[1].lower()
				if    len(tmp_elem) == 0 \
				   or tmp_elem == ":" \
				   or tmp_elem == "::":
					continue
				if tmp_elem[-1] == ":":
					if     len(tmp_elem) >= 2 \
					   and tmp_elem[-2] == ":":
						# this is a classicle namespace of C++ ==> just drop it, it might create an error in the namespace declaration
						continue
				if tmp_elem in tolerate_words:
					continue
				if tmp_elem in application_filter[2]:
					continue
				if tmp_elem not in english.list_english_word:
					number_of_error += 1
					debug.print_compilator(filename + ":" + str(elem["line-id"]) + ":error: unknown word: '" + tmp_elem + "'")
					debug.print_compilator("    '" + str(elem["line"]) + "'")
					debug.print_compilator("    " + " "*(elem["pos"]+elem_sub[0]) + "^")
					list_of_words = difflib.get_close_matches(tmp_elem, english.list_english_word)
					if len(list_of_words) != 0:
						debug.print_compilator("                try: " + str(list_of_words))
	if number_of_error != 0:
		debug.warning(filename + " " + str(number_of_error) + " error(s)")
	return number_of_error

