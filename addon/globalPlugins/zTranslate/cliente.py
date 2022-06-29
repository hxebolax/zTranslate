# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import os
import sys
dirAddon=os.path.dirname(__file__)
sys.path.append(dirAddon)
sys.path.append(os.path.join(dirAddon, "lib"))
import hmac
import pathlib
#hmac.__path__.append(os.path.join(dirAddon, "lib"))
from multiprocessing.connection import Client
del sys.path[-2:]
from . import ajustes

class Cliente():
	def __init__(self):

		try:
			self.conexion = Client(("localhost", int(ajustes.puerto)), authkey=ajustes.idMaquina)
			self.returnCode = True
			ajustes.IS_Cliente = True
		except Exception as e:
			self.returnCode = False
			ajustes.cliente = None
			ajustes.IS_Cliente = False

	def comando(self, valor):
		try:
			self.conexion.send(valor)
			return self.conexion.recv()
		except Exception as e:
			ajustes.cliente = None
			ajustes.IS_Cliente = False

	def terminar(self):
		try:
			self.conexion.send(["{}closeClient".format(ajustes.idMaquina), ""])
			self.conexion.close()
			ajustes.cliente = None
			ajustes.IS_Cliente = False
		except:
			ajustes.cliente = None
			ajustes.IS_Cliente = False

	def terminarServer(self):
		try:
			self.conexion.send(["{}closeServer".format(ajustes.idMaquina), ""])
			self.conexion.close()
			ajustes.cliente = None
			ajustes.IS_Cliente = False
		except:
			ajustes.cliente = None
			ajustes.IS_Cliente = False
