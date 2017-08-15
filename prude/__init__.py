#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##
import os
import sys
import fnmatch
# Local import
from . import target
from . import tools
from . import debug
from . import module
from . import env
is_init = False

def init():
	global is_init;
	if is_init == True:
		return
	

