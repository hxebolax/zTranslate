# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import addonHandler
import config
import globalVars
from collections import deque
import os
import json
import shutil
from . import idiomas

addonHandler.initTranslation()

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

# Comprueba si hay temporales
configPath = globalVars.appArgs.configPath
zTranslatepathTemp = os.path.join(configPath, "zTranslateTemp")
zTranslatepath = os.path.join(configPath, "addons", "zTranslate", "globalPlugins", "zTranslate", "servidor", "modelos")
if os.path.isdir(zTranslatepathTemp):
	for filename in os.listdir(zTranslatepath):
		file_path = os.path.join(zTranslatepath, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			pass
	recursive_overwrite(zTranslatepathTemp, zTranslatepath)
	try:
		shutil.rmtree(zTranslatepathTemp, ignore_errors=True)
	except:
		pass

# Historial
historialOrigen = deque(maxlen=500)
historialDestino = deque(maxlen=500)

# Banderas de control
IS_WinON = False
IS_Cliente = False
IS_Reinicio = False
IS_Sonido = False

# Variables para conexión del cliente con servidor
idMaquina = None
puerto = None
cliente = None

# Variables de lenguaje
# choiceLenguajes lista anidada: 0 idiomas origen, 1 idiomas destino, 2 idiomas en inglés, 3 directorios donde estan instalados los idiomas 
choiceLenguajes = [[],[],[],[]]
lenguajes = idiomas.diccionario_lenguajes
lenguajesEN = idiomas.diccionario_lenguajesEN
with open(os.path.join(os.path.dirname(__file__), "datos.json")) as f:
	dbDatos = json.load(f) # datos en local de los idiomas que se pueden descargar del servidor de Argos
indiceLangOrigen = 0
indiceLangDestino = 0

# Variables del traductor
_translationCache = {}
_nvdaSpeak = None
_nvdaGetPropertiesSpeech = None
_enableTranslation = False
_lastTranslatedText = None

# Configuración nvda.ini
def initConfiguration():
	confspec = {
		"langOrigen": "string(default='0')",
		"langDestino": "string(default='0')",
		"autodetect": "boolean(default=False)",
		"cache": "boolean(default=True)",
	}
	config.conf.spec['zTranslate'] = confspec

def getConfig(key):
	return config.conf["zTranslate"][key]

def setConfig(key, value):
	try:
		config.conf.profiles[0]["zTranslate"][key] = value
	except:
		config.conf["zTranslate"][key] = value

choiceLangOrigen = None
choiceLangDestino = None
chkAutoDetect = None
chkCache = None

def setup():
	global choiceLangOrigen, choiceLangDestino, chkAutoDetect, chkCache
	initConfiguration()
	choiceLangOrigen = getConfig("langOrigen")
	choiceLangDestino = getConfig("langDestino")
	chkAutoDetect = getConfig("autodetect")
	chkCache = getConfig("cache")

def guardaConfiguracion():
	setConfig("langOrigen", choiceLangOrigen)
	setConfig("langDestino", choiceLangDestino)
	setConfig("autodetect", chkAutoDetect)
	setConfig("cache", chkCache)
