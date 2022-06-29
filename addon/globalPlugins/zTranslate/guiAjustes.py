# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import addonHandler
import gui
from gui.nvdaControls import CustomCheckListBox
import core
import winsound
import wx
import json
import os
from . import utilidades
from . import ajustes
from . import hilos

addonHandler.initTranslation()

class VentanaAjustes(wx.Dialog):
	def __init__(self, parent):
		super(VentanaAjustes, self).__init__(parent, -1)

		ajustes.IS_WinON = True
		self.SetSize((1000, 800))
		self.SetTitle(_("Configuración de zTranslate"))

		self.IS_Active = False

		self.idiomasInstalar = []
		self.idiomasInstalados = []

		self.panelPrincipal = wx.Panel(self, wx.ID_ANY)

		sizerPrincipal = wx.BoxSizer(wx.VERTICAL)

		self.lista = wx.Listbook(self.panelPrincipal, wx.ID_ANY)
		sizerPrincipal.Add(self.lista, 1, wx.EXPAND, 0)
#####
		self.panelGeneral = wx.Panel(self.lista, wx.ID_ANY)
		self.lista.AddPage(self.panelGeneral, _("General"))

		sizerGeneral = wx.BoxSizer(wx.VERTICAL)

		label_1 = wx.StaticText(self.panelGeneral, wx.ID_ANY, _("Seleccione un idioma de &origen:"))
		sizerGeneral.Add(label_1, 0, wx.EXPAND, 0)

		self.choiceOrigen = wx.Choice(self.panelGeneral, 201)
		sizerGeneral.Add(self.choiceOrigen, 0, wx.EXPAND, 0)

		label_3 = wx.StaticText(self.panelGeneral, wx.ID_ANY, _("Seleccione un idioma de &destino:"))
		sizerGeneral.Add(label_3, 0, wx.EXPAND, 0)

		self.choiceDestino = wx.Choice(self.panelGeneral, 202)
		sizerGeneral.Add(self.choiceDestino, 0, wx.EXPAND, 0)

		self.checkboxAutoDetectar = wx.CheckBox(self.panelGeneral, wx.ID_ANY, _("Activar o desactivar auto detectar idioma de origen (opción experimental)"))
		sizerGeneral.Add(self.checkboxAutoDetectar, 0, wx.EXPAND, 0)

		self.checkboxCache = wx.CheckBox(self.panelGeneral, wx.ID_ANY, _("Activar o desactivar la cache de traducción"))
		sizerGeneral.Add(self.checkboxCache, 0, wx.EXPAND, 0)
#####
		self.panelGestor = wx.Panel(self.lista, wx.ID_ANY)
		self.lista.AddPage(self.panelGestor, _("Gestor de idiomas"))

		sizerGestor = wx.BoxSizer(wx.VERTICAL)

		label_4 = wx.StaticText(self.panelGestor, wx.ID_ANY, _("&Lista de idiomas para instalar:"))
		sizerGestor.Add(label_4, 0, wx.EXPAND, 0)

		self.listboxInstalar = CustomCheckListBox(self.panelGestor, wx.ID_ANY)
		sizerGestor.Add(self.listboxInstalar, 2, wx.EXPAND, 0)

		self.instalarBTN = wx.Button(self.panelGestor, 101, _("&Instalar idiomas seleccionados"))
		sizerGestor.Add(self.instalarBTN, 0, wx.EXPAND, 0)

		label_5 = wx.StaticText(self.panelGestor, wx.ID_ANY, _("&Lista de idiomas instalados:"))
		sizerGestor.Add(label_5, 0, wx.EXPAND, 0)

		self.listboxInstalados = CustomCheckListBox(self.panelGestor, wx.ID_ANY)
		sizerGestor.Add(self.listboxInstalados, 2, wx.EXPAND, 0)

		self.desinstalarBTN = wx.Button(self.panelGestor, 102, _("&Desinstalar idiomas seleccionados"))
		sizerGestor.Add(self.desinstalarBTN, 0, wx.EXPAND, 0)
#####
		sizerEstado = wx.BoxSizer(wx.VERTICAL)
		sizerPrincipal.Add(sizerEstado, 0, wx.EXPAND, 0)

		label_2 = wx.StaticText(self.panelPrincipal, wx.ID_ANY, _("&Estado:"))
		sizerEstado.Add(label_2, 0, wx.EXPAND, 0)

		self.textEstado = wx.TextCtrl(self.panelPrincipal, wx.ID_ANY, "", style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		sizerEstado.Add(self.textEstado, 1, wx.EXPAND, 0)

		self.progreso = wx.Gauge(self.panelPrincipal, wx.ID_ANY, 10)
		sizerEstado.Add(self.progreso, 0, wx.EXPAND, 0)

		sizerEstadoBotones = wx.BoxSizer(wx.HORIZONTAL)
		sizerEstado.Add(sizerEstadoBotones, 0, wx.EXPAND, 0)

		self.aceptarBTN = wx.Button(self.panelPrincipal, 196, _("&Aceptar"))
		sizerEstadoBotones.Add(self.aceptarBTN, 2, wx.CENTRE, 0)

		self.cancelarBTN = wx.Button(self.panelPrincipal, 197, _("&Cancelar"))
		sizerEstadoBotones.Add(self.cancelarBTN, 1, wx.CENTRE, 0)

		self.continuarBTN = wx.Button(self.panelPrincipal, 198, _("Con&tinuar"))
		sizerEstadoBotones.Add(self.continuarBTN, 2, wx.CENTRE, 0)

		self.cerrarBTN = wx.Button(self.panelPrincipal, 199, _("&Cerrar"))
		sizerEstadoBotones.Add(self.cerrarBTN, 2, wx.CENTRE, 0)

		self.panelGestor.SetSizer(sizerGestor)

		self.panelGeneral.SetSizer(sizerGeneral)

		self.panelPrincipal.SetSizer(sizerPrincipal)

		self.Layout()
		self.CenterOnScreen()
		self.eventos()

	def eventos(self):
		self.textEstado.Bind(wx.EVT_CONTEXT_MENU, self.onPasar)
		self.Bind(wx.EVT_BUTTON,self.onBoton)
		self.Bind(wx.EVT_CHAR_HOOK, self.onkeyVentanaDialogo)
		self.Bind(wx.EVT_CLOSE, self.onSalir)
		self.onEstado()
		self.inicio()

	def onEstado(self):
		self.textEstado.Disable()
		self.continuarBTN.Disable()
		self.cerrarBTN.Disable()

	def inicio(self):
		for i in range(0, len(ajustes.dbDatos)):
			self.idiomasInstalar.append("{} - {}".format(ajustes.lenguajes.get(ajustes.dbDatos[i]['from_code']), ajustes.lenguajes.get(ajustes.dbDatos[i]['to_code'])))

		if len(ajustes.choiceLenguajes[0]) == 0:
			self.choiceOrigen.Append(_("Sin idiomas. Agregue idiomas desde el gestor de idiomas."))
			self.choiceDestino.Append(_("Sin idiomas. Agregue idiomas desde el gestor de idiomas."))
			self.choiceOrigen.SetSelection(0)
			self.choiceDestino.SetSelection(0)
			self.listboxInstalados.Disable()
			self.desinstalarBTN.Disable()

			self.listboxInstalar.Append([x for x in self.idiomasInstalar if x not in self.idiomasInstalados])
			self.listboxInstalar.SetSelection(0)
		else:
			temp0 = [_("Elija un idioma de origen")]
			temp1 = [_("Elija un idioma de destino")]
			for i in utilidades.borraDuplicadosLista(ajustes.choiceLenguajes[0]):
				temp0.append(ajustes.lenguajes.get(i))
			for i in utilidades.borraDuplicadosLista(ajustes.choiceLenguajes[1]):
				temp1.append(ajustes.lenguajes.get(i))

			if ajustes.choiceLangOrigen == "0":
				self.choiceOrigen.Append(temp0)
				self.choiceOrigen.SetSelection(0)
			else:
				self.choiceOrigen.Append(temp0)
				if ajustes.choiceLangOrigen in ajustes.choiceLenguajes[0]:
					self.choiceOrigen.SetSelection(temp0.index(ajustes.lenguajes.get(ajustes.choiceLangOrigen)))
				else:
					self.choiceOrigen.SetSelection(0)

			if ajustes.choiceLangDestino == "0":
				self.choiceDestino.Append(temp1)
				self.choiceDestino.SetSelection(0)
			else:
				self.choiceDestino.Append(temp1)
				if ajustes.choiceLangDestino in ajustes.choiceLenguajes[1]:
					self.choiceDestino.SetSelection(temp1.index(ajustes.lenguajes.get(ajustes.choiceLangDestino)))
				else:
					self.choiceDestino.SetSelection(0)

			for i in range(0, len(ajustes.choiceLenguajes[0])):
				self.idiomasInstalados.append("{} - {}".format(ajustes.lenguajes.get(ajustes.choiceLenguajes[0][i]), ajustes.lenguajes.get(ajustes.choiceLenguajes[1][i])))
			instaladosTemp = [x for x in self.idiomasInstalar if x not in self.idiomasInstalados]
			if len(instaladosTemp) == 0:
				self.listboxInstalar.Disable()
				self.instalarBTN.Disable()
				self.listboxInstalados.Append(self.idiomasInstalados)
				self.listboxInstalados.SetSelection(0)
			else:
				self.listboxInstalar.Append([x for x in self.idiomasInstalar if x not in self.idiomasInstalados])
				self.listboxInstalados.Append(self.idiomasInstalados)
				self.listboxInstalar.SetSelection(0)
				self.listboxInstalados.SetSelection(0)

		self.checkboxAutoDetectar.SetValue(True) if ajustes.chkAutoDetect else self.checkboxAutoDetectar.SetValue(False)
		self.checkboxCache.SetValue(True) if ajustes.chkCache else self.checkboxCache.SetValue(False)

#		print(list(ajustes.lenguajes.keys())[list(ajustes.lenguajes.values()).index("Español")])
#		print(ajustes.choiceLenguajes)
#		print(ajustes.choiceLenguajes[3][3])

	def onPasar(self, event):
		return

	def OnSelection(self, event):
		pass

	def onProgreso(self, event):
		self.progreso.SetValue(event)

	def onTextoEstado(self, event):
		self.textEstado.Clear()
		self.textEstado.AppendText(event)

	def onCorrecto(self, event):
		self.progreso.SetValue(0)
		winsound.MessageBeep(0)
		self.IS_Active = False
		self.textEstado.Clear()
		self.textEstado.AppendText(event)
		self.textEstado.SetInsertionPoint(0) 
		self.continuarBTN.Enable()
		self.cerrarBTN.Enable()

	def onError(self, event):
		self.progreso.SetValue(0)
		winsound.MessageBeep(16)
		self.IS_Active = False
		self.textEstado.Clear()
		self.textEstado.AppendText(event)
		self.textEstado.SetInsertionPoint(0)
		self.continuarBTN.Enable()
		self.cerrarBTN.Enable()

	def onBoton(self, event):
		id = event.GetId()
		if id == 101: # Botón instalar
			idiomas = [self.listboxInstalar.GetString(i) for i in [i for i in range(self.listboxInstalar.GetCount()) if self.listboxInstalar.IsChecked(i)]]
			urls = [self.idiomasInstalar.index(i) for i in idiomas]
			if len(idiomas) == 0:
				msg = \
_("""Necesita seleccionar por lo menos un idioma en la lista de idiomas para instalar.

Presione aceptar para continuar.""")
				gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
				self.listboxInstalar.SetFocus()
				return
			if not utilidades.chkInternet():
				msg = \
_("""No se encontró conexión a internet.

Es necesaria para descargar idiomas.

Compruebe que todo esta correcto y vuelva a intentarlo.""")
				gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
				return
			self.IS_Active = True
			self.progreso.SetRange(100)
			self.lista.Disable()
			self.aceptarBTN.Disable()
			self.cancelarBTN.Disable()
			self.textEstado.Enable()
			self.textEstado.SetFocus()
			hilos.HiloDescarga(self, idiomas, urls)
		elif id == 102: # Botón desinstalar
			idiomas = [self.listboxInstalados.GetString(i) for i in [i for i in range(self.listboxInstalados.GetCount()) if self.listboxInstalados.IsChecked(i)]]
			directoriosBorrar = [self.idiomasInstalados.index(i) for i in idiomas]
			if len(idiomas) == 0:
				msg = \
_("""Necesita seleccionar por lo menos un idioma en la lista de idiomas instalados.

Presione aceptar para continuar.""")
				gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
				self.listboxInstalados.SetFocus()
				return
			msg = \
_("""Va a desinstalar los siguientes idiomas:

{}
Esta acción no es reversible.

¿Esta seguro que desea continuar?""").format("\n".join(str(x) for x in idiomas))
			dmsg = wx.MessageDialog(None, msg, _("Pregunta"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
			ret = dmsg.ShowModal()
			if ret == wx.ID_YES:
				dmsg.Destroy()
				self.IS_Active = True
				self.progreso.SetRange(len(idiomas))
				self.lista.Disable()
				self.aceptarBTN.Disable()
				self.cancelarBTN.Disable()
				self.textEstado.Enable()
				self.textEstado.SetFocus()
				hilos.HiloBorrarDirectorio(self, idiomas, directoriosBorrar)
			else:
				dmsg.Destroy()
				self.listboxInstalados.SetFocus()
		elif id == 196: # Botón aceptar
			if self.choiceOrigen.GetString(self.choiceOrigen.GetSelection()) == _("Sin idiomas. Agregue idiomas desde el gestor de idiomas.") or self.choiceDestino.GetString(self.choiceDestino.GetSelection()) == _("Sin idiomas. Agregue idiomas desde el gestor de idiomas."):
				ajustes.choiceLangOrigen = "0"
				ajustes.choiceLangDestino = "0"
				ajustes.chkAutoDetect = self.checkboxAutoDetectar.GetValue()
				ajustes.chkCache = self.checkboxCache.GetValue()
				ajustes.guardaConfiguracion()
				self.onSalir(None)
			else:
				if self.choiceOrigen.GetString(self.choiceOrigen.GetSelection()) == _("Elija un idioma de origen") or self.choiceDestino.GetString(self.choiceDestino.GetSelection()) == _("Elija un idioma de destino"):
					msg = \
_("""Necesita seleccionar un idioma de origen y uno de destino para poder continuar.""")
					gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
					return
				else:
					codeOrigen = list(ajustes.lenguajes.keys())[list(ajustes.lenguajes.values()).index(self.choiceOrigen.GetString(self.choiceOrigen.GetSelection()))]
					codeDestino = list(ajustes.lenguajes.keys())[list(ajustes.lenguajes.values()).index(self.choiceDestino.GetString(self.choiceDestino.GetSelection()))]
					if codeOrigen == codeDestino:
						msg = \
_("""Los idiomas origen y destino no pueden ser iguales.

Cambie uno de los dos para poder continuar.""")
						gui.messageBox(msg, _("Información"), wx.ICON_INFORMATION)
						return
					else:
						ajustes.choiceLangOrigen = codeOrigen
						ajustes.choiceLangDestino = codeDestino
						ajustes.chkAutoDetect = self.checkboxAutoDetectar.GetValue()
						ajustes.chkCache = self.checkboxCache.GetValue()
						ajustes.guardaConfiguracion()
						self.onSalir(None)
		elif id == 197: # Botón cancelar
			self.onSalir(None)
		elif id == 198: # Botón continuar
			if ajustes.IS_Reinicio:
				ajustes.chkAutoDetect = self.checkboxAutoDetectar.GetValue()
				ajustes.chkCache = self.checkboxCache.GetValue()
				ajustes.guardaConfiguracion()
				core.restart()
			else:
				self.aceptarBTN.Enable()
				self.cancelarBTN.Enable()
				self.onEstado()
				self.lista.Enable()
				self.lista.SetFocus()
		elif id == 199: # Botón cerrar
			codeOrigen = list(ajustes.lenguajes.keys())[list(ajustes.lenguajes.values()).index(self.choiceOrigen.GetString(self.choiceOrigen.GetSelection()))]
			codeDestino = list(ajustes.lenguajes.keys())[list(ajustes.lenguajes.values()).index(self.choiceDestino.GetString(self.choiceDestino.GetSelection()))]
			ajustes.choiceLangOrigen = codeOrigen
			ajustes.choiceLangDestino = codeDestino
			ajustes.chkAutoDetect = self.checkboxAutoDetectar.GetValue()
			ajustes.chkCache = self.checkboxCache.GetValue()
			ajustes.guardaConfiguracion()
			self.onSalir(None)

	def onkeyVentanaDialogo(self, event):
		if event.GetKeyCode() == 27: # Pulsamos ESC y cerramos la ventana
			self.onSalir(None)
		else:
			event.Skip()

	def onSalir(self, event):
		if self.IS_Active:
			return
		else:
			ajustes.IS_WinON = False
			self.Destroy()
			gui.mainFrame.postPopup()
