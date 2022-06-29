# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import addonHandler
import globalVars
from globalPlugins.zTranslate.lib import psutil
import os
import shutil

def recursive_overwrite(src, dest, ignore=None):
	if os.path.isdir(src):
		if not os.path.isdir(dest):
			os.makedirs(dest)
		files = os.listdir(src)
		if ignore is not None:
			ignored = ignore(src, files)
		else:
			ignored = set()
		for f in files:
			if f not in ignored:
				recursive_overwrite(os.path.join(src, f), os.path.join(dest, f), ignore)
	else:
		shutil.copyfile(src, dest)

def onInstall():
	PROCNAME = "zTranslate-srv.exe"
	for proc in psutil.process_iter():
		if proc.name() == PROCNAME:
			proc.kill()
	configPath = globalVars.appArgs.configPath
	zTranslatepath = os.path.join(configPath, "addons", "zTranslate", "globalPlugins", "zTranslate", "servidor", "modelos")
	zTranslatepathTemp = os.path.join(configPath, "zTranslateTemp")
	if not os.listdir(zTranslatepath): pass
	else: recursive_overwrite(zTranslatepath,zTranslatepathTemp)

