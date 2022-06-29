# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import addonHandler
from random import choice
import socket
import uuid
import os
import sys
dirAddon=os.path.dirname(__file__)
sys.path.append(dirAddon)
sys.path.append(os.path.join(dirAddon, "lib"))
import psutil
del sys.path[-2:]

def id_maquina():
	return str(uuid.uuid1(uuid.getnode(),0))[24:]

def procesoCHK(proceso):
	return proceso in (p.name() for p in psutil.process_iter())

def puertoUsado(puerto: int) -> bool:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		return s.connect_ex(('localhost', puerto)) == 0

def obtenPuerto():
	bandera = True
	while bandera:
		puerto = choice([i for i in range(49152, 65535) if i not in []])
		if puertoUsado(puerto):
			pass
		else:
			bandera = False
	return puerto

def chkInternet(host="8.8.8.8", port=53, timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except socket.error as ex:
		return False

def borraDuplicadosLista(lista):
	return list(dict.fromkeys(lista))


def limpiaLista(lista):
	resultado = []
	for i in lista:
		x = i.lstrip().rstrip()
		if x == "Traducción activada.":
			pass
		elif x == "en blanco":
			pass
		else:
			resultado.append(x)
	return resultado