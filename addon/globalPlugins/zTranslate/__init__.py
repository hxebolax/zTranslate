# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import globalPluginHandler
import addonHandler
import globalVars
import gui
import ui
from scriptHandler import script, getLastScriptRepeatCount
import core
import shellapi
import speech
from speech import *
import logHandler
import json
import re
import codecs
import wx
import wx.adv
from threading import Thread
import os
from .lib import psutil
from . import ajustes
from . import utilidades
from . import guiAjustes
from . import idiomas
from . import portapapeles

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()

		if hasattr(globalVars, "ztranslate"):
			self.postStartupHandler()
		core.postNvdaStartup.register(self.postStartupHandler)
		globalVars.ztranslate = None

	def postStartupHandler(self):
		Thread(target=self.__inicio, daemon = True).start()

	def __inicio(self):
		ajustes.setup()

		ajustes.idMaquina = str.encode(utilidades.id_maquina())
		ajustes.puerto = utilidades.obtenPuerto()

		try:
			PROCNAME = "zTranslate-srv.exe"
			for proc in psutil.process_iter():
				if proc.name() == PROCNAME:
					proc.kill()
		except:
			pass

		shellapi.ShellExecute(None, "open", os.path.realpath(os.path.join(os.path.dirname(__file__), "servidor", "zTranslate-srv.exe")), "{} {}".format("localhost", ajustes.puerto), os.path.join(os.path.dirname(__file__), "servidor"), 10)

		if ajustes.chkCache:
			self.loadLocalCache()

		self.menu = gui.mainFrame.sysTrayIcon.preferencesMenu
		self.WXMenu = wx.Menu()
		self.mainItem = self.menu.AppendSubMenu(self.WXMenu, _("&zTranslate"), "")
		self.settingsItem = self.WXMenu.Append(wx.ID_ANY, _("&Configuración"), "")
		self.rebootServer = self.WXMenu.Append(wx.ID_ANY, _("&Reiniciar el servidor y cliente"), "")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.settingsItem)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onReboot, self.rebootServer)

		from . import nvdaExtra

		ajustes._nvdaSpeak = speech._manager.speak
		ajustes._nvdaGetPropertiesSpeech = speech.getPropertiesSpeech
		speech._manager.speak = nvdaExtra.speak
		speech.getPropertiesSpeech = ajustes._nvdaGetPropertiesSpeech
		ajustes._enableTranslation = False

		Thread(target=self.startServer, daemon = True).start()

	def startServer(self):
		if ajustes.IS_Sonido:
			conectar = wx.adv.Sound(os.path.join(os.path.dirname(__file__), "audio", "conectar.wav"))
			conectar.Play(wx.adv.SOUND_ASYNC|wx.adv.SOUND_LOOP)
			ajustes.idMaquina = str.encode(utilidades.id_maquina())
			ajustes.puerto = utilidades.obtenPuerto()
			ajustes._enableTranslation = False
			try:
				PROCNAME = "zTranslate-srv.exe"
				for proc in psutil.process_iter():
					if proc.name() == PROCNAME:
						proc.kill()
			except:
				pass

			shellapi.ShellExecute(None, "open", os.path.realpath(os.path.join(os.path.dirname(__file__), "servidor", "zTranslate-srv.exe")), "{} {}".format("localhost", ajustes.puerto), os.path.join(os.path.dirname(__file__), "servidor"), 10)

		from . import cliente

		while True:
			if utilidades.procesoCHK("zTranslate-srv.exe"):
				ajustes.cliente = cliente.Cliente()
				if not ajustes.cliente.returnCode:
					ajustes.IS_Cliente = False
				else:
					ajustes.IS_Cliente = True
					ajustes.choiceLenguajes = ajustes.cliente.comando(["{}cmd".format(ajustes.idMaquina), "langDisponigles"])
					break

		if ajustes.IS_Sonido:
			conectar.Stop()
			ajustes.IS_Sonido = False
			ajustes.IS_Reinicio = False

	def terminate(self):
		try:
			PROCNAME = "zTranslate-srv.exe"
			for proc in psutil.process_iter():
				if proc.name() == PROCNAME:
					proc.kill()
		except:
			pass
		try:
			self.menu.Remove(self.mainItem)
		except Exception:
			pass
		try:
			ajustes.cliente.terminarServer()
		except:
			pass
		speech._manager.speak = ajustes._nvdaSpeak
		speech.getPropertiesSpeech = ajustes._nvdaGetPropertiesSpeech
		if ajustes.chkCache:
			self.saveLocalCache()
		core.postNvdaStartup.unregister(self.postStartupHandler)
		super().terminate()

	def loadLocalCache(self):
		path = os.path.join(globalVars.appArgs.configPath, "zTranslate_cache")
		# Checks that the storage path exists or create it.
		if os.path.exists(path) is False:
			try:
				os.mkdir(path)
			except Exception as e:
				logHandler.log.error("Failed to create storage path: {path} ({error})".format(path=path, error=e))
				return
                                                                                                
		# Scan stored files and load them.
		for entry in os.listdir(path):
			m = re.match("(.*)\.json$", entry)
			if m is not None:
				appName = m.group(1)
				try:
					cacheFile = codecs.open(os.path.join(path, entry), "r", "utf-8")
				except:
					continue
				try:
					values = json.load(cacheFile)
					cacheFile.close()
				except Exception as e:
					logHandler.log.error("Cannot read or decode data from {path}: {e}".format(path=path, e=e))
					cacheFile.close()
					continue
				ajustes._translationCache[appName] = values
				cacheFile.close()

	def saveLocalCache(self):
		print("holaaaa....")
		path = os.path.join(globalVars.appArgs.configPath, "zTranslate_cache")
		for appName in ajustes._translationCache:
			file = os.path.join(path, "{}.json".format(appName))
			try:
				cacheFile = codecs.open(file, "w", "utf-8")
				json.dump(ajustes._translationCache[appName], cacheFile, ensure_ascii=False)
				cacheFile.close()
			except Exception as e:
				logHandler.log.error("Failed to save translation cache for {app} to {file}: {error}".format(apap=appName, file=file, error=e))
				continue

	def onSettings(self, event):
		self.script_onSettings(None, True)

	def onReboot(self, event):
		try:
			ajustes.cliente.terminarServer()
		except:
			pass
		ajustes.IS_Sonido = True
		Thread(target=self.startServer, daemon = True).start()

	@script(gesture=None, description= _("Abre la configuración de zTranslate"), category= "zTranslate")
	def script_onSettings(self, event, menu=False):
		if ajustes.IS_Reinicio:
			msg = \
_("""zTranslate no puede usarse en este momento.

Tiene una acción por terminar.

Puede reiniciar NVDA o reiniciar en Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
			if menu:
				gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
			else:
				ui.message(msg)
		else:
			if utilidades.procesoCHK("zTranslate-srv.exe"):
				if ajustes.IS_Cliente:
					if ajustes.IS_WinON:
						if menu:
							gui.messageBox(_("Ya hay una instancia de zTranslate abierta."), _("Información"), wx.ICON_INFORMATION)
						else:
							ui.message(_("Ya hay una instancia de zTranslate abierta."))
					else:
						ajustes._enableTranslation = False
						HiloComplemento(1).start()
				else:
					msg = \
_("""Si acaba de iniciar NVDA espere unos segundos el cliente se esta cargando.

Si hace tiempo que inicio NVDA puede que la comunicación entre cliente y servidor se perdiera.

Reinicie NVDA o reinicie el cliente desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
					if menu:
						gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
					else:
						ui.message(msg)
			else:
				msg = \
_("""El servidor de traducciones no esta activo.

Reinicie NVDA o reinicie el servidor desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
				if menu:
					gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
				else:
					ui.message(msg)

	@script(gesture=None, description= _("Activa o desactiva la traducción simultanea"), category= "zTranslate")
	def script_toggleTranslate(self, event):
		if ajustes.IS_Reinicio:
			msg = \
_("""zTranslate no puede usarse en este momento.

Tiene una acción por terminar.

Puede reiniciar NVDA o reiniciar en Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
			ui.message(msg)
		else:
			if utilidades.procesoCHK("zTranslate-srv.exe"):
				if ajustes.IS_Cliente:
					if ajustes.IS_WinON:
						msg = \
_("""La traducción no puede ser activada mientras haya una ventana de zTranslate abierta""")
						ui.message(msg)
					else:
						if len(ajustes.choiceLenguajes[0]) == 0 or ajustes.choiceLangOrigen == "0":
							msg = \
_("""No tiene ningún idioma instalado o seleccionado.

Instale o seleccione un idioma desde la configuración de zTranslate.""")
							ui.message(msg)
						else:
							ajustes._enableTranslation = not ajustes._enableTranslation
							if ajustes._enableTranslation:
								ui.message(_("Traducción activada."))
								if ajustes.chkCache:
									self.loadLocalCache()
							else:
								ui.message(_("Traducción desactivada."))
								if ajustes.chkCache:
									self.saveLocalCache()
				else:
					msg = \
_("""El cliente de traducciones no esta activo.

Reinicie NVDA o reinicie el cliente desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
					ui.message(msg)
			else:
				msg = \
_("""El servidor de traducciones no esta activo.

Reinicie NVDA o reinicie el servidor desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
				ui.message(msg)

	@script(gesture=None, description= _("Eliminar todas las traducciones en caché para todas las aplicaciones"), category= "zTranslate")
	def script_flushAllCache(self, event):
		if getLastScriptRepeatCount() == 0:
			ui.message(_("Pulse dos veces para eliminar todas las traducciones en caché de todas las aplicaciones."))
			return

		ajustes._translationCache = {}
		path = os.path.join(globalVars.appArgs.configPath, "zTranslate_cache")
		error = False
		for entry in os.listdir(path):
			try:
				os.unlink(os.path.join(path, entry))
			except Exception as e:
				logHandler.log.error("Failed to remove {entry}".format(entry=entry))
				error = True
		if not error:
			ui.message(_("Se han eliminado todas las traducciones."))
		else:
			ui.message(_("No se a podido eliminar toda la cache."))

	@script(gesture=None, description= _("Eliminar la caché de traducción para la aplicación enfocada actualmente"), category= "zTranslate")
	def script_flushCurrentAppCache(self, event):
		try:
			appName = globalVars.focusObject.appModule.appName
		except:
			ui.message(_("No hay aplicación enfocada."))
			return
		if getLastScriptRepeatCount() == 0:
			msg = \
_("""Pulse dos veces para eliminar todas las traducciones de {} en lenguaje {}""").format(appName, idiomas.diccionario_lenguajes.get(ajustes.choiceLangDestino))
			ui.message(msg)
			return
                                        
		ajustes._translationCache[appName] = {}
		fullPath = os.path.join(globalVars.appArgs.configPath, "zTranslate_cache", "{}_{}.json".format(appName, ajustes.choiceLangDestino))
		if os.path.exists(fullPath):
			try:
				os.unlink(fullPath)
			except Exception as e:
				logHandler.log.error("Fallo al borrar la cache de la aplicación {} : {}".format(appName, e))
				ui.message(_("Error al borrar la caché de traducción de la aplicación."))
				return
			ui.message(_("Se ha borrado la cache de la aplicación {} correctamente.").format(appName))
		else:
			ui.message(_("No hay traducciones guardadas para {}").format(appName))

	@script(gesture=None, description= _("Copiar el ultimo texto traducido al portapapeles"), category= "zTranslate")
	def script_copyLastTranslation(self, event):
		if ajustes._lastTranslatedText is not None and len(ajustes._lastTranslatedText) > 0:
			portapapeles.put(ajustes._lastTranslatedText)
			ui.message(_("Se a copiado lo siguiente al portapapeles: {}").format(ajustes._lastTranslatedText))
		else:
			ui.message(_("No se a podido copiar nada al portapapeles"))

	@script(gesture=None, description= _("Cambiar rápidamente el idioma origen"), category= "zTranslate")
	def script_changeLangOrigen(self, event):
		if ajustes.IS_Reinicio:
			msg = \
_("""zTranslate no puede usarse en este momento.

Tiene una acción por terminar.

Puede reiniciar NVDA o reiniciar en Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
			ui.message(msg)
		else:
			if utilidades.procesoCHK("zTranslate-srv.exe"):
				if ajustes.IS_Cliente:
					if ajustes.IS_WinON:
						ui.message(_("El idioma origen no puede cambiarse rápidamente si hay una ventana de zTranslate abierta."))
					else:
						if len(ajustes.choiceLenguajes[0]) == 0 or ajustes.choiceLangOrigen == "0":
							msg = \
_("""No tiene ningún idioma instalado o seleccionado.

Instale o seleccione un idioma desde la configuración de zTranslate.""")
							ui.message(msg)
						else:
							if ajustes._enableTranslation:
								ajustes._enableTranslation = False
								temp = True
								if ajustes.chkCache:
									self.saveLocalCache()
							else:
								temp = False
							listaTemp = utilidades.borraDuplicadosLista(list(ajustes.choiceLenguajes[0]))
							try:
								del listaTemp[listaTemp.index(ajustes.choiceLangDestino)]
							except:
								pass
							ajustes.indiceLangOrigen = listaTemp.index(ajustes.choiceLangOrigen)
							if ajustes.indiceLangOrigen >= len(listaTemp) - 1:
								ajustes.indiceLangOrigen = 0
								nombreSiguiente = ajustes.lenguajes.get(listaTemp[ajustes.indiceLangOrigen])
								ui.message(_("Idioma origen {}").format(nombreSiguiente))
								ajustes.choiceLangOrigen = listaTemp[ajustes.indiceLangOrigen]
								ajustes.setConfig("langOrigen",listaTemp[ajustes.indiceLangOrigen])
							else:
								ajustes.indiceLangOrigen += 1
								nombreSiguiente = ajustes.lenguajes.get(listaTemp[ajustes.indiceLangOrigen])
								ui.message(_("Idioma origen {}").format(nombreSiguiente))
								ajustes.choiceLangOrigen = listaTemp[ajustes.indiceLangOrigen]
								ajustes.setConfig("langOrigen",listaTemp[ajustes.indiceLangOrigen])
							if temp:
								ajustes._enableTranslation = True
								if ajustes.chkCache:
									self.loadLocalCache()
				else:
					msg = \
_("""Si acaba de iniciar NVDA espere unos segundos el cliente se esta cargando.

Si hace tiempo que inicio NVDA puede que la comunicación entre cliente y servidor se perdiera.

Reinicie NVDA o reinicie el cliente desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
					ui.message(msg)
			else:
				msg = \
_("""El servidor de traducciones no esta activo.

Reinicie NVDA o reinicie el servidor desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
				ui.message(msg)

	@script(gesture=None, description= _("Cambiar rápidamente el idioma destino"), category= "zTranslate")
	def script_changeLangDestino(self, event):
		if ajustes.IS_Reinicio:
			msg = \
_("""zTranslate no puede usarse en este momento.

Tiene una acción por terminar.

Puede reiniciar NVDA o reiniciar en Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
			ui.message(msg)
		else:
			if utilidades.procesoCHK("zTranslate-srv.exe"):
				if ajustes.IS_Cliente:
					if ajustes.IS_WinON:
						ui.message(_("El idioma destino no puede cambiarse rápidamente si hay una ventana de zTranslate abierta."))
					else:
						if len(ajustes.choiceLenguajes[0]) == 0 or ajustes.choiceLangOrigen == "0":
							msg = \
_("""No tiene ningún idioma instalado o seleccionado.

Instale o seleccione un idioma desde la configuración de zTranslate.""")
							ui.message(msg)
						else:
							if ajustes._enableTranslation:
								ajustes._enableTranslation = False
								temp = True
								if ajustes.chkCache:
									self.saveLocalCache()
							else:
								temp = False
							listaTemp = utilidades.borraDuplicadosLista(list(ajustes.choiceLenguajes[1]))
							try:
								del listaTemp[listaTemp.index(ajustes.choiceLangOrigen)]
							except:
								pass
							ajustes.indiceLangDestino = listaTemp.index(ajustes.choiceLangDestino)
							if ajustes.indiceLangDestino >= len(listaTemp) - 1:
								ajustes.indiceLangDestino = 0
								nombreSiguiente = ajustes.lenguajes.get(listaTemp[ajustes.indiceLangDestino])
								ui.message(_("Idioma destino {}").format(nombreSiguiente))
								ajustes.choiceLangDestino = listaTemp[ajustes.indiceLangDestino]
								ajustes.setConfig("langDestino",listaTemp[ajustes.indiceLangDestino])
							else:
								ajustes.indiceLangDestino += 1
								nombreSiguiente = ajustes.lenguajes.get(listaTemp[ajustes.indiceLangDestino])
								ui.message(_("Idioma destino {}").format(nombreSiguiente))
								ajustes.choiceLangDestino = listaTemp[ajustes.indiceLangDestino]
								ajustes.setConfig("langDestino",listaTemp[ajustes.indiceLangDestino])
							if temp:
								ajustes._enableTranslation = True
								if ajustes.chkCache:
									self.saveLocalCache()
				else:
					msg = \
_("""Si acaba de iniciar NVDA espere unos segundos el cliente se esta cargando.

Si hace tiempo que inicio NVDA puede que la comunicación entre cliente y servidor se perdiera.

Reinicie NVDA o reinicie el cliente desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
					ui.message(msg)
			else:
				msg = \
_("""El servidor de traducciones no esta activo.

Reinicie NVDA o reinicie el servidor desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
				ui.message(msg)

	@script(gesture=None, description= _("Activa o desactiva la autodetección de idioma"), category= "zTranslate")
	def script_toggleAutoLang(self, event):
		if ajustes.IS_Reinicio:
			msg = \
_("""zTranslate no puede usarse en este momento.

Tiene una acción por terminar.

Puede reiniciar NVDA o reiniciar en Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
			ui.message(msg)
		else:
			if utilidades.procesoCHK("zTranslate-srv.exe"):
				if ajustes.IS_Cliente:
					if ajustes.IS_WinON:
						msg = \
_("""La autodetección  no puede ser activada o desactivada mientras haya una ventana de zTranslate abierta""")
						ui.message(msg)
					else:
						if len(ajustes.choiceLenguajes[0]) == 0 or ajustes.choiceLangOrigen == "0":
							msg = \
_("""No tiene ningún idioma instalado o seleccionado.

Instale o seleccione un idioma desde la configuración de zTranslate.""")
							ui.message(msg)
						else:
							if ajustes._enableTranslation:
								ajustes._enableTranslation = False
								temp = True
								if ajustes.chkCache:
									self.saveLocalCache()
							else:
								temp = False
							ajustes.chkAutoDetect = not ajustes.chkAutoDetect
							if ajustes.chkAutoDetect:
								ui.message(_("Autodetección de idioma activada."))
							else:
								ui.message(_("Autodetección de idioma desactivada."))
							ajustes.setConfig("autodetect", ajustes.chkAutoDetect)
							if temp:
								ajustes._enableTranslation = True
								if ajustes.chkCache:
									self.saveLocalCache()
				else:
					msg = \
_("""El cliente de traducciones no esta activo.

Reinicie NVDA o reinicie el cliente desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
					ui.message(msg)
			else:
				msg = \
_("""El servidor de traducciones no esta activo.

Reinicie NVDA o reinicie el servidor desde Preferencias / zTranslate / Reiniciar el servidor y cliente.""")
				ui.message(msg)

	def test(self):
		indiceActual = ajustes.choiceLenguajes[0].index(ajustes.choiceLangOrigen)
		ajustes.indiceLangOrigen += indiceActual
		try:
			nombreSiguiente = ajustes.lenguajes.get(ajustes.choiceLenguajes[0][ajustes.indiceLangOrigen])
			nombreSiguienteES = ajustes.lenguajesEN.get(ajustes.choiceLenguajes[0][ajustes.indiceLangOrigen])
			ui.message(nombreSiguiente)
		except:
			ajustes.indiceLangOrigen = 0

			nombreSiguiente = ajustes.lenguajes.get(ajustes.choiceLenguajes[0][ajustes.indiceLangOrigen+1])
			nombreSiguienteES = ajustes.lenguajesEN.get(ajustes.choiceLenguajes[0][ajustes.indiceLangOrigen+1])
			ui.message(nombreSiguiente)
		ajustes.choiceLangOrigen = ajustes.choiceLenguajes[0][ajustes.indiceLangOrigen - 1]
		ajustes.setConfig("langOrigen", ajustes.choiceLenguajes[0][ajustes.indiceLangOrigen - 1])

#	@script(gesture=None, description= _("comando extra."), category= "zTranslate")
#	def script_testcomando(self, event):
#		print(ajustes.historialOrigen)
#		print(ajustes.historialDestino)
#		self.history = [self.addon.getSequenceText(k) for k in self.addon._history]
#		print(utilidades.limpiaLista(list(ajustes.historialOrigen)))
#		print(utilidades.limpiaLista(list(ajustes.historialDestino)))

if globalVars.appArgs.secure:
	GlobalPlugin = globalPluginHandler.GlobalPlugin # noqa: F811 

class HiloComplemento(Thread):
	def __init__(self, opcion):
		super(HiloComplemento, self).__init__()

		self.opcion = opcion
		self.daemon = True

	def run(self):
		def appLauncherMain():
			self._main = guiAjustes.VentanaAjustes(gui.mainFrame)
			gui.mainFrame.prePopup()
			self._main.Show()

		if self.opcion == 1:
			wx.CallAfter(appLauncherMain)

