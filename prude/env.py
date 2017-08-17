#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

# Local import
from . import debug
import os



force_mode=False

def set_force_mode(val):
	global force_mode
	if val==1:
		force_mode = 1
	else:
		force_mode = 0

def get_force_mode():
	global force_mode
	return force_mode


system_base_name = "prude"

def set_system_base_name(val):
	global system_base_name
	system_base_name = val
	debug.debug("Set basename: '" + str(system_base_name) + "'")

def get_system_base_name():
	global system_base_name
	return system_base_name


prude_root_path = os.path.join(os.getcwd())
if os.path.exists(os.path.join(prude_root_path, "." + get_system_base_name())) == True:
	# all is good ...
	pass
elif os.path.exists(os.path.join(prude_root_path, "..", "." + get_system_base_name())) == True:
	prude_root_path = os.path.join(os.getcwd(), "..")
elif os.path.exists(os.path.join(prude_root_path, "..", "..", "." + get_system_base_name())) == True:
	prude_root_path = os.path.join(os.getcwd(), "..", "..")
elif os.path.exists(os.path.join(prude_root_path, "..", "..", "..", "." + get_system_base_name())) == True:
	prude_root_path = os.path.join(os.getcwd(), "..", "..", "..")
elif os.path.exists(os.path.join(prude_root_path, "..", "..", "..", "..", "." + get_system_base_name())) == True:
	prude_root_path = os.path.join(os.getcwd(), "..", "..", "..", "..")
elif os.path.exists(os.path.join(prude_root_path, "..", "..", "..", "..", "..", "." + get_system_base_name())) == True:
	prude_root_path = os.path.join(os.getcwd(), "..", "..", "..", "..", "..")
elif os.path.exists(os.path.join(prude_root_path, "..", "..", "..", "..", "..", "..", "." + get_system_base_name())) == True:
	prude_root_path = os.path.join(os.getcwd(), "..", "..", "..", "..", "..", "..")
else:
	#debug.error("the root path of " + get_system_base_name() + " must not be upper that 6 parent path")
	pass
prude_path = os.path.join(prude_root_path, "." + get_system_base_name())

def get_local_config_file():
	return prude_path

def file_read_data(path):
	if not os.path.isfile(path):
		return ""
	file = open(path, "r")
	data_file = file.read()
	file.close()
	return data_file

def get_local_filter():
	global capital_letter_check
	capital_letter_check = True
	if os.path.exists(prude_root_path) == False:
		return []
	# parse the global .prude file
	filter_list = [{"check-capital":True}, [], []]
	if os.path.exists(get_local_config_file()) == True:
		data = file_read_data(get_local_config_file())
		for elem in data.split("\n"):
			if elem == "":
				continue
			if elem[0] == "#":
				continue
			if elem[0] == "!":
				# specific control check
				if elem == "!NO_CAPITAL_LETTER":
					filter_list[0]["check-capital"] = False
				elif elem == "!CAPITAL_LETTER":
					filter_list[0]["check-capital"] = True
				else:
					debug.error("unknows parameter: '" + elem + "'")
				continue
			if elem[0] == "+":
				# check the full name:
				filter_list[1].append(elem[1:])
			else:
				filter_list[2].append(elem)
	
	list_files = os.listdir(prude_root_path)
	for ff_file in list_files:
		if    len(ff_file) <= 7 \
		   or ff_file[:7] != ".prude_":
			continue
		debug.debug("Load config file:" + os.path.join(prude_root_path,ff_file))
		data = file_read_data(os.path.join(prude_root_path,ff_file))
		for elem in data.split("\n"):
			if elem == "":
				continue
			if elem[0] == "#":
				continue
			if elem[0] == "!":
				# specific control check
				if elem == "!NO_CAPITAL_LETTER":
					filter_list[0]["check-capital"] = False
				else:
					debug.error("unknows parameter: '" + elem + "'")
				continue
			if elem[0] == "+":
				# check the full name:
				filter_list[1].append(elem[1:])
			else:
				filter_list[2].append(elem)
	debug.verbose("fulllist:" + str(filter_list))
	return filter_list
