# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import addonHandler
import urllib.request
import socket
import zipfile
import os
import wx
import time
from threading import Thread
import shutil
from . import ajustes

addonHandler.initTranslation()

class HiloDescarga(Thread):
	def __init__(self, frame, idiomas, urls):
		super(HiloDescarga, self).__init__()

		self.frame = frame
		self.idiomas = idiomas
		self.urls = urls
		self.tiempo = 30

		self.dirModelos = os.path.join(os.path.dirname(__file__), "servidor", "modelos")
		self.idiomaActual = ""
		self.daemon = True
		self.start()

	def humanbytes(self, B): # Convierte bytes
		B = float(B)
		KB = float(1024)
		MB = float(KB ** 2) # 1,048,576
		GB = float(KB ** 3) # 1,073,741,824
		TB = float(KB ** 4) # 1,099,511,627,776

		if B < KB:
			return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
		elif KB <= B < MB:
			return '{0:.2f} KB'.format(B/KB)
		elif MB <= B < GB:
			return '{0:.2f} MB'.format(B/MB)
		elif GB <= B < TB:
			return '{0:.2f} GB'.format(B/GB)
		elif TB <= B:
			return '{0:.2f} TB'.format(B/TB)

	def __call__(self, block_num, block_size, total_size):
		readsofar = block_num * block_size
		if total_size > 0:
			percent = readsofar * 1e2 / total_size
			wx.CallAfter(self.frame.onProgreso, percent)
			time.sleep(1 / 395)

			wx.CallAfter(self.frame.onTextoEstado, _("Espere por favor...\n") + _("Descargando {}: {}").format(self.idiomaActual, self.humanbytes(readsofar)))
			if readsofar >= total_size: # Si queremos hacer algo cuando la descarga termina.
				pass
		else: # Si la descarga es solo el tamaño
			wx.CallAfter(self.frame.onTextoEstado, _("Espere por favor...\n") + _("Descargando {}: {}").format(self.idiomaActual, self.humanbytes(readsofar)))

	def descomprimir_zip(self, archivo, directorio_destino):
		zf = zipfile.ZipFile(archivo)
		uncompress_size = sum((file.file_size for file in zf.infolist()))
		extracted_size = 0
		for file in zf.infolist():
			extracted_size += file.file_size
			progress = (lambda x, y: (int(x), int(x*y) % y/y))((extracted_size * 100/uncompress_size), 1e0)
			wx.CallAfter(self.frame.onProgreso, progress[0])
			zf.extract(file, directorio_destino)

	def run(self):
		errores = []
		logErrores = []
		indice = 0
		try:
			socket.setdefaulttimeout(self.tiempo) # Dara error si pasan 30 seg sin internet
			for i in self.urls:
				try:
					fichero = os.path.basename(ajustes.dbDatos[i]['links'][0])
					self.idiomaActual = self.idiomas[indice]
					try:
						urllib.request.urlretrieve(ajustes.dbDatos[i]['links'][0], os.path.join(self.dirModelos, fichero), reporthook=self.__call__)
						wx.CallAfter(self.frame.onTextoEstado, _("Instalando el idioma: {}").format(self.idiomas[indice]))
						self.descomprimir_zip(os.path.join(self.dirModelos, fichero), self.dirModelos)
						indice += 1
						try:
							os.remove(os.path.join(self.dirModelos, fichero))
						except:
							pass
					except Exception as e:
						errores.append(self.idiomas[indice])
						logErrores.append(e)
						indice += 1
						try:
							os.remove(os.path.join(self.dirModelos, fichero))
						except:
							pass
				except Exception as e:
					errores.append(self.idiomas[indice])
					logErrores.append(e)
					try:
						os.remove(os.path.join(self.dirModelos, fichero))
					except:
						pass

			if len(errores) == 0:
				ajustes.IS_Reinicio = True
				msg = \
_("""La instalación termino correctamente.

Para que los cambios tengan efecto NVDA tiene que reiniciarse.

¿Desea reiniciar NVDA?""")
				wx.CallAfter(self.frame.onCorrecto, msg)
			elif len(errores) == len(self.idiomas):
				msg = \
_("""Se produjeron errores en la instalación.

No se pudo instalar ningún idioma.

Error(es):
{}""").format("\n".join(str(x) for x in logErrores))
				wx.CallAfter(self.frame.onError, msg)
			else:
				ajustes.IS_Reinicio = True
				msg = \
_("""Se completo la instalación.

Pero hay idiomas que no han podido ser instalados:

{}

Para que los cambios tengan efecto NVDA tiene que reiniciarse.

¿Desea reiniciar NVDA?""").format("\n".join(str(x) for x in errores))
				wx.CallAfter(self.frame.onCorrecto, msg)
		except Exception as e:
			msg = \
_("""Algo salió mal.

Error:

{}""").format(e)
			wx.CallAfter(self.frame.onError, msg)

class HiloBorrarDirectorio(Thread):
	def __init__(self, frame, idiomas, directorios):
		super(HiloBorrarDirectorio, self).__init__()

		self.frame = frame
		self.idiomas = idiomas
		self.directorios = directorios

		self.idiomaActual = ""

		self.daemon = True
		self.start()

	def run(self):
		errores = []
		logErrores = []
		indice = 0
		try:
			for i in self.directorios:
				self.idiomaActual = self.idiomas[indice]
				wx.CallAfter(self.frame.onTextoEstado, _("Desinstalando el idioma: {}").format(self.idiomas[indice]))
				try:
					shutil.rmtree(ajustes.choiceLenguajes[3][i])
				except Exception as e:
					errores.append(self.idiomas[indice])
					logErrores.append(e)
				indice += 1
				wx.CallAfter(self.frame.onProgreso, indice)

			if len(errores) == 0:
				ajustes.IS_Reinicio = True
				msg = \
_("""La desinstalación termino correctamente.

Para que los cambios tengan efecto NVDA tiene que reiniciarse.

¿Desea reiniciar NVDA?""")
				wx.CallAfter(self.frame.onCorrecto, msg)
			elif len(errores) == len(self.idiomas):
				msg = \
_("""Se produjeron errores en la desinstalación.

No se pudo desinstalar ningún idioma.

Error(es):
{}""").format("\n".join(str(x) for x in logErrores))
				wx.CallAfter(self.frame.onError, msg)
			else:
				ajustes.IS_Reinicio = True
				msg = \
_("""Se completo la desinstalación.

Pero hay idiomas que no han podido ser desinstalados:

{}

Para que los cambios tengan efecto NVDA tiene que reiniciarse.

¿Desea reiniciar NVDA?""").format("\n".join(str(x) for x in errores))
				wx.CallAfter(self.frame.onCorrecto, msg)
		except Exception as e:
			msg = \
_("""Algo salió mal.

Error:

{}""").format(e)
			wx.CallAfter(self.frame.onError, msg)
