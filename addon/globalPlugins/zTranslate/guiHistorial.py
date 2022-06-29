# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import addonHandler
import wx
from . import utilidades
from . import ajustes

addonHandler.initTranslation()

class VentanaHistorial(wx.Dialog):
	def __init__(self, parent):
		super(VentanaHistorial, self).__init__(parent, -1)

		ajustes.IS_WinON = True
		self.SetSize((1000, 800))
		self.SetTitle(_("Historial de zTranslate"))

		self.panelGeneral = wx.Panel(self, wx.ID_ANY)

		sizerGeneral = wx.BoxSizer(wx.VERTICAL)

		label_1 = wx.StaticText(self.panelGeneral, wx.ID_ANY, _("&Buscar:"))
		sizerGeneral.Add(label_1, 0, wx.EXPAND, 0)

		self.textoBuscar = wx.TextCtrl(self.panelGeneral, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
		sizerGeneral.Add(self.textoBuscar, 0, wx.EXPAND, 0)

		label_2 = wx.StaticText(self.panelGeneral, wx.ID_ANY, _("&Lista texto original:"))
		sizerGeneral.Add(label_2, 0, wx.EXPAND, 0)

		self.listboxOriginal = wx.ListBox(self.panelGeneral, wx.ID_ANY, choices=[_("choice 1")])
		self.listboxOriginal.SetSelection(0)
		sizerGeneral.Add(self.listboxOriginal, 1, wx.EXPAND, 0)

		label_3 = wx.StaticText(self.panelGeneral, wx.ID_ANY, _("Texto &origen:"))
		sizerGeneral.Add(label_3, 0, wx.EXPAND, 0)

		self.textoOrigen = wx.TextCtrl(self.panelGeneral, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
		sizerGeneral.Add(self.textoOrigen, 0, wx.EXPAND, 0)

		label_4 = wx.StaticText(self.panelGeneral, wx.ID_ANY, _("Texto &traducido:"))
		sizerGeneral.Add(label_4, 0, wx.EXPAND, 0)

		self.textoTraducido = wx.TextCtrl(self.panelGeneral, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
		sizerGeneral.Add(self.textoTraducido, 0, wx.EXPAND, 0)

		sizerBotones = wx.BoxSizer(wx.HORIZONTAL)
		sizerGeneral.Add(sizerBotones, 0, wx.EXPAND, 0)

		self.button_1 = wx.Button(self.panelGeneral, wx.ID_ANY, _("Copiar &seleccionado"))
		sizerBotones.Add(self.button_1, 2, wx.CENTRE, 0)

		self.button_2 = wx.Button(self.panelGeneral, wx.ID_ANY, _("C&opiar todo"))
		sizerBotones.Add(self.button_2, 2, wx.CENTRE, 0)

		self.button_3 = wx.Button(self.panelGeneral, wx.ID_ANY, _("Borrar &historial"))
		sizerBotones.Add(self.button_3, 2, wx.CENTRE, 0)

		self.button_4 = wx.Button(self.panelGeneral, wx.ID_ANY, _("&Refrescar historial"))
		sizerBotones.Add(self.button_4, 2, wx.CENTRE, 0)

		self.button_5 = wx.Button(self.panelGeneral, wx.ID_ANY, _("&Cerrar"))
		sizerBotones.Add(self.button_5, 2, wx.CENTRE, 0)

		self.panelGeneral.SetSizer(sizerGeneral)

		self.Layout()
		self.CenterOnScreen()
