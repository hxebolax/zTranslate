# -*- coding: utf-8 -*-
# Copyright (C) 2022 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import globalVars
import controlTypes
import speech
from speech import *
import speechViewer
from queueHandler import eventQueue, queueFunction
from eventHandler import FocusLossCancellableSpeechCommand
from . import ajustes

# Cortesía de Gerardo Kessler
getRole = lambda attr: getattr(controlTypes, f'ROLE_{attr}') if hasattr(controlTypes, 'ROLE_BUTTON') else getattr(controlTypes.Role, attr)

def funTranslate(text):
	try:
		appName = "{}_{}".format(globalVars.focusObject.appModule.appName, ajustes.choiceLangDestino)
	except:
		appName = "__global__"
                
	if ajustes._enableTranslation is False:
		return text
	if ajustes.chkCache:
		appTable = ajustes._translationCache.get(appName, None)
		if appTable is None:
			ajustes._translationCache[appName] = {}
		translated = ajustes._translationCache[appName].get(text, None)
		if translated is not None and translated != text:
			ajustes.historialOrigen.appendleft(text)
			return translated
	try:
		translated = ajustes.cliente.comando(["{}cmdTrans".format(ajustes.idMaquina), [text, ajustes.choiceLenguajes[2].index(ajustes.lenguajesEN.get(ajustes.choiceLangOrigen)), ajustes.choiceLenguajes[2].index(ajustes.lenguajesEN.get(ajustes.choiceLangDestino)),  ajustes.chkAutoDetect]])
	except Exception as e:
		return text
	if translated is None or len(translated) == 0:
		translated = text
	else:
		if ajustes.chkCache:
			ajustes._translationCache[appName][text] = translated
	ajustes.historialOrigen.appendleft(text)
	return translated

def speak(speechSequence: SpeechSequence, priority: Spri = None):
	if ajustes._enableTranslation is False:
		return ajustes._nvdaSpeak(speechSequence=speechSequence, priority=priority)

	newSpeechSequence = []
	for val in speechSequence:
		if isinstance(val, str):
			v = funTranslate(" ".join(val.split()))
			newSpeechSequence.append(v if v is not None else val)
		else:
			newSpeechSequence.append(val)
	ajustes._nvdaSpeak(speechSequence=newSpeechSequence, priority=priority)
	ajustes._lastTranslatedText = " ".join(x if isinstance(x, str) else "" for x in newSpeechSequence)
	text = getSequenceText(ajustes._lastTranslatedText)
	if text.strip():
		queueFunction(eventQueue, append_to_history, newSpeechSequence)

def getSequenceText(sequence):
	return speechViewer.SPEECH_ITEM_SEPARATOR.join([x for x in sequence if isinstance(x, str)])

def append_to_history(seq):
	seq = [command for command in seq if not isinstance(command, FocusLossCancellableSpeechCommand)]
	ajustes.historialDestino.appendleft(seq[0])


