# -*- coding: utf-8 -*-

# SpecialJump by Fischreiher
#
# Special thanks to Dr.Best (Quickbutton)
# Special thanks to Emanuel (MultiQuickButton)
# Special thanks to vlamo   (Record Infobar)
# Special thanks to StarStb (ExecuteOnPowerEvent)
#
# This plugin is free software, you are allowed to
# modify it (if you keep the license),
# but you are not allowed to distribute/publish
# it without source code (this version and your modifications).
# This means you also have to distribute
# source code of your modifications.
#
# Jump forwards and backwards using two keys.
# After the first change of the jump direction, a new (configurable) jump distance from a list is used for every new jump.
# After the defined timeout, the initial jump distance is used again.
#
# For patent reasons, programming the jump distances so that it results in a "binary search" algorithm may be illegal.
# Therefore jump distance settings like "4:00, 2:00, 1:00, 0:30, 0:15, 0:08, 0:04, 0:02" should be avoided. 

from Screens.AudioSelection import AudioSelection
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.ChannelSelection import ChannelSelection
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.InfoBar import InfoBar
from Screens.InfoBarGenerics import InfoBarCueSheetSupport, InfoBarShowHide, InfoBarNumberZap, NumberZap, InfoBarMenu, InfoBarInstantRecord, InfoBarTimeshift, InfoBarSeek, TimeshiftState, InfoBarExtensions, InfoBarSubtitleSupport, InfoBarAudioSelection, InfoBarPlugins, InfoBarChannelSelection
from Screens.InfoBarGenerics import InfoBarShowMovies, InfoBarEPG
from Screens.InfoBarGenerics import InfoBarSimpleEventView
from Screens.InfoBarGenerics import InfoBarPiP
import Screens.Standby
from Plugins.Plugin import PluginDescriptor
from Components.Sources.List import List
##EMCsp##try:
##EMCsp##	from Components.Sources.EMCCurrentService import EMCCurrentService
##EMCsp##	from Components.Renderer import EMCPositionGauge
##EMCsp##except:
##EMCsp##	print "[SpecialJump] import EMCCurrentService failed"
from Components.Lcd import LCD
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.PluginComponent import plugins
from Components.config import config, ConfigInteger, ConfigSubsection, ConfigYesNo, ConfigLocations, getConfigListEntry, ConfigText, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.VolumeControl import VolumeControl
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Components.ServicePosition import ServicePositionGauge
from Components.NimManager import nimmanager
from ServiceReference import ServiceReference, isPlayableForCur
import NavigationInstance
from enigma import eTimer, ePoint, eSize
from enigma import eDVBVolumecontrol
from enigma import iServiceInformation
from enigma import iPlayableService, iRecordableService
from enigma import eDBoxLCD
from enigma import pNavigation
from enigma import eServiceReference
from datetime import datetime
from random import randint
from Tools.Directories import *
from Tools.BoundFunction import boundFunction
from Tools.ISO639 import LanguageCodes
from Tools import Notifications
from os import path
try:
	from Plugins.Extensions.MovieCut.plugin import main as MovieCut
except:
	print "import MovieCut failed"
try:
	from Plugins.Extensions.CutListEditor.plugin import main as CutListEditor
except:
	print "import CutListEditor failed"
try:
	from Plugins.Extensions.SpecialJump.addons_private import SpecialJumpPrivateAddons
	SpecialJumpPrivateAddonsInst = SpecialJumpPrivateAddons()
except:
	print "import SpecialJumpPrivateAddons failed"
	SpecialJumpPrivateAddonsInst = None

import xml.sax.xmlreader
import os.path
import os
import time
import keymapparser
from __init__ import _

fixedJumpValues  = [("-3600", "-1:00:00"), ("-3000", "-50:00"), ("-2400", "-40:00"), ("-1800", "-30:00"), ("-1500", "-25:00"), ("-1200", "-20:00"), ("-900", "-15:00"), ("-840", "-14:00"), ("-780", "-13:00"), ("-720", "-12:00"), ("-660", "-11:00"), ("-600", "-10:00"), ("-540", "-9:00"), ("-480", "-8:00"), ("-420", "-7:00"), ("-360", "-6:00"), ("-300", "-5:00"), ("-270", "-4:30"), ("-240", "-4:00"), ("-210", "-3:30"), ("-180", "-3:00"), ("-165", "-2:45"), ("-150", "-2:30"), ("-135", "-2:15"), ("-120", "-2:00"), ("-110", "-1:50"), ("-100", "-1:40"), ("-90", "-1:30"), ("-80", "-1:20"), ("-70", "-1:10"), ("-60", "-1:00"), ("-55", "-0:55"), ("-50", "-0:50"), ("-45", "-0:45"), ("-40", "-0:40"), ("-35", "-0:35"), ("-30", "-0:30"), ("-25", "-0:25"), ("-20", "-0:20"), ("-15", "-0:15"), ("-12", "-0:12"), ("-10", "-0:10"), ("-9", "-0:09"), ("-8", "-0:08"), ("-7", "-0:07"), ("-6", "-0:06"), ("-5", "-0:05"), ("-4", "-0:04"), ("-3", "-0:03"), ("-2", "-0:02"), ("-1", "-0:01"), ("0", "0:00"), ("1", "+0:01"), ("2", "+0:02"), ("3", "+0:03"), ("4", "+0:04"), ("5", "+0:05"), ("6", "+0:06"), ("7", "+0:07"), ("8", "+0:08"), ("9", "+0:09"), ("10", "+0:10"), ("12", "+0:12"), ("15", "+0:15"), ("20", "+0:20"), ("25", "+0:25"), ("30", "+0:30"), ("35", "+0:35"), ("40", "+0:40"), ("45", "+0:45"), ("50", "+0:50"), ("55", "+0:55"), ("60", "+1:00"), ("70", "+1:10"), ("80", "+1:20"), ("90", "+1:30"), ("100", "+1:40"), ("110", "+1:50"), ("120", "+2:00"), ("135", "+2:15"), ("150", "+2:30"), ("165", "+2:45"), ("180", "+3:00"), ("210", "+3:30"), ("240", "+4:00"), ("270", "+4:30"), ("300", "+5:00"), ("360", "+6:00"), ("420", "+7:00"), ("480", "+8:00"), ("540", "+9:00"), ("600", "+10:00"), ("660", "+11:00"), ("720", "+12:00"), ("780", "+13:00"), ("840", "+14:00"), ("900", "+15:00"), ("1200", "+20:00"), ("1500", "+25:00"), ("1800", "+30:00"), ("2400", "+40:00"), ("3000", "+50:00"), ("3600", "+1:00:00")]
fixedJumpActions = [("nothing", _("do nothing")), ("audio1", _("change to audio track 1")), ("audio2", _("change to audio track 2")), ("audio3", _("change to audio track 3")), ("audio4", _("change to audio track 4")), ("sub1", _("activate subtitle track 1")), ("sub2", _("activate subtitle track 2")), ("sub3", _("activate subtitle track 3")), ("sub4", _("activate subtitle track 4"))]
audioVolumes     = [("no_change", _("no change")), ("0", "0"), ("1", "1"), ("2", "2"), ("5", "5"), ("10", "10"), ("20", "20"), ("30", "30"), ("40", "40"), ("50", "50"), ("60", "60"), ("70", "70"), ("80", "80"), ("90", "90"), ("100", "100")]
timeoutValues    = [("500", "0.5s"), ("1000", "1s"), ("1500", "1.5s"), ("2000", "2s"), ("2500", "2.5s"), ("3000", "3s"), ("4000", "4s"), ("5000", "5s")]
protectValues    = [("-1", _("no protection, always zap")), ("5000", "5s"), ("10000", "10s"), ("20000", "20s"), ("30000", "30s"), ("60000", "1min"), ("120000", "2min"), ("300000", "5min"), ("600000", "10min"), ("900000", "15min"), ("1800000", "30min"), ("3600000", "60min")]
zapSpeedLimits   = [("0", _("no limit")),      ("60", "0.06s"), ("70", "0.07s"), ("80", "0.08s"), ("90", "0.09s"), ("100", "0.1s"), ("120", "0.12s"), ("150", "0.15s"), ("200", "0.2s"), ("300", "0.3s"), ("400", "0.4s"), ("500", "0.5s"), ("600", "0.6s"), ("700", "0.7s"), ("800", "0.8s"), ("900", "0.9s"), ("1000", "1.0s"), ("1100", "1.1s"), ("1200", "1.2s"), ("1500", "1.5s"), ("2000", "2.0s")]

keymapFiles = []
keymapFiles.append("keymap_classic.xml")
keymapFiles.append("keymap_FastZap_only.xml")
keymapFiles.append("keymap_SpecialJump_MP_only.xml")
keymapFiles.append("keymap_private_Fischreiher.xml")
keymapFiles.append("keymap_user.xml")

config.plugins.SpecialJump = ConfigSubsection()
config.plugins.SpecialJump.enable = ConfigYesNo(default=True)
config.plugins.SpecialJump.zapspeed_enable = ConfigYesNo(default=True)
config.plugins.SpecialJump.mainmenu = ConfigYesNo(default=False)
config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark = ConfigSelection([("yes", _("Yes")),("default", _("default"))], default="default")
config.plugins.SpecialJump.show_infobar = ConfigYesNo(default=True)
config.plugins.SpecialJump.debugEnable = ConfigYesNo(default=False)
	
config.plugins.SpecialJump.keymapFile    = ConfigSelection([(p,p) for p in keymapFiles], default="keymap_classic.xml")

config.plugins.SpecialJump.jump1         = ConfigSelection(fixedJumpValues,  default  ="-15")
config.plugins.SpecialJump.jump2         = ConfigSelection(fixedJumpValues,  default  ="15")
config.plugins.SpecialJump.jump3         = ConfigSelection(fixedJumpValues,  default  ="-30")
config.plugins.SpecialJump.jump4         = ConfigSelection(fixedJumpValues,  default  ="30")
config.plugins.SpecialJump.jump5         = ConfigSelection(fixedJumpValues,  default  ="-15")
config.plugins.SpecialJump.jump6         = ConfigSelection(fixedJumpValues,  default  ="15")
config.plugins.SpecialJump.jump7         = ConfigSelection(fixedJumpValues,  default  ="-30")
config.plugins.SpecialJump.jump8         = ConfigSelection(fixedJumpValues,  default  ="30")
config.plugins.SpecialJump.jump1action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump2action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump3action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump4action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump5action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump6action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump7action   = ConfigSelection(fixedJumpActions, default  ="nothing")
config.plugins.SpecialJump.jump8action   = ConfigSelection(fixedJumpActions, default  ="nothing")

config.plugins.SpecialJump.specialJump0  = ConfigInteger(default  = 131, limits  = (1, 999))
config.plugins.SpecialJump.specialJump1  = ConfigInteger(default  =  11, limits  = (1, 999))
config.plugins.SpecialJump.specialJump2  = ConfigInteger(default  = 101, limits  = (1, 999))
config.plugins.SpecialJump.specialJump3  = ConfigInteger(default  =  21, limits  = (1, 999))
config.plugins.SpecialJump.specialJump4  = ConfigInteger(default  =  91, limits  = (1, 999))
config.plugins.SpecialJump.specialJump5  = ConfigInteger(default  =  51, limits  = (1, 999))
config.plugins.SpecialJump.specialJump6  = ConfigInteger(default  =  11, limits  = (1, 999))
config.plugins.SpecialJump.specialJump7  = ConfigInteger(default  =   7, limits  = (1, 999))
config.plugins.SpecialJump.smallSpecialJumpStart  = ConfigSelection([("1", "1"),("2", "2"),("3", "3"),("4", "4"),("5", "5"),("6", "6"),("7", "7")], default="3")

#SpecialJump infobar default coordinates
config.plugins.SpecialJump.bar_x         = ConfigInteger(default  =  70, limits  = (0, 1919))
config.plugins.SpecialJump.bar_y         = ConfigInteger(default  = 600, limits  = (0, 1079))
#SJJumpTime blended text default coordinates
#config.plugins.SpecialJump.bar_x         = ConfigInteger(default  = 400, limits  = (0, 1919))
#config.plugins.SpecialJump.bar_y         = ConfigInteger(default  =  50, limits  = (0, 1079))

config.plugins.SpecialJump.zap_x         = ConfigInteger(default  =  50, limits  = (0, 1919))
config.plugins.SpecialJump.zap_y         = ConfigInteger(default  = 500, limits  = (0, 1079))
config.plugins.SpecialJump.subs_x        = ConfigInteger(default  = 965, limits  = (0, 1919))
config.plugins.SpecialJump.subs_y        = ConfigInteger(default  =  30, limits  = (0, 1079))
config.plugins.SpecialJump.zapspeed_x    = ConfigInteger(default  =  30, limits  = (0, 1919))
config.plugins.SpecialJump.zapspeed_y    = ConfigInteger(default  =  30, limits  = (0, 1079))    
config.plugins.SpecialJump.audio_x       = ConfigInteger(default  =  30, limits  = (0, 1919))
config.plugins.SpecialJump.audio_y       = ConfigInteger(default  =  30, limits  = (0, 1079))
config.plugins.SpecialJump.audioVolume_x = ConfigInteger(default  =  30, limits  = (0, 1919))
config.plugins.SpecialJump.audioVolume_y = ConfigInteger(default  =  95, limits  = (0, 1079))

config.plugins.SpecialJump.LCDonOnEventChange             = ConfigYesNo(default=True)

config.plugins.SpecialJump.subs_anchor                    = ConfigSelection([("top", _("top")),("bottom", _("bottom"))], default="top")
config.plugins.SpecialJump.zapspeed_anchor                = ConfigSelection([("top", _("top")),("bottom", _("bottom"))], default="top")
config.plugins.SpecialJump.audio_anchor                   = ConfigSelection([("top", _("top")),("bottom", _("bottom"))], default="top")
config.plugins.SpecialJump.specialJumpTimeout_ms          = ConfigSelection(                           timeoutValues, default="2500")
config.plugins.SpecialJump.specialJumpMuteTime_ms         = ConfigSelection([("0", _("no mute"))]    + timeoutValues, default="0")
config.plugins.SpecialJump.jumpMuteTime_ms                = ConfigSelection([("0", _("no mute"))]    + timeoutValues, default="0")
config.plugins.SpecialJump.zapSpeedLimit_ms               = ConfigSelection(zapSpeedLimits, default="0")
config.plugins.SpecialJump.zapFromTimeshiftTime_ms        = ConfigSelection([("0", _("never zap"))]  + timeoutValues, default="2000")
config.plugins.SpecialJump.zapFromTimeshiftMessageTime_ms = ConfigSelection([("0", _("no message"))] + timeoutValues, default="1000")
config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms = ConfigSelection(protectValues, default="5000")
config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms = ConfigSelection(protectValues, default="1800000")
config.plugins.SpecialJump.zap_ProtectOnlyWhenBlanked     = ConfigYesNo(default=False)
config.plugins.SpecialJump.subToggleMode_single           = ConfigSelection([("12noff", _("1-2-n-off-1-2-n-off")), ("onoff", _("on-off-on-off"))], default="onoff")
config.plugins.SpecialJump.subToggleMode_multi            = ConfigSelection([("12noff", _("1-2-n-off-1-2-n-off")), ("onoff", _("on-off-on-off"))], default="12noff")

config.plugins.SpecialJump.subToggleVerbosity             = ConfigSelection([("off", _("no infobox")), ("single_line", _("single line")), ("line_per_track", _("one line per track"))], default="line_per_track")
config.plugins.SpecialJump.audioToggleVerbosity           = ConfigSelection([("off", _("no infobox")), ("single_line", _("single line")), ("line_per_track", _("one line per track"))], default="line_per_track")
config.plugins.SpecialJump.audioVolumeVerbosity           = ConfigSelection([("off", _("no infobox")), ("single_line", _("single line"))], default="single_line")
config.plugins.SpecialJump.zapspeedVerbosity              = ConfigSelection([("off", _("no infobox")), ("single_line", _("single line")), ("line_per_track", _("full statistics"))], default="line_per_track")

config.plugins.SpecialJump.subToggleTimeout_ms            = ConfigSelection(timeoutValues, default="1000")
config.plugins.SpecialJump.zapspeedTimeout_ms             = ConfigSelection(timeoutValues, default="3000")
config.plugins.SpecialJump.audioToggleTimeout_ms          = ConfigSelection(timeoutValues, default="1000")
config.plugins.SpecialJump.audioVolumeTimeout_ms          = ConfigSelection(timeoutValues, default="1000")

config.plugins.SpecialJump.audioVolumeTVorTSvideo         = ConfigSelection(audioVolumes, default="no_change")
config.plugins.SpecialJump.audioVolumeNonTSVideoTrack1    = ConfigSelection(audioVolumes, default="no_change")
config.plugins.SpecialJump.audioVolumeNonTSVideoTrack2    = ConfigSelection(audioVolumes, default="no_change")
config.plugins.SpecialJump.audioVolumeNonTSVideoTrack3    = ConfigSelection(audioVolumes, default="no_change")
config.plugins.SpecialJump.audioVolumeNonTSVideoTrack4    = ConfigSelection(audioVolumes, default="no_change")
config.plugins.SpecialJump.audioVolumeMuteDuringJump      = ConfigSelection(audioVolumes, default="0")

config.plugins.SpecialJump.EMCdirsHideOnPowerup           = ConfigYesNo(default=False)
config.plugins.SpecialJump.EMCdirsShowWindowTitle         = ConfigText(default = "EMC parental control")
config.plugins.SpecialJump.EMCdirsShowText                = ConfigText(default = "Enter PIN to show EMC hidden dirs")
config.plugins.SpecialJump.EMCdirsShowPin                 = ConfigInteger(default  = 0000, limits  = (0, 9999))

config.plugins.SpecialJump.fastZapEnable                  = ConfigYesNo(default=True)
config.plugins.SpecialJump.fastZapBenchmarkMode           = ConfigSelection(default = "false", choices = [("random", _("random")), ("random_stop", _("random, stop at error")), ("false", _("No")), ("just_zap", _("just zap")), ("just_zap_stop", _("just zap, stop at error"))])
config.plugins.SpecialJump.preloadIfSameTSID              = ConfigYesNo(default=True)
config.plugins.SpecialJump.fastZapMethod                  = ConfigSelection(choices = [("pip", _("Picture in Picture (debug only)")),("pip_hidden", _("Picture in Picture, hidden (not recommended)")),("record", _("fake recording"))],default = "record")
config.plugins.SpecialJump.zapspeedMeasureTimeout_ms      = ConfigInteger(default = 5500, limits  = (1, 99999))
config.plugins.SpecialJump.fastZapBenchmarkTime_ms        = ConfigInteger(default = 6000, limits  = (1, 99999))

config.plugins.SpecialJump.showSettingsGeneral            = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsKeymap             = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsFastZap            = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsInfobar            = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsSpecialJump        = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsFixedJump          = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsDualZap            = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsSubsAudio          = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.subToggleMode_single           = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsAudioVolumes       = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")
config.plugins.SpecialJump.showSettingsLCDBrightness      = ConfigSelection([("show", _("show")),("hide", _("hide"))], default="hide")

config.plugins.SpecialJump.separator = ConfigSelection([("na", " ")], default="na")

SpecialJumpInstance = None
baseInfoBarPlugins__init__ = None
base_ChannelSelection_setHistoryPath = None
base_InfoBarChannelSelection_zapUp = None
base_InfoBarChannelSelection_zapDown = None
base_ChannelSelection_zap = None
thisZapDirection = "None"

#----------------------------------------------------------------------

def autostart(reason, **kwargs):
	global baseInfoBarPlugins__init__
	global base_ChannelSelection_setHistoryPath
	global base_InfoBarChannelSelection_zapUp
	global base_InfoBarChannelSelection_zapDown
	global base_ChannelSelection_zap
	global SpecialJumpInstance
	if config.plugins.SpecialJump.enable.value:
		print "SpecialJump enabled: ",config.plugins.SpecialJump.enable.getValue()
		session = kwargs['session']
		if SpecialJumpInstance is None:
			SpecialJumpInstance = SpecialJump(session)
		if baseInfoBarPlugins__init__ is None:
			baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
		if base_ChannelSelection_setHistoryPath is None:
			base_ChannelSelection_setHistoryPath = ChannelSelection.setHistoryPath
		if base_InfoBarChannelSelection_zapUp is None:
			base_InfoBarChannelSelection_zapUp = InfoBarChannelSelection.zapUp
		if base_InfoBarChannelSelection_zapDown is None:
			base_InfoBarChannelSelection_zapDown = InfoBarChannelSelection.zapDown
		if base_ChannelSelection_zap is None:
			base_ChannelSelection_zap = ChannelSelection.zap
		ChannelSelection.setHistoryPath     = SJsetHistoryPath
		InfoBarChannelSelection.zapUp       = SJzapUp
		InfoBarChannelSelection.zapDown     = SJzapDown
		ChannelSelection.zap                = SJzap
		InfoBarPlugins.__init__ = InfoBarPlugins__init__
		InfoBarPlugins.specialjump_forwards             = specialjump_forwards
		InfoBarPlugins.specialjump_backwards            = specialjump_backwards
		InfoBarPlugins.specialjump_emcpin               = specialjump_emcpin
		InfoBarPlugins.specialjump_debugmessagebox      = specialjump_debugmessagebox
		InfoBarPlugins.specialjump_startTeletext        = specialjump_startTeletext
		InfoBarPlugins.specialjump_toggleSubtitleTrack_skipTeletext         = specialjump_toggleSubtitleTrack_skipTeletext
		InfoBarPlugins.specialjump_jump                 = specialjump_jump
		InfoBarPlugins.specialjump_toggleSubtitleTrack  = specialjump_toggleSubtitleTrack
		InfoBarPlugins.specialjump_toggleAudioTrack     = specialjump_toggleAudioTrack
		InfoBarPlugins.specialjump_channelDown          = specialjump_channelDown
		InfoBarPlugins.specialjump_channelUp            = specialjump_channelUp
		InfoBarPlugins.specialjump_doNothing            = specialjump_doNothing
		InfoBarPlugins.specialjump_clearDoubleAction    = specialjump_clearDoubleAction
		InfoBarPlugins.specialjump_jumpPreviousMark     = specialjump_jumpPreviousMark
		InfoBarPlugins.specialjump_jumpNextMark         = specialjump_jumpNextMark
		InfoBarPlugins.specialjump_toggleMark           = specialjump_toggleMark
		InfoBarPlugins.specialjump_toggleLCDBlanking    = specialjump_toggleLCDBlanking
		InfoBarPlugins.specialjump_toggleMarkIn         = specialjump_toggleMarkIn
		InfoBarPlugins.specialjump_toggleMarkOut        = specialjump_toggleMarkOut
		InfoBarPlugins.specialjump_callMovieCut         = specialjump_callMovieCut
		InfoBarPlugins.specialjump_callCutListEditor    = specialjump_callCutListEditor
		if reason == 0:
			if session is not None:
				if not session.nav.wasTimerWakeup() or session.nav.RecordTimer.getNextRecordingTime() > session.nav.RecordTimer.getNextZapTime():
					SpecialJump.powerOn(SpecialJumpInstance)
		else:
			SpecialJump.powerOff(SpecialJumpInstance)
		
def setup(session, **kwargs):
	session.open(SpecialJumpConfiguration)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("SpecialJump", setup, "SpecialJump_menu", 55)]
	return []

def Plugins(**kwargs):
	list = [PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart)]
	list.append(PluginDescriptor(name='SpecialJump', description=_('Fast manual skipping of commercials, and more...'), where=[PluginDescriptor.WHERE_PLUGINMENU], icon='SpecialJump.png', fnc=setup))
	list.append(PluginDescriptor(name='SpecialJump', description=_('Fast manual skipping of commercials, and more...'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=setup))
	if config.plugins.SpecialJump.mainmenu.value:
		list.append(PluginDescriptor(name='SpecialJump', description=_('Fast manual skipping of commercials, and more...'), where=[PluginDescriptor.WHERE_MENU], fnc=menu))
	return list

def InfoBarPlugins__init__(self):
	if isinstance(self, InfoBarShowMovies):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "isinstance(self, InfoBarShowMovies)"
		x = {'specialjump_forwards':        (boundFunction(self.specialjump_forwards,"MP","normal"),  'SpecialJump forwards'),
		 'specialjump_backwards':           (boundFunction(self.specialjump_backwards,"MP","normal"), 'SpecialJump backwards'),
		 'specialjump_forwards_small':      (boundFunction(self.specialjump_forwards,"MP","small"),  'SpecialJump forwards small'),
		 'specialjump_backwards_small':     (boundFunction(self.specialjump_backwards,"MP","small"), 'SpecialJump backwards small'),
		 'specialjump_jump1':               (boundFunction(self.specialjump_jump,"MP", "J1"), 'programmable jump 1'),
		 'specialjump_jump2':               (boundFunction(self.specialjump_jump,"MP", "J2"), 'programmable jump 2'),
		 'specialjump_jump3':               (boundFunction(self.specialjump_jump,"MP", "J3"), 'programmable jump 3'),
		 'specialjump_jump4':               (boundFunction(self.specialjump_jump,"MP", "J4"), 'programmable jump 4'),
		 'specialjump_jump5':               (boundFunction(self.specialjump_jump,"MP", "J5"), 'programmable jump 5'),
		 'specialjump_jump6':               (boundFunction(self.specialjump_jump,"MP", "J6"), 'programmable jump 6'),
		 'specialjump_jump7':               (boundFunction(self.specialjump_jump,"MP", "J7"), 'programmable jump 7'),
		 'specialjump_jump8':               (boundFunction(self.specialjump_jump,"MP", "J8"), 'programmable jump 8'),
		 'specialjump_jumpkey1':            (boundFunction(self.specialjump_jump,"MP", "K1"), 'programmable jump key 1'),
		 'specialjump_jumpkey4':            (boundFunction(self.specialjump_jump,"MP", "K4"), 'programmable jump key 4'),
		 'specialjump_jumpkey7':            (boundFunction(self.specialjump_jump,"MP", "K7"), 'programmable jump key 7'),
		 'specialjump_jumpkey3':            (boundFunction(self.specialjump_jump,"MP", "K3"), 'programmable jump key 3'),
		 'specialjump_jumpkey6':            (boundFunction(self.specialjump_jump,"MP", "K6"), 'programmable jump key 6'),
		 'specialjump_jumpkey9':            (boundFunction(self.specialjump_jump,"MP", "K9"), 'programmable jump key 9'),
		 'specialjump_channelDown':         (boundFunction(self.specialjump_channelDown,"MP"),    'KEY_CHANNELDOWN combined pause/zap function'),
		 'specialjump_channelUp':           (boundFunction(self.specialjump_channelUp,  "MP"),    'KEY_CHANNELUP   combined  play/zap function'),
		 'specialjump_jumpPreviousMark':    (boundFunction(self.specialjump_jumpPreviousMark,"MP"), 'jump to previous mark'),
		 'specialjump_jumpNextMark':        (boundFunction(self.specialjump_jumpNextMark,"MP"),     'jump to next mark'),
		 'specialjump_toggleMark':          (boundFunction(self.specialjump_toggleMark,"MP"),       'toggle mark'),
		 'specialjump_toggleMarkIn':        (boundFunction(self.specialjump_toggleMarkIn,"MP"),     'toggle mark in'),
		 'specialjump_toggleMarkOut':       (boundFunction(self.specialjump_toggleMarkOut,"MP"),    'toggle mark out'),
		 'specialjump_callMovieCut':        (boundFunction(self.specialjump_callMovieCut,"MP"),     'call MovieCut plugin'),
		 'specialjump_callCutListEditor':   (boundFunction(self.specialjump_callCutListEditor,"MP"),'call CutListEditor plugin'),
		 'specialjump_doNothing':           (self.specialjump_doNothing, 'do nothing'),
		 'specialjump_clearDoubleAction':   (self.specialjump_clearDoubleAction, 'avoid double action for certain keys, call on make'),
		 'specialjump_toggleSubtitleTrack': (self.specialjump_toggleSubtitleTrack, 'toggle subtitle track'),
		 'specialjump_toggleAudioTrack':    (self.specialjump_toggleAudioTrack,    'toggle audio track'),
		 'specialjump_toggleLCDBlanking':   (self.specialjump_toggleLCDBlanking,   'toggle LCD blanking'),
		 'specialjump_emcpin':              (self.specialjump_emcpin,              'enter parental control PIN for EMC hidden dirs'),
		 'specialjump_debugmessagebox':     (self.specialjump_debugmessagebox,     'show debug message box'),
		 'specialjump_startTeletext':       (self.specialjump_startTeletext,       'start teletext'),
		 'specialjump_toggleSubtitleTrack_skipTeletext':        (self.specialjump_toggleSubtitleTrack_skipTeletext,        'skip teletext activation')}
		self['SpecialJumpMoviePlayerActions'] = HelpableActionMap(self, 'SpecialJumpMoviePlayerActions', x, prio=-2) # -2 for priority over InfoBarSeek SeekActions seekdef:1 etc.
	elif isinstance(self, InfoBarEPG):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "isinstance(self, InfoBarEPG)"
		x = {'specialjump_forwards':        (boundFunction(self.specialjump_forwards,"TV","normal"),  'SpecialJump forwards'),
		 'specialjump_backwards':           (boundFunction(self.specialjump_backwards,"TV","normal"), 'SpecialJump backwards'),
		 'specialjump_forwards_small':      (boundFunction(self.specialjump_forwards,"TV","small"),  'SpecialJump forwards small'),
		 'specialjump_backwards_small':     (boundFunction(self.specialjump_backwards,"TV","small"), 'SpecialJump backwards small'),
		 'specialjump_jump1':               (boundFunction(self.specialjump_jump,"TV", "J1"), 'programmable jump 1'),
		 'specialjump_jump2':               (boundFunction(self.specialjump_jump,"TV", "J2"), 'programmable jump 2'),
		 'specialjump_jump3':               (boundFunction(self.specialjump_jump,"TV", "J3"), 'programmable jump 3'),
		 'specialjump_jump4':               (boundFunction(self.specialjump_jump,"TV", "J4"), 'programmable jump 4'),
		 'specialjump_jump5':               (boundFunction(self.specialjump_jump,"TV", "J5"), 'programmable jump 5'),
		 'specialjump_jump6':               (boundFunction(self.specialjump_jump,"TV", "J6"), 'programmable jump 6'),
		 'specialjump_jump7':               (boundFunction(self.specialjump_jump,"TV", "J7"), 'programmable jump 7'),
		 'specialjump_jump8':               (boundFunction(self.specialjump_jump,"TV", "J8"), 'programmable jump 8'),
		 'specialjump_jumpkey1':            (boundFunction(self.specialjump_jump,"TV", "K1"), 'programmable jump key 1'),
		 'specialjump_jumpkey4':            (boundFunction(self.specialjump_jump,"TV", "K4"), 'programmable jump key 4'),
		 'specialjump_jumpkey7':            (boundFunction(self.specialjump_jump,"TV", "K7"), 'programmable jump key 7'),
		 'specialjump_jumpkey3':            (boundFunction(self.specialjump_jump,"TV", "K3"), 'programmable jump key 3'),
		 'specialjump_jumpkey6':            (boundFunction(self.specialjump_jump,"TV", "K6"), 'programmable jump key 6'),
		 'specialjump_jumpkey9':            (boundFunction(self.specialjump_jump,"TV", "K9"), 'programmable jump key 9'),
		 'specialjump_jumpkey2':            (boundFunction(self.specialjump_jump,"TV", "K2"), 'number zap key 2'),
		 'specialjump_jumpkey5':            (boundFunction(self.specialjump_jump,"TV", "K5"), 'number zap key 5'),
		 'specialjump_jumpkey8':            (boundFunction(self.specialjump_jump,"TV", "K8"), 'number zap key 8'),
		 'specialjump_channelDown':         (boundFunction(self.specialjump_channelDown,"TV"),      'KEY_CHANNELDOWN combined pause/zap function'),
		 'specialjump_channelUp':           (boundFunction(self.specialjump_channelUp,  "TV"),      'KEY_CHANNELUP   combined  play/zap function'),
		 'specialjump_jumpPreviousMark':    (boundFunction(self.specialjump_jumpPreviousMark,"TV"), 'jump to previous mark'),
		 'specialjump_jumpNextMark':        (boundFunction(self,specialjump_jumpNextMark,"TV"),     'jump to next mark'),
		 'specialjump_toggleMark':          (boundFunction(self.specialjump_toggleMark,"TV"),       'toggle mark'),
		 'specialjump_toggleMarkIn':        (boundFunction(self.specialjump_toggleMarkIn,"TV"),     'toggle mark in'),
		 'specialjump_toggleMarkOut':       (boundFunction(self.specialjump_toggleMarkOut,"TV"),    'toggle mark out'),
		 'specialjump_callMovieCut':        (boundFunction(self.specialjump_callMovieCut,"TV"),     'call MovieCut plugin'),
		 'specialjump_callCutListEditor':   (boundFunction(self.specialjump_callCutListEditor,"TV"),'call CutListEditor plugin'),
		 'specialjump_doNothing':           (self.specialjump_doNothing, 'do nothing'),
		 'specialjump_clearDoubleAction':   (self.specialjump_clearDoubleAction, 'avoid double action for certain keys, call on make'),
		 'specialjump_toggleSubtitleTrack': (self.specialjump_toggleSubtitleTrack, 'toggle subtitle track'),
		 'specialjump_toggleAudioTrack':    (self.specialjump_toggleAudioTrack,    'toggle audio track'),
		 'specialjump_toggleLCDBlanking':   (self.specialjump_toggleLCDBlanking,   'toggle LCD blanking'),
		 'specialjump_emcpin':              (self.specialjump_emcpin,              'enter parental control PIN for EMC hidden dirs'),
		 'specialjump_debugmessagebox':     (self.specialjump_debugmessagebox,     'show debug message box'),
		 'specialjump_startTeletext':       (self.specialjump_startTeletext,       'start teletext'),
		 'specialjump_toggleSubtitleTrack_skipTeletext':        (self.specialjump_toggleSubtitleTrack_skipTeletext,        'skip teletext activation')}
		self['SpecialJumpActions'] = HelpableActionMap(self, 'SpecialJumpActions', x, prio=-2) # -2 for priority over InfoBarSeek SeekActions seekdef:1 etc.
	else:
		if config.plugins.SpecialJump.debugEnable.getValue(): print "NOT isinstance(self, ...)"
		InfoBarPlugins.__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.specialjump_doNothing = None
		InfoBarPlugins.specialjump_forwards = None
		InfoBarPlugins.specialjump_backwards = None
		InfoBarPlugins.specialjump_debugmessagebox = None
		InfoBarPlugins.specialjump_startTeletext = None
		InfoBarPlugins.specialjump_toggleSubtitleTrack_skipTeletext = None
		InfoBarPlugins.specialjump_emcpin = None
		InfoBarPlugins.specialjump_jump = None
		InfoBarPlugins.specialjump_toggleSubtitleTrack = None
		InfoBarPlugins.specialjump_clearDoubleAction = None
		InfoBarPlugins.specialjump_toggleAudioTrack = None
		InfoBarPlugins.specialjump_toggleLCDBlanking = None
		InfoBarPlugins.specialjump_channelDown = None
		InfoBarPlugins.specialjump_channelUp = None
		InfoBarPlugins.specialjump_jumpPreviousMark = None
		InfoBarPlugins.specialjump_jumpNextMark = None
		InfoBarPlugins.specialjump_toggleMark = None
		InfoBarPlugins.specialjump_toggleMarkIn = None
		InfoBarPlugins.specialjump_toggleMarkOut = None
		InfoBarPlugins.specialjump_callMovieCut = None
		InfoBarPlugins.specialjump_callCutListEditor = None
	baseInfoBarPlugins__init__(self)

def SJsetHistoryPath(self, doZap=True):
	# history zap is using ChannelSelection.setHistoryPath. Disable pseudo recordings before changing service (freeing the tuner), do predictive zap afterwards.
	SpecialJump.initInfoBar(SpecialJumpInstance,None) # 'self' isn't InfoBar, pass 'None'
	SpecialJump.initZapSpeedCounter(SpecialJumpInstance)
	SpecialJump.disablePredictiveRecOrPIP(SpecialJumpInstance)
	base_ChannelSelection_setHistoryPath(self,doZap)
	SpecialJump.zapHandler(SpecialJumpInstance,"zapDown") # P+
	global thisZapDirection
	thisZapDirection = "None" # for next zap caused by anything else than SJzapUp / SJzapDown

def SJzapUp(self):
	global thisZapDirection
	thisZapDirection = "zapUp"
	base_InfoBarChannelSelection_zapUp(self)
	
def SJzapDown(self):
	global thisZapDirection
	thisZapDirection = "zapDown"
	base_InfoBarChannelSelection_zapDown(self)

def SJzap(self, enable_pipzap=False, preview_zap=False, checkParentalControl=True, ref=None):
	global thisZapDirection
	# zapUp, zapDown, ChannelSelection are using ChannelSelection.zap.
	SpecialJump.initInfoBar(SpecialJumpInstance,None) # 'self' isn't InfoBar, pass 'None'
	SpecialJump.initZapSpeedCounter(SpecialJumpInstance)
	#now only done after zapping (TODO remove):
	#if thisZapDirection != SpecialJumpInstance.fastZapDirection: # guessed wrong
	#	SpecialJump.disablePredictiveRecOrPIP(SpecialJumpInstance)
	base_ChannelSelection_zap(self, enable_pipzap, preview_zap, checkParentalControl, ref)
	if thisZapDirection is not "None":
		SpecialJump.zapHandler(SpecialJumpInstance,thisZapDirection)
	else:
		SpecialJump.zapHandler(SpecialJumpInstance,"zapDown") # P+ is a good guess for the next zap
	thisZapDirection = "None" # for next zap caused by anything else than SJzapUp / SJzapDown

def specialjump_jumpPreviousMark(self,mode):
	if not SpecialJumpInstance.doubleActionFlag: # 'break' action suppressed after 'long' key action
		SpecialJump.jumpPreviousMark(SpecialJumpInstance,self,mode)

def specialjump_jumpNextMark(self,mode):
	if not SpecialJumpInstance.doubleActionFlag: # 'break' action suppressed after 'long' key action
		SpecialJump.jumpNextMark(SpecialJumpInstance,self,mode)

def specialjump_toggleMark(self,mode):
	if not SpecialJumpInstance.doubleActionFlag: # 'break' action suppressed after 'long' key action
		SpecialJump.toggleMark(SpecialJumpInstance,self,mode,InfoBarCueSheetSupport.CUT_TYPE_MARK)

def specialjump_toggleMarkIn(self,mode):
	SpecialJumpInstance.doubleActionFlag = True # 'long' press action, suppress 'break' action
	SpecialJump.toggleMark(SpecialJumpInstance,self,mode,InfoBarCueSheetSupport.CUT_TYPE_IN)

def specialjump_toggleMarkOut(self,mode):
	SpecialJumpInstance.doubleActionFlag = True # 'long' press action, suppress 'break' action
	SpecialJump.toggleMark(SpecialJumpInstance,self,mode,InfoBarCueSheetSupport.CUT_TYPE_OUT)

def specialjump_callMovieCut(self,mode):
	SpecialJumpInstance.doubleActionFlag = True # 'long' press action, suppress 'break' action
	SpecialJump.callMovieCut(SpecialJumpInstance,self,mode)

def specialjump_callCutListEditor(self,mode):
	SpecialJumpInstance.doubleActionFlag = True # 'long' press action, suppress 'break' action
	SpecialJump.callCutListEditor(SpecialJumpInstance,self,mode)

def specialjump_doNothing(self):
	pass

def specialjump_clearDoubleAction(self):
	SpecialJumpInstance.doubleActionFlag = False

def specialjump_channelDown(self,mode):
	#SpecialJump.showTimeBetweenKeys(SpecialJumpInstance)	
	SpecialJump.channelDown(SpecialJumpInstance,self,mode)

def specialjump_channelUp(self,mode):
	#SpecialJump.showTimeBetweenKeys(SpecialJumpInstance)	
	SpecialJump.channelUp(SpecialJumpInstance,self,mode)

def specialjump_forwards(self,mode,size):
	if   size == 'normal': SpecialJump.specialJumpForwards(SpecialJumpInstance,self,mode,0)
	elif size == 'small':  SpecialJump.specialJumpForwards(SpecialJumpInstance,self,mode,int(config.plugins.SpecialJump.smallSpecialJumpStart.getValue()))

def specialjump_backwards(self,mode,size):
	if   size == 'normal': SpecialJump.specialJumpBackwards(SpecialJumpInstance,self,mode,0)
	elif size == 'small':  SpecialJump.specialJumpBackwards(SpecialJumpInstance,self,mode,int(config.plugins.SpecialJump.smallSpecialJumpStart.getValue()))

def specialjump_jump(self,mode,jumpkey):
	#SpecialJump.showTimeBetweenKeys(SpecialJumpInstance)	
	if   jumpkey == 'J1': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump1.getValue()),config.plugins.SpecialJump.jump1action.getValue())
	elif jumpkey == 'J2': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump2.getValue()),config.plugins.SpecialJump.jump2action.getValue())
	elif jumpkey == 'J3': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump3.getValue()),config.plugins.SpecialJump.jump3action.getValue())
	elif jumpkey == 'J4': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump4.getValue()),config.plugins.SpecialJump.jump4action.getValue())
	elif jumpkey == 'J5': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump5.getValue()),config.plugins.SpecialJump.jump5action.getValue())
	elif jumpkey == 'J6': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump6.getValue()),config.plugins.SpecialJump.jump6action.getValue())
	elif jumpkey == 'J7': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump7.getValue()),config.plugins.SpecialJump.jump7action.getValue())
	elif jumpkey == 'J8': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "-", int( config.plugins.SpecialJump.jump8.getValue()),config.plugins.SpecialJump.jump8action.getValue())
	elif jumpkey == 'K1': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "1", int(-config.seek.selfdefined_13.getValue()), "nothing")
	elif jumpkey == 'K4': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "4", int(-config.seek.selfdefined_46.getValue()), "nothing")
	elif jumpkey == 'K7': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "7", int(-config.seek.selfdefined_79.getValue()), "nothing")
	elif jumpkey == 'K3': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "3", int( config.seek.selfdefined_13.getValue()), "nothing")
	elif jumpkey == 'K6': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "6", int( config.seek.selfdefined_46.getValue()), "nothing")
	elif jumpkey == 'K9': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "9", int( config.seek.selfdefined_79.getValue()), "nothing")
	elif jumpkey == 'K2': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "2", int( 0), "nothing")
	elif jumpkey == 'K5': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "5", int( 0), "nothing")
	elif jumpkey == 'K8': SpecialJump.fixedJump(SpecialJumpInstance, self, mode, "8", int( 0), "nothing")

def specialjump_toggleSubtitleTrack(self):
	SpecialJump.toggleSubtitleTrack(SpecialJumpInstance,self)

def specialjump_toggleAudioTrack(self):
	SpecialJump.toggleAudioTrack(SpecialJumpInstance,self)
	
def specialjump_toggleLCDBlanking(self):
	SpecialJump.toggleLCDBlanking(SpecialJumpInstance,self)
			
def specialjump_debugmessagebox(self):
	SpecialJump.debugmessagebox(SpecialJumpInstance,self)

def specialjump_startTeletext(self):
	SpecialJump.startTeletext(SpecialJumpInstance,self)

def specialjump_toggleSubtitleTrack_skipTeletext(self):
	SpecialJump.toggleSubtitleTrack(SpecialJumpInstance,self)
	SpecialJump.skipTeletext(SpecialJumpInstance,self)

def specialjump_emcpin(self):
	SpecialJump.specialJumpEMCpin(SpecialJumpInstance,self)
#----------------------------------------------------------------------

class SpecialJumpEventTracker(Screen):

	def __init__(self, session, parent):
		self.session = session
		Screen.__init__(self, session)
		self.labels = []
		self.SJChangedTimer = eTimer()
		self.SJChangedTimer.callback.append(self.serviceChanged_delayed)
		self.onClose.append(self.__onClose)
		self.onShow.append(self.__onShow)
		self.parent = parent

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evStart: self.__serviceChanged,
				iPlayableService.evEnd: self.__serviceChanged,
				iPlayableService.evUpdatedInfo: self.__serviceChanged,
				iPlayableService.evUpdatedEventInfo: self.__serviceChanged
			})

	def __serviceChanged(self):
		#if config.plugins.SpecialJump.debugEnable.getValue(): print "__serviceChanged"
		if not self.parent.SJMuteTimerActive:
			self.SJChangedTimer.start(100,1) #1 = once / false = repetitively

	def serviceChanged_delayed(self):
		#if config.plugins.SpecialJump.debugEnable.getValue(): print "serviceChanged_delayed 1"
		self.SJChangedTimer.stop()
		if self.parent is not None:
			#if config.plugins.SpecialJump.debugEnable.getValue(): print "serviceChanged_delayed 2"
			self.parent.checkSetNewVolumeOnChange()

			if not self.parent.SJLCDon and config.plugins.SpecialJump.LCDonOnEventChange.getValue():
				#if config.plugins.SpecialJump.debugEnable.getValue(): print "serviceChanged_delayed turned on LCD"
				self.parent.restoreLCDBrightness()

	def __onShow(self):
		pass

	def __onClose(self):
		self.SJChangedTimer.stop()

	def doShow(self):
		pass

	def doHide(self):
		pass

#----------------------------------------------------------------------

class SpecialJumpInfoBar(Screen):
	skin= """
	<screen name="SpecialJump_SpecialJumpInfoBar" title="SpecialJump InfoBar" flags="wfNoBorder" position="center,center" size="1135,70" zPosition="1" backgroundColor="black">
		<widget source="session.CurrentService" render="Label" position="180, 15" size="150,27" font="Arial;22" halign="left" backgroundColor="black" transparent="1" zPosition="3">
			<convert type="ServicePosition">Remaining</convert>
		</widget>
		<widget source="session.CurrentService" render="Label" position=" 920, 15" size=" 80,27" font="Arial;22" halign="right" backgroundColor="black" transparent="1" zPosition="3">
			<convert type="ServicePosition">Position</convert>
		</widget>
		<eLabel text="/" position="1010, 15" size=" 10,27" font="Arial;22" halign="center" backgroundColor="black" transparent="1" />
		<widget source="session.CurrentService" render="Label" position="1030, 15" size=" 80,27" font="Arial;22" halign="left" backgroundColor="black" transparent="1" zPosition="3">
			<convert type="ServicePosition">Length</convert>
		</widget>
		<widget source="session.CurrentService" render="Progress" position="  10,49" size="1120,8" pixmap="DMConcinnity-HD/progress.png" transparent="1" zPosition="3">
			<convert type="ServicePosition">Position</convert>
		</widget>
<!--##EMCsp##	    <widget source="Service" render="Progress" position="10,49" size="1120,8" zPosition="4" pixmap="DMConcinnity-HD/progress_rec.png" transparent="1">
			<convert type="EMCRecordPosition">Position</convert>
		</widget>
		<widget source="Service" render="Progress" position="10,49" size="1120,8" zPosition="5" pixmap="DMConcinnity-HD/progress.png" transparent="1">
			<convert type="EMCServicePosition">Position</convert>
		</widget>
		<widget source="Service" render="EMCPositionGauge" position="10,48" size="1120,10" zPosition="6" transparent="1">
			<convert type="EMCServicePosition">Gauge</convert>
		</widget>  -->
		<widget backgroundColor="black" font="Regular; 24" halign="left" name="SJJumpTime" position="300,15" size=" 350,27" transparent="1" />
	</screen>
	"""
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = ["SpecialJump_" + self.__class__.__name__] # 'SpecialJump_SpecialJumpInfoBar'
		self.labels = ["SJJumpTime"]
		for x in self.labels:
			self[x] = Label("")
		self.SJRefreshTimer = eTimer()
		self.SJRefreshTimer.callback.append(self.refreshInfoBar)
		self.onClose.append(self.__onClose)
		self.onShow.append(self.__onShow)
		self.parent = None
		self.localJumpTime = ""
		
		##EMCsp##self['Service'] = EMCCurrentService(session.nav, self.parent) # overwritten in doShow

	def __onShow(self):
		self.instance.move(ePoint(config.plugins.SpecialJump.bar_x.getValue(), config.plugins.SpecialJump.bar_y.getValue()))
		self.refreshInfoBar()

	def __onClose(self):
		self.SJRefreshTimer.stop()

	def doShow(self, parent, grandparent_InfoBar):
		##EMCsp##self['Service'] = EMCCurrentService(self.session.nav, grandparent_InfoBar) ### creates a new Components.Sources.EMCCurrentService.EMCCurrentService object, we don't want that
		##EMCsp##self['Service'] = grandparent_InfoBar['Service']                           ### gets Service from the Components.Sources.EMCCurrentService.EMCCurrentService object from EMCMediaCenter, not from EMCMoviePlayerSummary which we want
		self.parent = parent
		self.localJumpTime = self.parent.SJJumpTime
		self.show()

	def doHide(self):
		if self.shown:
			self.hide()

	def refreshInfoBar(self):
		try:
			if int(self.localJumpTime) < 0:
				self["SJJumpTime"].setText("jump -%d:%02d" % (abs(int(self.localJumpTime)) // 60, abs(int(self.localJumpTime)) % 60))
			else:
				self["SJJumpTime"].setText("jump +%d:%02d" % (self.localJumpTime // 60, self.localJumpTime % 60))
		except:
			self["SJJumpTime"].setText("%s" % self.localJumpTime) # not an int
		if self.shown:
			self.SJRefreshTimer.start(100,True)

#----------------------------------------------------------------------

class SpecialJumpInfoBarCuts(Screen):
	skin= """
	<screen name="SpecialJump_SpecialJumpInfoBarCuts" title="SpecialJump InfoBar" flags="wfNoBorder" position="center,center" size="1135,70" zPosition="1" backgroundColor="black">
		<widget source="session.CurrentService" render="Label" position="180, 15" size="150,27" font="Arial;22" halign="left" backgroundColor="black" transparent="1" zPosition="3">
			<convert type="ServicePosition">Remaining</convert>
		</widget>
		<widget source="session.CurrentService" render="Label" position=" 920, 15" size=" 80,27" font="Arial;22" halign="right" backgroundColor="black" transparent="1" zPosition="3">
			<convert type="ServicePosition">Position</convert>
		</widget>
		<eLabel text="/" position="1010, 15" size=" 10,27" font="Arial;22" halign="center" backgroundColor="black" transparent="1" />
		<widget source="session.CurrentService" render="Label" position="1030, 15" size=" 80,27" font="Arial;22" halign="left" backgroundColor="black" transparent="1" zPosition="3">
			<convert type="ServicePosition">Length</convert>
		</widget>
		<widget name="Timeline" position="10,49" size="1120,20" backgroundColor="#181818" pointer="skin_default/position_arrow.png:3,5" foregroundColor="blue" />
		<widget backgroundColor="black" font="Regular; 24" halign="left" name="SJJumpTime" position="300,15" size=" 350,27" transparent="1" />
	</screen>
	"""
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = ["SpecialJump_" + self.__class__.__name__] # 'SpecialJump_SpecialJumpInfoBarCuts'
		self.labels = ["SJJumpTime"]
		for x in self.labels:
			self[x] = Label("")
		self.SJRefreshTimer = eTimer()
		self.SJRefreshTimer.callback.append(self.refreshInfoBar)
		self.onClose.append(self.__onClose)
		self.onShow.append(self.__onShow)
		self.parent = None
		self.localJumpTime = ""
		self["Timeline"] = ServicePositionGauge(self.session.nav)
		
		#self['Service'] = EMCCurrentService(session.nav, self.parent) # overwritten in doShow

	def __onShow(self):
		self.instance.move(ePoint(config.plugins.SpecialJump.bar_x.getValue(), config.plugins.SpecialJump.bar_y.getValue()))
		self.refreshInfoBar()

	def __onClose(self):
		self.SJRefreshTimer.stop()

	def doShow(self, parent, grandparent_InfoBar):
		#self['Service'] = EMCCurrentService(self.session.nav, grandparent_InfoBar)
		self.parent = parent
		self.localJumpTime = self.parent.SJJumpTime
		self.show()

	def doHide(self):
		if self.shown:
			self.hide()

	def refreshInfoBar(self):
		try:
			if int(self.localJumpTime) < 0:
				self["SJJumpTime"].setText("jump -%d:%02d" % (abs(int(self.localJumpTime)) // 60, abs(int(self.localJumpTime)) % 60))
			else:
				self["SJJumpTime"].setText("jump +%d:%02d" % (self.localJumpTime // 60, self.localJumpTime % 60))
		except:
			self["SJJumpTime"].setText("%s" % self.localJumpTime) # not an int
		if self.shown:
			self.SJRefreshTimer.start(100,True)

#----------------------------------------------------------------------

class ZapMessage(Screen):
	skin= """
	<screen name="SpecialJump_ZapMessage" title="SpecialJump" flags="wfNoBorder" position="center,center" size="400,50" zPosition="1" backgroundColor="transparent">
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/images/ZapMessageBG.png" position="-1,2" size="400,50" zPosition="-1" />
		<widget backgroundColor="black" font="Regular; 24" halign="left" name="ZapMessageText" position="30,13" size=" 360,28" transparent="1" />
	</screen>
	"""
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = ["SpecialJump_" + self.__class__.__name__] # 'SpecialJump_ZapMessage'
		self.labels = ["ZapMessageText"]
		for x in self.labels:
			self[x] = Label("")
		self["ZapMessageText"].setText("timeshift active, 2* P+/P- = zap")
		self.parent = None

	def doShow(self, parent):
		self.instance.move(ePoint(config.plugins.SpecialJump.zap_x.getValue(), config.plugins.SpecialJump.zap_y.getValue()))
		self.parent = parent
		self.show()

	def doHide(self):
		if self.shown:
			self.hide()

#----------------------------------------------------------------------

class AudioSubsInfobox(Screen):
	skin= """
	<screen name="SpecialJump_AudioSubsInfobox_Audio" title="SpecialJump AudioSubsInfobox Audio" flags="wfNoBorder" position="center,center" size="300,20" zPosition="1" >
		<widget name="number"       position="0,0"   size="30,20"  zPosition="1" font="Regular;18" halign="right" transparent="1" />
		<widget name="description"  position="40,0"  size="100,20" zPosition="1" font="Regular;18" halign="left"  transparent="1" />
		<widget name="language"     position="150,0" size="100,20" zPosition="1" font="Regular;18" halign="left"  transparent="1" />
		<widget name="selected"     position="260,0" size="40,20"  zPosition="1" font="Regular;18" halign="left"  transparent="1" />
	</screen>
	"""
	
	def __init__(self, session, screenType):
		self.streams   = {}
		self.session   = session
		self.verbosity = 'off'
		self.anchor    = 'top'
		self.pos_x     = 10
		self.pos_y     = 10
		self.numLines_last = 1
		self.screenType = screenType # 'Audio' or 'Subs' or 'Volume'

		Screen.__init__(self, session)
		self.skinName = ["SpecialJump_" + self.__class__.__name__ + "_" + self.screenType] # 'SpecialJump_AudioSubsInfobox_Audio', 'SpecialJump_AudioSubsInfobox_Volume', 'SpecialJump_AudioSubsInfobox_Subs'
		self.labels = ["number","description","language","selected"]
		for x in self.labels:
			self[x] = Label("")

		#self.updateTimer = eTimer()
		#self.updateTimer.callback.append(self.updateInfo)
		self.onClose.append(self.__onClose)
		self.onShow.append(self.__onShow)
		self.onLayoutFinish.append(self.__onLayoutFinished)

	def __onLayoutFinished(self):
		for x in self.labels:
			self[x].instance.setNoWrap(1)
		self.def_size = self.instance.size()
		self.def_hreg = max(0, self.def_size.height() - self["description"].instance.size().height())
		if len(self.streams) == 0: self.reSize()

	def __onShow(self):
		#self.updateInfo()
		pass

	def __onClose(self):
		#self.updateTimer.stop()
		pass

	def updateInfo(self):
		lin = 0
		idx = 0
		fields = ["","","",""] # see self.labels
		for value in self.streams:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "updateInfo"
			if config.plugins.SpecialJump.debugEnable.getValue(): print value
			if (self.verbosity == 'line_per_track') or (idx == self.selected_track) or (self.screenType == 'Volume'):
				lin += 1
				if lin > 1:
					for x in range(len(fields)):
						fields[x] += '\n'
				fields[0] += "%s"%(value[0])
				fields[1] += "%s"%(value[1])
				fields[2] += "%s"%(value[2])
				fields[3] += "%s"%(value[3]) # "X " or " ", try to avoid white frame around black box that shows up when printing ""
			idx += 1
		if (self.verbosity == 'single_line') and (self.selected_track == -1) and (self.screenType != 'Volume'):
			fields[0] = " "
			fields[1] = "-"
			fields[2] = " "
			fields[3] = " "
			if self.screenType == 'Subs':
				fields[1] = "ST off"
		cnt = 0
		for x in self.labels:
			self[x].setText(fields[cnt])
			cnt += 1
		#if self.verbosity == 'single_line':
		#    numLines = 1
		#else:
		#    numLines = len(self.streams)
		#if self.numLines_last != numLines:
		#    self.numLines_last = numLines
		#    self.reSize()
		self.reSize()
		#if self.shown:
		#    self.updateTimer.start(500,True)

	def reSize(self):
		if len(self.streams) == 0:
			self.instance.resize(eSize(self.def_size.width(), 0))
		else:
			height = self["description"].instance.calculateSize().height() + 9
			for x in self.labels:
				self[x].instance.resize(eSize(self[x].instance.size().width(), height))
			height += self.def_hreg
			self.instance.resize(eSize(self.def_size.width(), height))
			if self.anchor == "bottom":
				y = self.pos_y + self.def_size.height() - height
			else:
				y = self.pos_y
			self.instance.move(ePoint(self.pos_x, y))

	def doShow(self, parent, streams, selected_track, verbosity, anchor, pos_x, pos_y):
		self.parent         = parent
		self.streams        = streams
		self.selected_track = selected_track
		self.verbosity      = verbosity
		self.anchor         = anchor
		self.pos_x          = pos_x
		self.pos_y          = pos_y
		self.show()
		self.updateInfo()

	def doHide(self):
		if self.shown:
			self.hide()

#----------------------------------------------------------------------

class SpecialJumpConfiguration(Screen, ConfigListScreen):
	skin= """
	<screen name="SpecialJump_SpecialJumpConfiguration" position="center,center" size="1100,605" title="SpecialJump Configuration" flags="wfNoBorder">
		<ePixmap position="0,0" zPosition="-10" size="1100,605" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/images/mainbg.png" />
		<widget source="global.CurrentTime" render="Label" position=" 20,20" size=" 80,25" font="Regular;23" foregroundColor="black" backgroundColor="white" transparent="1">
			<convert type="ClockToText">Default</convert>
		</widget>
		<widget source="global.CurrentTime" render="Label" position="110,20" size="140,25" font="Regular;23" foregroundColor="blue" backgroundColor="white" transparent="1">
			<convert type="ClockToText">Format:%d.%m.%Y</convert>
		</widget>
		<widget source="title" render="Label" position="270,15" size="800,43" font="Regular;35" halign="right" foregroundColor="black" backgroundColor="white" transparent="1" />
		<widget name="config" position="30,90" size="1040,440" itemHeight="30" scrollbarMode="showOnDemand" backgroundColor="black" transparent="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/buttons/red.png" position=" 30,570" size="35,27" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/buttons/green.png" position="290,570" size="35,27" alphatest="blend" />
		<widget source="key_red" render="Label" position=" 80,573" size="200,26" font="Regular;22" halign="left" foregroundColor="black" backgroundColor="grey" transparent="1" />
		<widget source="key_green" render="Label" position="340,573" size="200,26" font="Regular;22" halign="left" foregroundColor="black" backgroundColor="grey" transparent="1" />
	</screen>
	"""
	
	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)

		self.initConfigList()
		self.createConfigList()
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.skinName = ["SpecialJump_" + self.__class__.__name__] # 'SpecialJump_SpecialJumpConfiguration'
		
		self["title"] = StaticText(_("SpecialJump Configuration"))
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.save,
				"red": self.cancel,
				"save": self.save,
				"cancel": self.cancel,
				"ok": self.save,
			}, -2)

	def initConfigList(self):
		self.configList = [
		( _("__ General settings __"),                                                           0, config.plugins.SpecialJump.showSettingsGeneral),
		( _("Enable SpecialJump plugin [restart GUI]"),                                          1, config.plugins.SpecialJump.enable),
		( _("SpecialJump entry in main menu [restart GUI]"),                                     2, config.plugins.SpecialJump.mainmenu),
		( _("Enable SpecialJump debug output in normal logfile"),                                3, config.plugins.SpecialJump.debugEnable),
		( " ",                                                                                   4, config.plugins.SpecialJump.separator),
		( _("__ Keymap selection __"),                                                           0, config.plugins.SpecialJump.showSettingsKeymap),
		( _("Local keymap file"),                                                                1, config.plugins.SpecialJump.keymapFile),
		( _("Create your own keymap (instructions in the file):"),                               2, config.plugins.SpecialJump.separator),
		( "  /usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/keymap_user.xml",            3, config.plugins.SpecialJump.separator),
		( " ",                                                                                   4, config.plugins.SpecialJump.separator),
		( _("__ Fast zapping __"),                                                               0, config.plugins.SpecialJump.showSettingsFastZap),
		( _("Enable predictive fast zap mode"),                                                  1, config.plugins.SpecialJump.fastZapEnable),
		( _("Fast zap mode method of activating next channel"),                                  2, config.plugins.SpecialJump.fastZapMethod),
		( _("Auto-zap benchmark mode (debug only, random hit/miss/off)"),                        3, config.plugins.SpecialJump.fastZapBenchmarkMode),
		( _("Also preload next channel if it is on the same transponder (recommended)"),         4, config.plugins.SpecialJump.preloadIfSameTSID),
		( _("Enable zap speed measurement"),                                                     5, config.plugins.SpecialJump.zapspeed_enable),
		( _("Zap speed infobox verbosity"),                                                      6, config.plugins.SpecialJump.zapspeedVerbosity),
		( _("Zap speed infobox timeout"),                                                        7, config.plugins.SpecialJump.zapspeedTimeout_ms),
		( _("Zap speed infobox x position"),                                                     8, config.plugins.SpecialJump.zapspeed_x),
		( _("Zap speed infobox y position"),                                                     9, config.plugins.SpecialJump.zapspeed_y),
		( _("Zap speed infobox anchor"),                                                        10, config.plugins.SpecialJump.zapspeed_anchor),
		( _("Zap speed measurement timeout (zap error) [ms]"),                                  11, config.plugins.SpecialJump.zapspeedMeasureTimeout_ms),
		( _("Auto-zap benchmark mode time between zaps [ms]"),                                  12, config.plugins.SpecialJump.fastZapBenchmarkTime_ms),
		( " ",                                                                                  13, config.plugins.SpecialJump.separator),
		( _("__ Infobar settings __"),                                                           0, config.plugins.SpecialJump.showSettingsInfobar),
		( _("[OSD settings] Show infobar on skip (set to 'no' when using SpecialJump infobar)"), 1, config.usage.show_infobar_on_skip),
		( _("[Timeshift settings] Show timeshift infobar"),                                      2, config.timeshift.showinfobar),
		( _("Show SpecialJump infobar (set to 'yes')"),                                          3, config.plugins.SpecialJump.show_infobar),
		( _("Show SpecialJump infobar on jumpNextMark/jumpPreviousMark (set to 'yes')"),         4, config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark),
		( " ",                                                                                   5, config.plugins.SpecialJump.separator),
		( _("__ Special jump (fast manual skipping of commercials using 2 keys) __"),            0, config.plugins.SpecialJump.showSettingsSpecialJump),
		( _("Special jump 0 (initial value)"),                                                   1, config.plugins.SpecialJump.specialJump0),
		( _("Special jump 1 after 1st direction change"),                                        2, config.plugins.SpecialJump.specialJump1),
		( _("Special jump 2 (subsequent jump)"),                                                 3, config.plugins.SpecialJump.specialJump2),
		( _("Special jump 3 (subsequent jump)"),                                                 4, config.plugins.SpecialJump.specialJump3),
		( _("Special jump 4 (subsequent jump)"),                                                 5, config.plugins.SpecialJump.specialJump4),
		( _("Special jump 5 (subsequent jump)"),                                                 6, config.plugins.SpecialJump.specialJump5),
		( _("Special jump 6 (subsequent jump)"),                                                 7, config.plugins.SpecialJump.specialJump6),
		( _("Special jump 7 (subsequent jump)"),                                                 8, config.plugins.SpecialJump.specialJump7),
		( _("Special jump timeout"),                                                             9, config.plugins.SpecialJump.specialJumpTimeout_ms),
		( _("Mute after SpecialJump"),                                                          10, config.plugins.SpecialJump.specialJumpMuteTime_ms),
		( _("Small SpecialJump: start at initial value no."),                                   11, config.plugins.SpecialJump.smallSpecialJumpStart),
		( _("SpecialJump infobar x position"),                                                  12, config.plugins.SpecialJump.bar_x),
		( _("SpecialJump infobar y position"),                                                  13, config.plugins.SpecialJump.bar_y),
		( " ",                                                                                  14, config.plugins.SpecialJump.separator),
		( _("__ Programmable jumps using up to 8 keys __"),                                      0, config.plugins.SpecialJump.showSettingsFixedJump),
		( _("Programmable jump 1"),                                                              1, config.plugins.SpecialJump.jump1),
		( _("Programmable jump 1 action"),                                                       2, config.plugins.SpecialJump.jump1action),
		( _("Programmable jump 2"),                                                              3, config.plugins.SpecialJump.jump2),
		( _("Programmable jump 2 action"),                                                       4, config.plugins.SpecialJump.jump2action),
		( _("Programmable jump 3"),                                                              5, config.plugins.SpecialJump.jump3),
		( _("Programmable jump 3 action"),                                                       6, config.plugins.SpecialJump.jump3action),
		( _("Programmable jump 4"),                                                              7, config.plugins.SpecialJump.jump4),
		( _("Programmable jump 4 action"),                                                       8, config.plugins.SpecialJump.jump4action),
		( _("Programmable jump 5"),                                                              9, config.plugins.SpecialJump.jump5),
		( _("Programmable jump 5 action"),                                                      10, config.plugins.SpecialJump.jump5action),
		( _("Programmable jump 6"),                                                             11, config.plugins.SpecialJump.jump6),
		( _("Programmable jump 6 action"),                                                      12, config.plugins.SpecialJump.jump6action),
		( _("Programmable jump 7"),                                                             13, config.plugins.SpecialJump.jump7),
		( _("Programmable jump 7 action"),                                                      14, config.plugins.SpecialJump.jump7action),
		( _("Programmable jump 8"),                                                             15, config.plugins.SpecialJump.jump8),
		( _("Programmable jump 8 action"),                                                      16, config.plugins.SpecialJump.jump8action),
		( _("Mute after programmable jump"),                                                    17, config.plugins.SpecialJump.jumpMuteTime_ms),
		( " ",                                                                                  18, config.plugins.SpecialJump.separator),
		( _("__ Zap (dual function P+/P- and play/pause) __"),                                   0, config.plugins.SpecialJump.showSettingsDualZap),
		( _("Zap speed limit"),                                                                  1, config.plugins.SpecialJump.zapSpeedLimit_ms),
		( _("Zap from timeshift by pressing P+/P- twice within"),                                2, config.plugins.SpecialJump.zapFromTimeshiftTime_ms),
		( _("Zap from timeshift, warning message duration"),                                     3, config.plugins.SpecialJump.zapFromTimeshiftMessageTime_ms),
		( _("Zap from timeshift, warning message x position"),                                   4, config.plugins.SpecialJump.zap_x),
		( _("Zap from timeshift, warning message y position"),                                   5, config.plugins.SpecialJump.zap_y),
		( _("Protect large timeshift buffer in live TV (P+ required twice)"),                    6, config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms),
		( _("Protect large timeshift buffer in live TV (P- required twice)"),                    7, config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms),
		( _("Protect large timeshift buffer only in cinema mode (LCD brighness off, see below)"),8, config.plugins.SpecialJump.zap_ProtectOnlyWhenBlanked),
		( " ",                                                                                   9, config.plugins.SpecialJump.separator),
		( _("__ Subtitle and audio toggling with a single key each __"),                         0, config.plugins.SpecialJump.showSettingsSubsAudio),
		( _("Subtitle toggle mode when pressing key only once within infobox timeout"),          1, config.plugins.SpecialJump.subToggleMode_single),
		( _("Subtitle toggle mode when pressing multiple times within infobox timeout"),         2, config.plugins.SpecialJump.subToggleMode_multi),
		( _("Subtitle toggle infobox timeout"),                                                  3, config.plugins.SpecialJump.subToggleTimeout_ms),
		( _("Subtitle toggle infobox verbosity"),                                                4, config.plugins.SpecialJump.subToggleVerbosity),
		( _("Subtitle infobox x position"),                                                      5, config.plugins.SpecialJump.subs_x),
		( _("Subtitle infobox y position"),                                                      6, config.plugins.SpecialJump.subs_y),
		( _("Subtitle infobox anchor"),                                                          7, config.plugins.SpecialJump.subs_anchor),
		( _("Audio toggle infobox timeout"),                                                     8, config.plugins.SpecialJump.audioToggleTimeout_ms),
		( _("Audio toggle infobox verbosity"),                                                   9, config.plugins.SpecialJump.audioToggleVerbosity),
		( _("Audio toggle infobox x position"),                                                 10, config.plugins.SpecialJump.audio_x),
		( _("Audio toggle infobox y position"),                                                 11, config.plugins.SpecialJump.audio_y),
		( _("Audio toggle infobox anchor"),                                                     12, config.plugins.SpecialJump.audio_anchor),
		( " ",                                                                                  13, config.plugins.SpecialJump.separator),
		( _("__ Fixed audio volumes (when remove controls TV volume) __"),                       0, config.plugins.SpecialJump.showSettingsAudioVolumes),
		( _("Volume for TV and recorded TV (.ts files)"),                                        1, config.plugins.SpecialJump.audioVolumeTVorTSvideo),
		( _("Volume for non .ts videos, audio track 1"),                                         2, config.plugins.SpecialJump.audioVolumeNonTSVideoTrack1),
		( _("Volume for non .ts videos, audio track 2"),                                         3, config.plugins.SpecialJump.audioVolumeNonTSVideoTrack2),
		( _("Volume for non .ts videos, audio track 3"),                                         4, config.plugins.SpecialJump.audioVolumeNonTSVideoTrack3),
		( _("Volume for non .ts videos, audio track 4"),                                         5, config.plugins.SpecialJump.audioVolumeNonTSVideoTrack4),
		( _("Volume for (nearly) muting after a jump"),                                          6, config.plugins.SpecialJump.audioVolumeMuteDuringJump),
		( _("Volume infobox timeout"),                                                           7, config.plugins.SpecialJump.audioVolumeTimeout_ms),
		( _("Volume infobox x position"),                                                        8, config.plugins.SpecialJump.audioVolume_x),
		( _("Volume infobox y position"),                                                        9, config.plugins.SpecialJump.audioVolume_y),
		( _("Volume infobox verbosity"),                                                        10, config.plugins.SpecialJump.audioVolumeVerbosity),
		( _("[from AV menu] Audio auto volume level"),                                          11, config.av.autovolume),
		( " ",                                                                                  12, config.plugins.SpecialJump.separator),
		( _("__ Toggle LCD brightness by key __"),                                               0, config.plugins.SpecialJump.showSettingsLCDBrightness),
		( _("Turn LCD on again on event change"),                                                1, config.plugins.SpecialJump.LCDonOnEventChange),
		]

	def createConfigList(self):
		list = []
		for i, conf in enumerate( self.configList ):
			# 0 entry text
			# 1 visibility looking up
			# 2 config variable
			if (conf[1] == 0) or (self.configList[i-conf[1]][2].getValue() == "show"):
				list.append(getConfigListEntry(conf[0], conf[2]))
		self.list = list
		
	def changedEntry(self):
		self.createConfigList()
		self["config"].setList(self.list)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		self.changedEntry()
		global SpecialJumpInstance
		SpecialJump.reloadKeymap(SpecialJumpInstance)
		self.close(True,self.session)

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Quit without saving changes ?"), MessageBox.TYPE_YESNO, default = False)
		else:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False,self.session)

	def cancelConfirm(self, result):
		if result is None or result is False:
			pass
		else:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False,self.session)

#----------------------------------------------------------------------
		
class SpecialJump():

	def __init__(self,session):
		self.session = session
		config.misc.standbyCounter.addNotifier(self._onStandby, initial_call = False)
		self.session.nav.record_event.append(self.gotRecordEvent)
		
		self.SJLCDon = True                    # for toggling LCD brightness
		if config.plugins.SpecialJump.debugEnable.getValue(): print "__init__ SJLCDon = True"
		self.SJNextJumpIndex = 0               # next jump (0 = before 1st direction change)        
		self.SJLastJumpDir   = 0               # last jump direction (0=none, 1=forward, -1=backward)        
		self.SJJumpTime      = 0               # accumulated jump time since last timeout        
		self.SJPreMuteVolume = -1              # -1 = no value stored
		self.SJLastSubsTrack = 0               # last subtitle track in "onoff" toggle mode
		self.SJMode="--"                       # TV or MoviePlayer mode
		self.SJLastInitialJump = 0             # last value of "initialJump" (for starting over again when changing between full and small SpecialJump)
		self.SJAudioBoxTimerActive     = False # timer for audio infobox is (not) active
		self.SJSubsBoxTimerActive      = False # timer for subtitle infobox is (not) active
		self.SJZapspeedBoxTimerActive  = False # timer for zap speed infobox is (not) active
		self.SJMuteTimerActive         = False # timer for muting is (not) active
		self.SJZapTimerActive          = False # for zapping speed limit: timer starts when last zapped
		self.SJZapUpTimerActive        = False # for zapping from timeshift instead of play/pause by pressing KEY_CHANNELUP/DOWN twice quickly: time starts when last "zap up" was blocked
		self.SJZapDownTimerActive      = False # for zapping from timeshift instead of play/pause by pressing KEY_CHANNELUP/DOWN twice quickly: time starts when last "zap down" was blocked
		self.skipTeletextActivation = False    # see below
		self.fastZapDirection = None           # predictive zap direction for fast zapping
		self.fastZapPipActive = False          # invisible PIP window active (for fast zapping)
		self.fastZapRecService = None          # pseudo recording service (for fast zapping)
		
		self.SJTimer=eTimer()                  # timer for specialJump timeout
		self.SJTimer.timeout.get().append(self.specialJumpTimeout)
		self.SJMuteTimer=eTimer()              # timer for specialJump muting
		self.SJMuteTimer.timeout.get().append(self.specialJumpUnmute)
		self.SJZapMessageTimer=eTimer()        # timer for zapping from timeshift, timeout for message window
		self.SJZapMessageTimer.timeout.get().append(self.specialJumpZapMessageTimeout)
		self.SJAudioBoxTimer=eTimer()          # timer for audio infobox
		self.SJAudioBoxTimer.timeout.get().append(self.specialJumpAudioBoxTimeout)
		self.SJAudioVolumeBoxTimer=eTimer()    # timer for audio volumeinfobox
		self.SJAudioVolumeBoxTimer.timeout.get().append(self.specialJumpAudioVolumeBoxTimeout)
		self.SJSubsBoxTimer=eTimer()           # timer for subtitle infobox
		self.SJSubsBoxTimer.timeout.get().append(self.specialJumpSubsBoxTimeout)
		self.SJZapspeedBoxTimer=eTimer()       # timer for zap speed display
		self.SJZapspeedBoxTimer.timeout.get().append(self.specialJumpZapspeedBoxTimeout)
		self.SJZapspeedPollTimer=eTimer()      # timer for zap speed detection
		self.SJZapspeedPollTimer.timeout.get().append(self.specialJumpZapspeedPollTimeout)
		self.SJZapUpTimer=eTimer()             # timer for zapping from timeshift (up)
		self.SJZapUpTimer.timeout.get().append(self.specialJumpZapUpTimeout)
		self.SJZapDownTimer=eTimer()           # timer for zapping from timeshift (down)
		self.SJZapDownTimer.timeout.get().append(self.specialJumpZapDownTimeout)
		self.SJZapTimer=eTimer()               # timer for zapping speed limit
		self.SJZapTimer.timeout.get().append(self.specialJumpZapTimeout)
		self.SJZapBenchmarkTimer=eTimer()         # timer for fast zap benchmark mode
		self.SJZapBenchmarkTimer.timeout.get().append(self.zapDown)
		self.executeCyclicTimer=eTimer() 
		self.executeCyclicTimer.timeout.get().append(self.executeCyclic)
		self.gotRecordEventTimer=eTimer() 
		self.gotRecordEventTimer.timeout.get().append(self.gotRecordEventDelayed)
	   		
		self.InfoBar_instance         = None # always passed as an argument
		# always use self.InfoBar_instance from parent (not global InfoBar.instance):
		# there are separate InfoBar.instance.seekstate for InfoBarEPG and InfoBarShowMovies
		#   probably InfoBarShowMovies inherits the unique SpecialJump instance from InfoBarEPG
		#   use self.InfoBar_instance to get the seekstate from the correct parent InfoBar
		# without this, KEY_PAUSE handled by MP would pause (setting InfoBarShowMovies seekstate to "PAUSE"),
		#   but then KEY_CHANNELUP handled by SJ would not play (InfoBarEPG seekstate is constantly "PLAY")
		#   so  InfoBarSeek.unPauseService(InfoBar.instance) would do nothing
		#   but InfoBarSeek.unPauseService(self.InfoBar_instance) correctly uses InfoBarShowMovies seekstate

		self.starttime = self.getTime_ms()
		
		self.doubleActionFlag = False                  # avoid double action ('break' and 'long') for certain keys, set to False on 'make'
		
		self.volctrl = eDVBVolumecontrol.getInstance() # volume control # dirty
		
		# initialize local windows
		self.SpecialJumpInfoBar_instance      = self.session.instantiateDialog(SpecialJumpInfoBar)
		self.SpecialJumpInfoBarCuts_instance  = self.session.instantiateDialog(SpecialJumpInfoBarCuts)
		self.SpecialJumpEventTracker_instance = self.session.instantiateDialog(SpecialJumpEventTracker, self)
		self.ZapMessage_instance              = self.session.instantiateDialog(ZapMessage)
		self.AudioToggleInfobox_instance      = self.session.instantiateDialog(AudioSubsInfobox, 'Audio')
		self.AudioVolumeInfobox_instance      = self.session.instantiateDialog(AudioSubsInfobox, 'Volume')
		self.SubsToggleInfobox_instance       = self.session.instantiateDialog(AudioSubsInfobox, 'Subs')
		self.zapspeedInfobox_instance         = self.session.instantiateDialog(AudioSubsInfobox, 'Zapspeed')
		
		# for zap speed display
		self.services_hd_plus = ['1:0:19:151A:455:1:C00000:0:0:0:', '1:0:19:2E9B:411:1:C00000:0:0:0:', '1:0:19:2EAF:411:1:C00000:0:0:0:', '1:0:19:5274:41D:1:C00000:0:0:0:', '1:0:19:EF10:421:1:C00000:0:0:0:', '1:0:19:EF11:421:1:C00000:0:0:0:', '1:0:19:EF14:421:1:C00000:0:0:0:', '1:0:19:EF15:421:1:C00000:0:0:0:', '1:0:19:EF74:3F9:1:C00000:0:0:0:', '1:0:19:EF75:3F9:1:C00000:0:0:0:', '1:0:19:EF76:3F9:1:C00000:0:0:0:', '1:0:19:EF77:3F9:1:C00000:0:0:0:', '1:0:19:EF78:3F9:1:C00000:0:0:0:']
		self.services_hd_free = ['1:0:19:283D:3FB:1:C00000:0:0:0:', '1:0:19:283E:3FB:1:C00000:0:0:0:', '1:0:19:283F:3FB:1:C00000:0:0:0:', '1:0:19:2859:401:1:C00000:0:0:0:', '1:0:19:285B:401:1:C00000:0:0:0:', '1:0:19:286E:425:1:C00000:0:0:0:', '1:0:19:286F:425:1:C00000:0:0:0:', '1:0:19:2870:425:1:C00000:0:0:0:', '1:0:19:2873:425:1:C00000:0:0:0:', '1:0:19:2887:40F:1:C00000:0:0:0:', '1:0:19:2888:40F:1:C00000:0:0:0:', '1:0:19:2889:40F:1:C00000:0:0:0:', '1:0:19:2B66:3F3:1:C00000:0:0:0:', '1:0:19:2B7A:3F3:1:C00000:0:0:0:', '1:0:19:2B84:3F3:1:C00000:0:0:0:', '1:0:19:2B8E:3F2:1:C00000:0:0:0:', '1:0:19:2B98:3F2:1:C00000:0:0:0:', '1:0:19:2BA2:3F2:1:C00000:0:0:0:', '1:0:19:6EA5:4B1:1:C00000:0:0:0:']
		self.services_sd_free = ['1:0:1:1146:404:1:C00000:0:0:0:', '1:0:1:272E:402:1:C00000:0:0:0:', '1:0:1:2742:402:1:C00000:0:0:0:', '1:0:1:2753:402:1:C00000:0:0:0:', '1:0:1:2EE3:441:1:C00000:0:0:0:', '1:0:1:2EF4:441:1:C00000:0:0:0:', '1:0:1:2F08:441:1:C00000:0:0:0:', '1:0:1:2F1C:441:1:C00000:0:0:0:', '1:0:1:2F1D:441:1:C00000:0:0:0:', '1:0:1:2F3A:441:1:C00000:0:0:0:', '1:0:1:308:5:85:C00000:0:0:0:', '1:0:1:33:21:85:C00000:0:0:0:', '1:0:1:384:21:85:C00000:0:0:0:', '1:0:1:3F:21:85:C00000:0:0:0:', '1:0:1:445C:453:1:C00000:0:0:0:', '1:0:1:445D:453:1:C00000:0:0:0:', '1:0:1:445E:453:1:C00000:0:0:0:', '1:0:1:445F:453:1:C00000:0:0:0:', '1:0:1:4461:453:1:C00000:0:0:0:', '1:0:1:7004:436:1:C00000:0:0:0:', '1:0:1:701:5:85:C00000:0:0:0:', '1:0:1:7036:41B:1:C00000:0:0:0:', '1:0:1:79E0:443:1:C00000:0:0:0:', '1:0:1:79F4:443:1:C00000:0:0:0:']
		self.zap_time_event_counter    = 0
		self.zap_error_counter         = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
		self.zap_time_event_counter_ms = 50
		self.zap_time                  = 0
		self.zap_time_res_0_seen       = False
		self.zap_success               = 'off'
		self.zapPredictiveService      = None
		self.zap_time_nums = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
		self.zap_time_sums = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
		self.zap_list_ind1  = ['off', 'miss', 'fast']
		self.zap_list_ind2  = ['HD+', 'HD', 'SD', '??', 'tot']
		
		self.lastZapTime = None
		
		self.activeKeyMap = "keymap_classic.xml"
		self.reloadKeymap()

	def reloadKeymap(self):
		if config.plugins.SpecialJump.keymapFile.getValue() != self.activeKeyMap:
			error = False
			keymap = os.path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/SpecialJump/"), self.activeKeyMap)
			if fileExists(keymap):
				try:
					keymapparser.removeKeymap(keymap)
					print "keymap for plugin SpecialJump (%s) removed." % keymap
				except Exception, exc:
					print "keymap for plugin SpecialJump (%s) failed to remove: " % keymap, exc
					error = True
			else:
				print "keymap for plugin SpecialJump (%s) not found for removal." % keymap
				error = True

			keymap = os.path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/SpecialJump/"), config.plugins.SpecialJump.keymapFile.getValue())
			if fileExists(keymap):
				try:
					keymapparser.readKeymap(keymap)
					print "keymap for plugin SpecialJump (%s) loaded." % keymap
					self.activeKeyMap = config.plugins.SpecialJump.keymapFile.getValue()
				except Exception, exc:
					print "keymap for plugin SpecialJump (%s) failed to load: " % keymap, exc
					error = True
			else:
				print "keymap for plugin SpecialJump (%s) not found." % keymap
				error = True
				
			os.system("ln -fs %s %s" % (keymap, os.path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/SpecialJump/"), "keymap.xml")))
				
			if error:
				self.session.open(MessageBox,_("Could not change keymap. Check that files exist and see log file for details."), type = MessageBox.TYPE_ERROR,timeout = 30)
				
	def showTimeBetweenKeys(self):
		if self.lastZapTime is not None:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "Time since last KEY:",datetime.now()-self.lastZapTime
		self.lastZapTime = datetime.now()

	def powerOn(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "powerOn"
		self.SJLCDon = True
		self.fastZapPipActive = False
		if config.plugins.SpecialJump.EMCdirsHideOnPowerup.getValue():
			try:
				#/etc/engima2/emc-hide.cfg
				config.EMC.cfghide_enable.setValue(True)
			except:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "could not set config.EMC.cfghide_enable True"
			if SpecialJumpPrivateAddonsInst is not None:
				SpecialJumpPrivateAddons.SJprivateHide(SpecialJumpPrivateAddonsInst)
		
	def powerOff(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "powerOff"
		pass

	def _onStandby(self, element):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "_onStandby"
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.powerOn)
		self.powerOff()

	def gotRecordEvent(self, service, event):
		if event == iRecordableService.evRecordStopped:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "evRecordStopped starting timer"
			self.gotRecordEventTimer.start(500)

	def gotRecordEventDelayed(self):
		self.gotRecordEventTimer.stop()
		if len(NavigationInstance.instance.getRecordings(False,pNavigation.isFromSpecialJumpFastZap)) == 0:
			#pseudo recording was stopped externally (e.g. in RecordTimer.py) to free a tuner, null the pointer so that the tuner is no longer blocked
			if config.plugins.SpecialJump.debugEnable.getValue(): print "evRecordStopped externally, nulling the pointer of the pseudo recording"
			self.fastZapRecService = None

	def specialJumpEMCpin(self,parent):
		from Screens.InputBox import PinInput
		self.session.openWithCallback(self.checkEMCpin, PinInput, pinList=[config.plugins.SpecialJump.EMCdirsShowPin.getValue()], triesEntry=config.ParentalControl.retries.servicepin, title=config.plugins.SpecialJump.EMCdirsShowText.getValue(), windowTitle=config.plugins.SpecialJump.EMCdirsShowWindowTitle.getValue())

	def checkEMCpin(self, ret):
		if ret is not None:
			if ret:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "EMC PIN correct"
				try:
					config.EMC.cfghide_enable.setValue(False)
				except:
					if config.plugins.SpecialJump.debugEnable.getValue(): print "could not set config.EMC.cfghide_enable False"
				if SpecialJumpPrivateAddonsInst is not None:
					SpecialJumpPrivateAddons.SJprivateShow(SpecialJumpPrivateAddonsInst)
			else:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "EMC PIN incorrect"

		
	def specialJumpValue(self,index):
		#I want arrays ...
		if index == 0:
			value = config.plugins.SpecialJump.specialJump0.getValue()
		elif index == 1:
			value = config.plugins.SpecialJump.specialJump1.getValue()
		elif index == 2:
			value = config.plugins.SpecialJump.specialJump2.getValue()
		elif index == 3:
			value = config.plugins.SpecialJump.specialJump3.getValue()
		elif index == 4:
			value = config.plugins.SpecialJump.specialJump4.getValue()
		elif index == 5:
			value = config.plugins.SpecialJump.specialJump5.getValue()
		elif index == 6:
			value = config.plugins.SpecialJump.specialJump6.getValue()
		else:
			value = config.plugins.SpecialJump.specialJump7.getValue()
		return value

	def specialJumpStartTimerShowInfoBar(self, withCuts, muteTime_ms):
		self.SJTimer.stop()
		self.SJTimer.start(int(config.plugins.SpecialJump.specialJumpTimeout_ms.getValue()))
		if withCuts:
			self.SpecialJumpInfoBarCuts_instance.doShow(self,self.InfoBar_instance) # grandparent_InfoBar
		else:
			if config.plugins.SpecialJump.show_infobar.getValue():
				self.SpecialJumpInfoBar_instance.doShow(self,self.InfoBar_instance) # grandparent_InfoBar
		if muteTime_ms>0:
			self.specialJumpMute(muteTime_ms)

	def specialJumpMute(self, muteTime_ms):
		if int(muteTime_ms) > 0:
			if self.SJPreMuteVolume == -1: # -1 = no value stored
				self.SJPreMuteVolume = self.volctrl.getVolume()
				self.setAudioVolume(config.plugins.SpecialJump.audioVolumeMuteDuringJump.getValue())
			self.SJMuteTimer.stop()
			self.SJMuteTimer.start(int(muteTime_ms))
			self.SJMuteTimerActive = True
		   
	def specialJumpShowZapWarning(self):
		self.SJZapMessageTimer.stop()
		self.SJZapMessageTimer.start(int(config.plugins.SpecialJump.zapFromTimeshiftMessageTime_ms.getValue()))
		self.ZapMessage_instance.doShow(self)
		   
	def specialJumpStartTimerShowAudioBox(self, streams, selected_track):
		verbosity = config.plugins.SpecialJump.audioToggleVerbosity.getValue()
		anchor    = config.plugins.SpecialJump.audio_anchor.getValue()
		pos_x     = config.plugins.SpecialJump.audio_x.getValue()
		pos_y     = config.plugins.SpecialJump.audio_y.getValue()
		self.SJAudioBoxTimer.stop()
		self.SJAudioBoxTimer.start(int(config.plugins.SpecialJump.audioToggleTimeout_ms.getValue()))
		self.SJAudioBoxTimerActive = True
		if verbosity != 'off':
			self.AudioToggleInfobox_instance.doShow(self, streams, selected_track, verbosity, anchor, pos_x, pos_y)
		   
	def specialJumpStartTimerShowAudioVolumeBox(self, volume):
		verbosity = config.plugins.SpecialJump.audioVolumeVerbosity.getValue()
		anchor    = 'top'
		pos_x     = config.plugins.SpecialJump.audioVolume_x.getValue()
		pos_y     = config.plugins.SpecialJump.audioVolume_y.getValue()
		self.SJAudioVolumeBoxTimer.stop()
		self.SJAudioVolumeBoxTimer.start(int(config.plugins.SpecialJump.audioVolumeTimeout_ms.getValue()))
		streams = []
		streams.append(('','volume',volume,''))
		if verbosity != 'off':
			self.AudioVolumeInfobox_instance.doShow(self, streams, -1, verbosity, anchor, pos_x, pos_y)
		   
	def specialJumpStartTimerShowSubsBox(self, streams, selected_track):
		verbosity = config.plugins.SpecialJump.subToggleVerbosity.getValue()
		anchor    = config.plugins.SpecialJump.subs_anchor.getValue()
		pos_x     = config.plugins.SpecialJump.subs_x.getValue()
		pos_y     = config.plugins.SpecialJump.subs_y.getValue()
		self.SJSubsBoxTimer.stop()
		self.SJSubsBoxTimer.start(int(config.plugins.SpecialJump.subToggleTimeout_ms.getValue()))
		self.SJSubsBoxTimerActive = True
		if verbosity != 'off':
			self.SubsToggleInfobox_instance.doShow(self, streams, selected_track, verbosity, anchor, pos_x, pos_y)
		   
	def specialJumpStartTimerShowZapspeedBox(self,ind1):
		verbosity = config.plugins.SpecialJump.zapspeedVerbosity.getValue()
		anchor    = config.plugins.SpecialJump.zapspeed_anchor.getValue()
		pos_x     = config.plugins.SpecialJump.zapspeed_x.getValue()
		pos_y     = config.plugins.SpecialJump.zapspeed_y.getValue()
		self.SJZapspeedBoxTimer.stop()
		self.SJZapspeedBoxTimer.start(int(config.plugins.SpecialJump.zapspeedTimeout_ms.getValue()))
		self.SJZapspeedBoxTimerActive = True
		streams = []
		streams.append(('','%s zap t=' % (self.zap_list_ind1[ind1]), '%sms' % (self.zap_time),''))
		for ind1 in range(0, len(self.zap_list_ind1)):
			streams.append(('','','',''))
			for ind2 in range(0, len(self.zap_list_ind2)):
				if ind2 == self.zap_list_ind2.index('tot'):
					zap_errors = ''
				else:
					zap_errors = self.zap_error_counter[ind1][ind2]
					if zap_errors == 0:
						zap_errors = ''
				streams.append((zap_errors,'t %s %s' % (self.zap_list_ind1[ind1],self.zap_list_ind2[ind2]), '%dms' % (self.myDivide(self.zap_time_sums[ind1][ind2],self.zap_time_nums[ind1][ind2])),self.zap_time_nums[ind1][ind2]))
			streams.append((self.zap_error_counter[ind1][self.zap_list_ind2.index('tot')],'zap errors','>%dms' % (config.plugins.SpecialJump.zapspeedMeasureTimeout_ms.getValue()),''))

		if verbosity != 'off':
			self.zapspeedInfobox_instance.doShow(self, streams, 0, verbosity, anchor, pos_x, pos_y)
		   
	def myDivide(self,a,b):
		if (b==0):
			return -1
		return a/b
		   
	def specialJumpStartZapUpTimer(self):
		self.SJZapUpTimer.stop()
		self.SJZapUpTimer.start(int(config.plugins.SpecialJump.zapFromTimeshiftTime_ms.getValue()))
		self.SJZapUpTimerActive = True
		   
	def specialJumpStartZapDownTimer(self):
		self.SJZapDownTimer.stop()
		self.SJZapDownTimer.start(int(config.plugins.SpecialJump.zapFromTimeshiftTime_ms.getValue()))
		self.SJZapDownTimerActive = True
		   
	def specialJumpStartZapTimer(self):
		self.SJZapTimer.stop()
		self.SJZapTimer.start(int(config.plugins.SpecialJump.zapSpeedLimit_ms.getValue()))
		self.SJZapTimerActive = True
		   
	def specialJumpTimeout(self):
		self.SJNextJumpIndex = 0
		self.SJLastJumpDir   = 0
		self.SJJumpTime      = 0
		self.SJTimer.stop()
		self.SpecialJumpInfoBar_instance.doHide()
		self.SpecialJumpInfoBarCuts_instance.doHide()

	def specialJumpUnmute(self):
		self.SJMuteTimer.stop()
		self.SJMuteTimerActive = False
		self.setAudioVolume(self.SJPreMuteVolume)
		self.SJPreMuteVolume = -1 # -1 = no value stored

	def specialJumpZapMessageTimeout(self):
		self.SJZapMessageTimer.stop()
		self.ZapMessage_instance.doHide()
 
	def specialJumpAudioBoxTimeout(self):
		self.SJAudioBoxTimer.stop()
		self.SJAudioBoxTimerActive = False
		self.AudioToggleInfobox_instance.doHide()
 
	def specialJumpAudioVolumeBoxTimeout(self):
		self.SJAudioVolumeBoxTimer.stop()
		self.AudioVolumeInfobox_instance.doHide()
 
	def specialJumpSubsBoxTimeout(self):
		self.SJSubsBoxTimer.stop()
		self.SJSubsBoxTimerActive = False
		self.SubsToggleInfobox_instance.doHide()

	def specialJumpZapspeedBoxTimeout(self):
		self.SJZapspeedBoxTimer.stop()
		self.SJZapspeedBoxTimerActive = False
		self.zapspeedInfobox_instance.doHide()

	def specialJumpZapspeedPollTimeout(self):
		self.zap_time_event_counter += 1
		#if config.plugins.SpecialJump.debugEnable.getValue(): print "specialJumpZapspeedPollTimeout ",self.zap_time_event_counter
		ind1 = self.zap_list_ind1.index(self.zap_success)
		cur = self.InfoBar_instance.servicelist.getCurrentSelection()
		if cur:
			cur = cur.toString()            
			if cur in self.services_hd_plus:
				ind2 = self.zap_list_ind2.index('HD+')
			elif cur in self.services_hd_free:
				ind2 = self.zap_list_ind2.index('HD')
			elif cur in self.services_sd_free:
				ind2 = self.zap_list_ind2.index('SD')
			else:
				ind2 = self.zap_list_ind2.index('??')
		else:
			ind2 = self.zap_list_ind2.index('??')
		if self.zap_time_event_counter == config.plugins.SpecialJump.zapspeedMeasureTimeout_ms.getValue() / self.zap_time_event_counter_ms:
			if self.zap_time_res_0_seen:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "illegal zap time"
				if (config.plugins.SpecialJump.fastZapBenchmarkMode.value == "just_zap_stop") or (config.plugins.SpecialJump.fastZapBenchmarkMode.value == "random_stop"):
					self.SJZapBenchmarkTimer.stop()
				self.SJZapspeedPollTimer.stop()
				self.zap_error_counter[ind1][ind2] += 1
				self.zap_error_counter[ind1][self.zap_list_ind2.index('tot')] += 1
			else:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "could not determine zap time (yres 0 not seen until timeout)"
				self.SJZapspeedPollTimer.stop()
		else:
			if path.exists('/proc/stb/vmpeg/0/yres'):
				try:
					f = open('/proc/stb/vmpeg/0/yres', 'r')
					video_height = int(f.read(), 16)
					f.close()
				except:
					video_height = 0
				if video_height == 0:
					self.zap_time_res_0_seen = True
				elif self.zap_time_res_0_seen:
					self.zap_time = self.zap_time_event_counter * self.zap_time_event_counter_ms
					self.SJZapspeedPollTimer.stop()

					self.zap_time_sums[ind1][ind2] += self.zap_time
					self.zap_time_nums[ind1][ind2] += 1

					ind2 = self.zap_list_ind2.index('tot')
					self.zap_time_sums[ind1][ind2] += self.zap_time
					self.zap_time_nums[ind1][ind2] += 1
					
					self.specialJumpStartTimerShowZapspeedBox(ind1)
						
	def specialJumpZapUpTimeout(self):
		self.SJZapUpTimer.stop()
		self.SJZapUpTimerActive = False

	def specialJumpZapDownTimeout(self):
		self.SJZapDownTimer.stop()
		self.SJZapDownTimerActive = False

	def specialJumpZapTimeout(self):
		self.SJZapTimer.stop()
		self.SJZapTimerActive = False
 
	def specialJumpBackwards(self,parent,mode,initialJump):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if initialJump != self.SJLastInitialJump:
			self.SJLastInitialJump = initialJump
			self.SJLastJumpDir = 0 # start over when changing between full and small SpecialJump
		if InfoBar and self.InfoBar_instance:
			if self.SJLastJumpDir    == 0:
				self.SJNextJumpIndex  = initialJump # 0 for full specialJump
			elif self.SJLastJumpDir  == 1:
				self.SJNextJumpIndex += 1
			elif self.SJNextJumpIndex > initialJump:
				self.SJNextJumpIndex += 1

			self.SJJumpTime     -= self.specialJumpValue(self.SJNextJumpIndex)
			self.SJLastJumpDir   = -1
			self.activateTimeshiftIfNecessaryAndDoSeekRelative(- self.specialJumpValue(self.SJNextJumpIndex) * 90000, config.plugins.SpecialJump.specialJumpMuteTime_ms.getValue())                
			
	def specialJumpForwards(self,parent,mode,initialJump):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if initialJump != self.SJLastInitialJump:
			self.SJLastInitialJump = initialJump
			self.SJLastJumpDir = 0 # start over when changing between full and small SpecialJump
		if InfoBar and self.InfoBar_instance:
			if self.SJLastJumpDir    == 0:
				self.SJNextJumpIndex  = initialJump # 0 for full specialJump
			elif self.SJLastJumpDir == -1:
				self.SJNextJumpIndex += 1
			elif self.SJNextJumpIndex > initialJump:
				self.SJNextJumpIndex += 1

			self.SJJumpTime     += self.specialJumpValue(self.SJNextJumpIndex)
			self.SJLastJumpDir   = 1
			self.activateTimeshiftIfNecessaryAndDoSeekRelative(self.specialJumpValue(self.SJNextJumpIndex) * 90000, config.plugins.SpecialJump.specialJumpMuteTime_ms.getValue())

	def debugMessage(self,locationString):
		if config.plugins.SpecialJump.debugEnable.getValue():
			print '-----------------------------------------'
			print '[SpecialJump] ', locationString
			print '-----------------------------------------'
			seek = self.getSeek()
			print 'self.InfoBar_instance:', self.InfoBar_instance
			print 'seek:', seek
			if seek.isCurrentlySeekable():
				print "is  seek.isCurrentlySeekable()"
			else:
				print "not seek.isCurrentlySeekable()"
			length  = seek.getLength()
			playpos = seek.getPlayPosition()
			print 'length/pos', length[1]/90000, playpos[1]/90000
			if isinstance(self.InfoBar_instance, InfoBarShowMovies):
				print "Infobar is MoviePlayer"
			if isinstance(self.InfoBar_instance, InfoBarEPG):
				print "Infobar is InfoBar"
			print '-----------------------------------------'

	def fixGigablueDriverProb(self,locationString):
		#short version: getting length and pos seems to help
		seek = self.getSeek()
		length  = seek.getLength()
		playpos = seek.getPlayPosition()
			
	def activateTimeshiftIfNecessaryAndDoSeekRelative(self, pts, MuteTime_ms):
		if config.plugins.SpecialJump.debugEnable.getValue(): print 'activateTimeshiftIfNecessaryAndDoSeekRelative', pts, ' ', MuteTime_ms
		if InfoBar and self.InfoBar_instance:
			seek = self.getSeek()
			if seek is not None:
				if not seek.isCurrentlySeekable():
					# need to activate timeshift first
					InfoBarTimeshift.activateTimeshiftEndAndPause(self.InfoBar_instance)
					InfoBarSeek.unPauseService(self.InfoBar_instance)
				needPauseService = False
				if self.isSeekstatePaused():
					# workaround for the bug that, when paused, multiple jumps are not possible (only the last one has effect at a time)
					self.unPauseService()
					needPauseService = True
				InfoBarSeek.doSeekRelative(self.InfoBar_instance, pts)
				if needPauseService:
					# workaround part II
					self.pauseService()
				self.specialJumpStartTimerShowInfoBar(False, MuteTime_ms)
			#else:
			#	self.session.open(MessageBox,_("no seek"), type = MessageBox.TYPE_ERROR,timeout = 2)
		else:
			self.session.open(MessageBox,_("no (InfoBar and self.InfoBar_instance)"), type = MessageBox.TYPE_ERROR,timeout = 2)
			
	def channelDown(self,parent,mode):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if mode == "MP":
			self.pauseService()
		if mode == "TV":
			if self.isCurrentlySeekable(): # timeshift active and play position "in the past"
				if self.SJZapDownTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "A-"
					self.zapUp() # zapUp = P-
				else:
					if self.isSeekstatePaused():
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "B-"
						self.specialJumpStartZapDownTimer()
						self.specialJumpShowZapWarning()
					else:
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "C-"
						self.pauseService()
			else: # live TV
				if self.SJZapDownTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "D-"
					self.zapUp() # zapUp = P-
				else:
					length = self.getTimeshiftFileSize_kB() # length of timeshift buffer (estimated: 1kB ~ 1ms)
					if (length > int(config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms.getValue())) and not (int(config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms.getValue()) == -1) and (not self.SJLCDon or not config.plugins.SpecialJump.zap_ProtectOnlyWhenBlanked.getValue()): # protect timeshift buffer unless "no protection" is selected
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "E-"
						self.specialJumpStartZapDownTimer()
						self.specialJumpShowZapWarning()
						InfoBarTimeshift.activateTimeshiftEndAndPause(self.InfoBar_instance) # not just self.pauseService()
					else: # zap with speed limit
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "F-"
						if not self.SJZapTimerActive:
							#if config.plugins.SpecialJump.debugEnable.getValue(): print "G-"
							self.zapUp() # zapUp = P-
							self.SJZapDownTimer.stop()

	def channelUp(self,parent,mode):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if mode == "MP":
			self.unPauseService()
		if mode == "TV":
			if self.isCurrentlySeekable(): # timeshift active and play position "in the past"
				if self.SJZapUpTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "A+"
					#InfoBarTimeshift.stopTimeshift(self.InfoBar_instance) # not just zap, or zapping will be impossible for ~2s -- didn't help
					self.zapDown() # zapDown = P+
				else:
					if not self.isSeekstatePaused():
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "B+"
						self.specialJumpStartZapUpTimer()
						self.specialJumpShowZapWarning()
					else:
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "C+"
						self.unPauseService()
			else: # live TV
				if self.SJZapUpTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "D+"
					self.zapDown() # zapDown = P+
				else:
					length = self.getTimeshiftFileSize_kB() # length of timeshift buffer (estimated: 1kB ~ 1ms)
					if (length > int(config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms.getValue())) and not (int(config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms.getValue()) == -1) and (not self.SJLCDon or not config.plugins.SpecialJump.zap_ProtectOnlyWhenBlanked.getValue()): # protect timeshift buffer unless "no protection" is selected
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "E+"
						self.specialJumpStartZapUpTimer()
						self.specialJumpShowZapWarning()
					else: # zap with speed limit
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "F+"
						if not self.SJZapTimerActive:
							#if config.plugins.SpecialJump.debugEnable.getValue(): print "G+"
							self.zapDown() # zapDown = P+
							self.SJZapUpTimer.stop()

	def zapUp(self):
		self.specialJumpStartZapTimer()
		self.SJZapBenchmarkTimer.stop()
		self.InfoBar_instance.LongButtonPressed = False # do not treat as PIP zap even when pressed long
		try:
			self.InfoBar_instance.pts_blockZap_timer.stop()
		except:
			print "self.InfoBar_instance.pts_blockZap_timer.stop() failed in zapUp"
		global thisZapDirection
		thisZapDirection = "zapUp"
		base_InfoBarChannelSelection_zapUp(self.InfoBar_instance)     
				
	def zapDown(self):
		self.specialJumpStartZapTimer()
		self.InfoBar_instance.LongButtonPressed = False # do not treat as PIP zap even when pressed long
		try:
			self.InfoBar_instance.pts_blockZap_timer.stop()
		except:
			print "self.InfoBar_instance.pts_blockZap_timer.stop() failed in zapDown"
		global thisZapDirection
		thisZapDirection = "zapDown"
		base_InfoBarChannelSelection_zapDown(self.InfoBar_instance)

	def initInfoBar(self,parent):
		if parent is not None:
			self.InfoBar_instance = parent
		else:
			self.InfoBar_instance = InfoBar.instance # SJsetHistoryPath always requires standard (not EMC) InfoBar.instance
			# note: if this doesn't work in all cases, make a copy of self.InfoBar_instance everywhere if mode == "TV" and use it here

	def initZapSpeedCounter(self):
		if config.plugins.SpecialJump.zapspeed_enable.value:
			self.SJZapspeedPollTimer.start(self.zap_time_event_counter_ms,False)#repetitive
			self.zap_time_res_0_seen = False
		self.zap_time_event_counter = 0

	def zapHandler(self,direction):
		if config.plugins.SpecialJump.fastZapEnable.value and self.zapPredictiveService is not None:
			cur = self.InfoBar_instance.servicelist.getCurrentSelection()
			if cur:
				cur = cur.toString()
				if cur == self.zapPredictiveService:
					# fast zap due to previously active PIP on the new channel
					if config.plugins.SpecialJump.debugEnable.getValue(): print self.fastZapDirection," PIP predictive zap success"
					self.zap_success = 'fast'
				else:
					self.zap_success = 'miss'
					if config.plugins.SpecialJump.debugEnable.getValue(): print self.fastZapDirection," PIP predictive zap guessed wrong, is ",cur," exp. ",self.zapPredictiveService
		else:
			self.zap_success = 'off'
		
		if config.plugins.SpecialJump.fastZapBenchmarkMode.value != "false":
			if (config.plugins.SpecialJump.fastZapBenchmarkMode.value == "random") or (config.plugins.SpecialJump.fastZapBenchmarkMode.value == "random_stop"):
				rand = randint(0,2)
				if config.plugins.SpecialJump.debugEnable.getValue(): print "Benchmark Mode ",rand
				if rand == 0: # 33% fast zap
					config.plugins.SpecialJump.fastZapEnable.setValue(True)
				elif rand == 1: # 33% inverted direction for intentional wrong prediction
					config.plugins.SpecialJump.fastZapEnable.setValue(True)
					if direction == "zapDown":
						direction = "zapUp"
					else:
						direction == "zapDown"
				else: # 33% fast zap mode off
					config.plugins.SpecialJump.fastZapEnable.setValue(False)
			self.SJZapBenchmarkTimer.start(config.plugins.SpecialJump.fastZapBenchmarkTime_ms.getValue()) # auto zap
		else:
			self.SJZapBenchmarkTimer.stop()
				
		if config.plugins.SpecialJump.fastZapEnable.value and self.getNumberOfFrontendsFreeForSJ() > 1:
			self.fastZapDirection = direction
			if (config.plugins.SpecialJump.fastZapMethod.value == "pip") or (config.plugins.SpecialJump.fastZapMethod.value == "pip_hidden"):
				if (self.fastZapPipActive == False):
					if (InfoBarPiP.pipShown(self.InfoBar_instance) == False):
						if config.plugins.SpecialJump.debugEnable.getValue(): print direction," zapPredictive incl. initial showPiP"
						self.postZap_preloadPredictive()
					else:
						if config.plugins.SpecialJump.debugEnable.getValue(): print direction," PIP unexpectedly active, don't touch PIP",InfoBarPiP.pipShown(self.InfoBar_instance)
				else:
					if (InfoBarPiP.pipShown(self.InfoBar_instance) == True):
						if config.plugins.SpecialJump.debugEnable.getValue(): print direction," zapPredictive (PIP already active)"
						self.postZap_preloadPredictive()
					else:
						if config.plugins.SpecialJump.debugEnable.getValue(): print direction," zapPredictive (PIP unexpectedly inactive)",InfoBarPiP.pipShown(self.InfoBar_instance)
						self.postZap_preloadPredictive()
			else:
				if config.plugins.SpecialJump.debugEnable.getValue(): print direction," start zapPredictive (pseudo rec.)"
				self.postZap_preloadPredictive()
		else:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "disabling FastZap temporarily (only %d free tuner(s) available)" % self.getNumberOfFrontendsFreeForSJ()
			if (self.fastZapPipActive == True):
				#not using PIP any more, restore size and turn off PIP
				self.session.pip.instance.move(ePoint(config.av.pip.value[0],config.av.pip.value[1]))
				self.session.pip.instance.resize(eSize(*(config.av.pip.value[2],config.av.pip.value[3])))
				self.session.pip["video"].instance.resize(eSize(*(config.av.pip.value[2],config.av.pip.value[3])))
			self.disablePredictiveRecOrPIP()

	def postZap_preloadPredictive(self):
		#start PIP or pseudo recording on the expected next service
		if config.plugins.SpecialJump.debugEnable.getValue(): print "zapPredictive 1"
		self.disablePredictiveRecOrPIP()
		
		storeService = self.InfoBar_instance.servicelist.getCurrentSelection()

		if self.fastZapDirection == "zapDown":
			#predictive zapDown: same algorithm as in InfoBarGenerics/zapDown
			if self.InfoBar_instance.servicelist.inBouquet():
				prev = self.InfoBar_instance.servicelist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.value and self.InfoBar_instance.servicelist.atEnd():
							self.InfoBar_instance.servicelist.nextBouquet()
							self.InfoBar_instance.servicelist.moveTop()
						else:
							self.InfoBar_instance.servicelist.moveDown()
						cur = self.InfoBar_instance.servicelist.getCurrentSelection()
						if cur:
							if self.InfoBar_instance.servicelist.dopipzap:
								isPlayable = self.session.pip.isPlayableForPipService(cur)
							else:
								isPlayable = isPlayableForCur(cur)
						if cur and (cur.toString() == prev or isPlayable):
							break
			else:
				self.InfoBar_instance.servicelist.moveDown()
		else:
			#predictive zapUp: same algorithm as in InfoBarGenerics/zapUp
			if self.InfoBar_instance.servicelist.inBouquet():
				prev = self.InfoBar_instance.servicelist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.value and self.InfoBar_instance.servicelist.atBegin():
							self.InfoBar_instance.servicelist.prevBouquet()
							self.InfoBar_instance.servicelist.moveEnd()
						else:
							self.InfoBar_instance.servicelist.moveUp()
						cur = self.InfoBar_instance.servicelist.getCurrentSelection()
						if cur:
							if self.InfoBar_instance.servicelist.dopipzap:
								isPlayable = self.session.pip.isPlayableForPipService(cur)
							else:
								isPlayable = isPlayableForCur(cur)
						if cur and (cur.toString() == prev or isPlayable):
							break
			else:
				self.InfoBar_instance.servicelist.moveUp()

		fastZapNextService = self.InfoBar_instance.servicelist.getCurrentSelection()
		
		if self.compareTSIDandNamespace(storeService,fastZapNextService) and not config.plugins.SpecialJump.preloadIfSameTSID.value:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "FastZap not preloading the next service as it is on the same transponder"
			self.zapPredictiveService = None
		else:		
			self.enablePredictiveRecOrPIP(fastZapNextService)
			self.zapPredictiveService = fastZapNextService.toString()

		self.InfoBar_instance.servicelist.setCurrentSelection(storeService)
		if config.plugins.SpecialJump.debugEnable.getValue(): print "zapPredictive 2"
														
	def enablePredictiveRecOrPIP(self, fastZapNextService):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "enablePredictiveRecOrPIP ",fastZapNextService.toString()
		if (config.plugins.SpecialJump.fastZapMethod.value == "pip") or (config.plugins.SpecialJump.fastZapMethod.value == "pip_hidden"):
			if (InfoBarPiP.pipShown(self.InfoBar_instance) == False):
				InfoBarPiP.showPiP(self.InfoBar_instance)
				self.fastZapPipActive = True
				fastZapNextService = self.session.pip.resolveAlternatePipService(fastZapNextService)
				if fastZapNextService:
					self.session.pip.playService(fastZapNextService)
					if config.plugins.SpecialJump.debugEnable.getValue(): print "zapPredictive ",self.fastZapDirection," switched PIP to service ",fastZapNextService.toString()
					if config.plugins.SpecialJump.fastZapMethod.value == "pip":
						self.session.pip.instance.move(ePoint(config.av.pip.value[0],config.av.pip.value[1]))
						self.session.pip.instance.resize(eSize(*(config.av.pip.value[2],config.av.pip.value[3])))
						self.session.pip["video"].instance.resize(eSize(*(config.av.pip.value[2],config.av.pip.value[3])))
					elif config.plugins.SpecialJump.fastZapMethod.value == "pip_hidden":
						self.session.pip.instance.move(ePoint(0, 0))
						self.session.pip.instance.resize(eSize(*(0, 0)))
						self.session.pip["video"].instance.resize(eSize(*(0, 0)))
						self.session.pip.setSizePosMainWindow(0,0,0,0) #------------------------- could be good against black screen ---------
		else:
			#fake recording from enigma2-plugins/epgrefresh/src/RecordAdapter.py
			try:
				#not all images support recording types
				self.fastZapRecService = self.session.nav.recordService(fastZapNextService,False,pNavigation.isPseudoRecording|pNavigation.isFromSpecialJumpFastZap)
			except:
				self.fastZapRecService = self.session.nav.recordService(fastZapNextService)
			if self.fastZapRecService is not None:
				self.fastZapRecService.prepareStreaming()
				self.fastZapRecService.start()
				if config.plugins.SpecialJump.debugEnable.getValue(): print "zapPredictive ",self.fastZapDirection," pseudo recording service ",fastZapNextService.toString()

	def disablePredictiveRecOrPIP(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "disablePredictiveRecOrPIP"
		if (self.fastZapPipActive == True) and (InfoBarPiP.pipShown(self.InfoBar_instance) == True):
			#disable PIP
			InfoBarPiP.showPiP(self.InfoBar_instance)
			self.fastZapPipActive = False
		if self.fastZapRecService is not None:
			#disable fake recording
			self.session.nav.stopRecordService(self.fastZapRecService)
			self.fastZapRecService = None
			self.zapPredictiveService = None
			
	def compareTSIDandNamespace(self, service1, service2):
		namespace1 = ServiceReference(service1).ref.getUnsignedData(4) # NAMESPACE
		tsid1      = ServiceReference(service1).ref.getUnsignedData(2) # TSID
		namespace2 = ServiceReference(service2).ref.getUnsignedData(4) # NAMESPACE
		tsid2      = ServiceReference(service2).ref.getUnsignedData(2) # TSID
		if (namespace1 and tsid1 and namespace2 and tsid2):
			if config.plugins.SpecialJump.debugEnable.getValue(): print "check whether next service is on same transponder: (%04x,%04x) vs. (%04x,%04x)" % (namespace1,tsid1,namespace2,tsid2)
			return (namespace1 and tsid1 and namespace2 and tsid2 and (namespace1 == namespace2) and (tsid1 == tsid2))
		else:
			return False
	
	def pauseService(self):
		if InfoBar and self.InfoBar_instance:
			InfoBarSeek.pauseService(self.InfoBar_instance)
			
	def unPauseService(self):
		if InfoBar and self.InfoBar_instance:
			InfoBarSeek.unPauseService(self.InfoBar_instance)

	def SJnumberEntered(self, service = None, bouquet = None):
		if service:
			self.InfoBar_instance.selectAndStartService(service, bouquet)
			
	def fixedJump(self,parent,mode,number,time_seconds,action):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if InfoBar and self.InfoBar_instance:
			if (mode == "TV") and (number != "-") and not self.isCurrentlySeekable(): # live TV: NumberZap
				#self.session.openWithCallback(self.InfoBar_instance.numberEntered, NumberZap, number, self.InfoBar_instance.searchNumber)
				self.session.openWithCallback(self.SJnumberEntered, NumberZap, number, self.InfoBar_instance.searchNumber)
			else: # no NumberZap
				doJump  = True
				doMute  = True
				doSubs  = False
				doAudio = False
				if (action == "audio1"):
					self.setAudioTrack(0)
					doMute = False
					doAudio = True
				if (action == "audio2"):
					self.setAudioTrack(1)
					doMute = False
					doAudio = True
				if (action == "audio3"):
					self.setAudioTrack(2)
					doMute = False
					doAudio = True
				if (action == "audio4"):
					self.setAudioTrack(3)
					doMute = False
					doAudio = True
				if (action == "sub1"):
					self.setSubtitleTrack(0)
					doSubs = True
				if (action == "sub2"):
					self.setSubtitleTrack(1)
					doSubs = True
				if (action == "sub3"):
					self.setSubtitleTrack(2)
					doSubs = True
				if (action == "sub4"):
					self.setSubtitleTrack(3)
					doSubs = True
				if doSubs:
					(n, SubtitleTrackList, selected_track) = SpecialJump.getSubtitleTrackList(SpecialJumpInstance)
					SpecialJump.specialJumpStartTimerShowSubsBox(SpecialJumpInstance, SubtitleTrackList, selected_track)
				if doAudio:
					(n, AudioTrackList, selected_track) = SpecialJump.getAudioTrackList(SpecialJumpInstance)
					SpecialJump.specialJumpStartTimerShowAudioBox(SpecialJumpInstance, AudioTrackList, selected_track)
				if doJump:
					self.SJJumpTime += time_seconds
					if doMute:
						self.activateTimeshiftIfNecessaryAndDoSeekRelative(time_seconds * 90000, config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
					else:
						self.activateTimeshiftIfNecessaryAndDoSeekRelative(time_seconds * 90000, 0)

	def setNewVolumeWithBox(self,newVolume):
		lastVolume = self.getAudioVolume()
		#if config.plugins.SpecialJump.debugEnable.getValue(): print "setNewVolumeWithBox 1"
		#if config.plugins.SpecialJump.debugEnable.getValue(): print lastVolume
		#if config.plugins.SpecialJump.debugEnable.getValue(): print newVolume
		if newVolume != 'no_change':
			if int(newVolume) != int(lastVolume):
				#if config.plugins.SpecialJump.debugEnable.getValue(): print "setNewVolumeWithBox 2"
				self.setAudioVolume(newVolume)
				self.specialJumpStartTimerShowAudioVolumeBox(newVolume)

	def checkSetNewVolumeOnChange(self):
		#if config.plugins.SpecialJump.debugEnable.getValue(): print "checkSetNewVolumeOnChange 1"
		if InfoBar and self.InfoBar_instance:
			#if config.plugins.SpecialJump.debugEnable.getValue(): print "checkSetNewVolumeOnChange 2"
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			if ref is not None:
				try:
					mypath = ref.getPath()
				except:
					mypath = ''
				if mypath != '':
					if mypath.endswith('.ts'):
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "__serviceChanged/ playing .ts file"
						serviceType = "TVorTSvideo"
					else:
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "__serviceChanged/ playing other (non .ts) file"
						serviceType = "nonTSvideo"
				else:
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "__serviceChanged/ no path, presumably live TV"
					serviceType = "TVorTSvideo"
			else:
				#if config.plugins.SpecialJump.debugEnable.getValue(): print "__serviceChanged/ no service reference"
				serviceType = "none"
			
			if serviceType == "TVorTSvideo":
				self.setNewVolumeWithBox(config.plugins.SpecialJump.audioVolumeTVorTSvideo.getValue())
			if serviceType == "nonTSvideo":
				(n, selected_track) = self.getAudioTrack()
				if selected_track == 0:
					self.setNewVolumeWithBox(config.plugins.SpecialJump.audioVolumeNonTSVideoTrack1.getValue())
				if selected_track == 1:
					self.setNewVolumeWithBox(config.plugins.SpecialJump.audioVolumeNonTSVideoTrack2.getValue())
				if selected_track == 2:
					self.setNewVolumeWithBox(config.plugins.SpecialJump.audioVolumeNonTSVideoTrack3.getValue())
				if selected_track == 3:
					self.setNewVolumeWithBox(config.plugins.SpecialJump.audioVolumeNonTSVideoTrack4.getValue())

	def getAudioVolume(self):
		return self.volctrl.getVolume()

	def setAudioVolume(self, volume):
		self.volctrl.setVolume(int(volume),int(volume))

	def setAudioTrack(self, track):
		service = self.session.nav.getCurrentService()
		audioTracks = audio = service and service.audioTracks()
		n = audio and audio.getNumberOfTracks() or 0
		if n > track:
			audioTracks.selectTrack(track)
			self.checkSetNewVolumeOnChange()

	def getAudioTrack(self):
		service = self.session.nav.getCurrentService()
		audioTracks = audio = service and service.audioTracks()
		n = audio and audio.getNumberOfTracks() or 0
		selectedidx = -1
		if n > 0:
			selectedidx = audioTracks.getCurrentTrack()
		return (n, selectedidx)

	def getAudioTrackList(self):
		#entries: number,description,language,selected
		#returns number of tracks, full list, and selected index (-1=none selected)
		#stolen from AudioSelection.py:
		streams = []
		selectedidx = -1
		service = self.session.nav.getCurrentService()
		audioTracks = audio = service and service.audioTracks()
		n = audio and audio.getNumberOfTracks() or 0
		if n > 0:
			selectedAudio = audioTracks.getCurrentTrack()
			for x in range(n):
				number = str(x + 1)
				i = audio.getTrackInfo(x)
				languages = i.getLanguage().split('/')
				description = i.getDescription() or ''
				selected = ' '
				language = ''
				if selectedAudio == x:
					selected = 'X'
					selectedidx = x
				cnt = 0
				for lang in languages:
					if cnt:
						language += ' / '
					if LanguageCodes.has_key(lang):
						language += LanguageCodes[lang][0]
					else:
						language += lang
					cnt += 1
				if language == '':
					language = 'undef.'

				streams.append((number, description, language, selected))
		return (n, streams, selectedidx)

	def setSubtitleTrack(self, track):
		(n, SubtitleTrackList, selected_track) = self.getSubtitleTrackList()
		if (n > track) and (track != selected_track):        
			if track == -1:
				self.InfoBar_instance.selected_subtitle=None
				#self.InfoBar_instance.enableSubtitle(None)
				InfoBarSubtitleSupport.enableSubtitle(self.InfoBar_instance,None)
			else:
				# either subtitle.getSubtitleList()   and  subtitlelist[track][:4]
				# or     self.getSubtitleTrackList()  and SubtitleTrackList[track][4][:4]
				self.InfoBar_instance.selected_subtitle=SubtitleTrackList[track][4][:4] # x[:4] = x[0:4] = (x[0], x[1], x[2], x[3])
				#self.InfoBar_instance.enableSubtitle(SubtitleTrackList[track][4][:4])
				InfoBarSubtitleSupport.enableSubtitle(self.InfoBar_instance,SubtitleTrackList[track][4][:4])

	def getSubtitleTrack(self):
		service = self.session.nav.getCurrentService()
		subtitle = service and service.subtitle()
		subtitlelist = subtitle and subtitle.getSubtitleList()
		selectedidx = -1
		try:
			n = len(subtitlelist)
		except:
			n = 0
		if n > 0:
			idx = 0
			for x in subtitlelist:
				if self.InfoBar_instance.selected_subtitle and x[:4] == self.InfoBar_instance.selected_subtitle[:4]:
					selectedidx = idx
				idx += 1
		return (n, selectedidx)

	def getSubtitleTrackList(self):
		#entries: number,description,language,selected,x (x is the 4-entry list specifying the subtitle)
		#returns number of tracks, full list, and selected index (-1=none selected)
		#stolen from AudioSelection.py:
		streams = []
		idx = 0
		selectedidx = -1
		service = self.session.nav.getCurrentService()
		subtitle = service and service.subtitle()
		subtitlelist = subtitle and subtitle.getSubtitleList()
		for x in subtitlelist:
			number = str(x[1])
			description = '?'
			language = 'undef.'
			selected = ' '
			if self.InfoBar_instance.selected_subtitle and x[:4] == self.InfoBar_instance.selected_subtitle[:4]:
				selected = 'X'
				selectedidx = idx
			try:
				if x[4] != 'und':
					if LanguageCodes.has_key(x[4]):
						language = LanguageCodes[x[4]][0]
					else:
						language = x[4]
			except:
				language = 'undef.'
			if x[0] == 0:
				description = 'DVB'
				number = '%x' % x[1]
			elif x[0] == 1:
				description = 'teletext'
				number = '%x%02x' % (x[3] and x[3] or 8, x[2])
			elif x[0] == 2:
				types = ('unknown', 'embedded', 'SSA file', 'ASS file', 'SRT file', 'VOB file', 'PGS file')
				try:
					description = types[x[2]]
				except:
					description = _('unknown') + ': %s' % x[2]
					number = str(int(number) + 1)
			idx += 1
			#we return "idx+1", not "number", for always being consistent with "selectedidx"
			streams.append((idx, description, language, selected, x))
		try:
			n = len(subtitlelist)
		except:
			n = 0
		return (n, streams, selectedidx)
		
	def shutdown(self):
		self.SJTimer.callback.remove(self.specialJumpTimeout)
		self.SJTimer = None
		self.SJMuteTimer.callback.remove(self.specialJumpUnmute)
		self.SJMuteTimer = None
		self.SJZapMessageTimer.callback.remove(self.specialJumpZapMessageTimeout)
		self.SJZapMessageTimer = None
		self.SJAudioBoxTimer.callback.remove(self.specialJumpAudioBoxTimeout)
		self.SJAudioBoxTimer = None
		self.SJAudioVolumeBoxTimer.callback.remove(self.specialJumpAudioVolumeBoxTimeout)
		self.SJAudioVolumeBoxTimer = None
		self.SJSubsBoxTimer.callback.remove(self.specialJumpSubsBoxTimeout)
		self.SJSubsBoxTimer = None
		self.SJZapspeedBoxTimer.callback.remove(self.specialJumpZapspeedBoxTimeout)
		self.SJZapspeedBoxTimer = None
		self.SJZapspeedPollTimer.callback.remove(self.specialJumpZapspeedPollTimeout)
		self.SJZapspeedPollTimer = None
		self.SJZapUpTimer.callback.remove(self.specialJumpZapUpTimeout)
		self.SJZapUpTimer = None
		self.SJZapDownTimer.callback.remove(self.specialJumpZapDownTimeout)
		self.SJZapDownTimer = None
		self.SJZapTimer.callback.remove(self.specialJumpZapTimeout)
		self.SJZapTimer = None
		self.SJZapBenchmarkTimer.callback.remove(self.zapDown)
		self.SJZapBenchmarkTimer = None
		self.executeCyclicTimer.callback.remove(self.executeCyclic)
		self.executeCyclicTimer = None
		self.gotRecordEventTimer.callback.remove(self.gotRecordEventDelayed)
		self.gotRecordEventTimer = None
		self.session.nav.record_event.remove(self.gotRecordEvent)

	def getSeek(self):
		service = self.session.nav.getCurrentService()
		if service is None:
			self.session.open(MessageBox,_("SpecialJump: no service%d"), type = MessageBox.TYPE_ERROR,timeout = 2)
			return
		seek = service.seek()
		#if seek is None or not seek.isCurrentlySeekable():
		if seek is None:
			#self.session.open(MessageBox,_("SpecialJump: no seek%d"), type = MessageBox.TYPE_ERROR,timeout = 2)
			return
		return seek

	def getTime_ms(self):
		return int(round(time.time() * 1000))
		
	def getLength(self):
		seek = self.getSeek()
		if seek is not None:
			length = seek.getLength()
			if length and int(length[1]) > 0:
				return int(length[1])
			else:
				return -1
		else:
			return -1

	def getTimeshiftFileSize_kB(self):
		service = self.session.nav.getCurrentService()
		if service is not None:
			ts = service and service.timeshift()
			if ts is not None:
				timeshift_filename = ts.getTimeshiftFilename()
				if timeshift_filename != '':
					timeshift_file_kB = os.path.getsize(timeshift_filename)/1024
				else:
					timeshift_file_kB = -1
			else:
				timeshift_file_kB = -1
		else:
			timeshift_file_kB = -1
		return timeshift_file_kB

	def isCurrentlySeekable(self):
		if InfoBar and self.InfoBar_instance:
			seek = self.getSeek()
			if seek is not None:
				if seek.isCurrentlySeekable():
					return True
				else:
					return False
			else:
				return False
		else:
			return False

	def isSeekstatePaused(self):
		if self.InfoBar_instance.seekstate == self.InfoBar_instance.SEEK_STATE_PAUSE:
			return True
		else:
			return False
			
	def toggleSubtitleTrack(self,parent):
		self.InfoBar_instance = parent
		if InfoBar and self.InfoBar_instance:
			(n, selected_track) = self.getSubtitleTrack()
			if n > 0:
				if self.SJSubsBoxTimerActive:
					subToggleMode = config.plugins.SpecialJump.subToggleMode_multi.getValue()
				else:
					subToggleMode = config.plugins.SpecialJump.subToggleMode_single.getValue()
				if subToggleMode == '12noff':
					if selected_track == -1:
						selected_track = 0;
					elif selected_track == n-1:
						selected_track = -1
					else:
						selected_track = (selected_track + 1)
				else: # 'onoff'
					if selected_track == -1:
						selected_track = self.SJLastSubsTrack
					else:
						self.SJLastSubsTrack = selected_track
						selected_track = -1
				self.setSubtitleTrack(selected_track)
				(n, SubtitleTrackList, selected_track) = self.getSubtitleTrackList()
				self.specialJumpStartTimerShowSubsBox(SubtitleTrackList, selected_track)

	def toggleAudioTrack(self,parent):
		self.InfoBar_instance = parent
		if InfoBar and self.InfoBar_instance:
			(n, selected_track) = self.getAudioTrack()
			if n > 0:
				selected_track = (selected_track+1) % n
				self.setAudioTrack(selected_track)
				(n, AudioTrackList, selected_track) = self.getAudioTrackList()
				self.specialJumpStartTimerShowAudioBox(AudioTrackList, selected_track)
				if config.plugins.SpecialJump.debugEnable.getValue(): print selected_track

	def toggleLCDBlanking(self,parent):
		self.InfoBar_instance = parent
		# config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 10))
		# config.lcd.bright  = ConfigSlider(default=5, limits=(0, 10))
		if self.SJLCDon:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SJLCDon"
			self.setLCDBrightness(0)
			self.SJLCDon = False
		else:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "not SJLCDon"
			self.restoreLCDBrightness()

	def setLCDBrightness(self, value):
		#self.LCD_instance.setBright(value)
		value *= 255
		value /= 10
		if value > 255:
			value = 255
		eDBoxLCD.getInstance().setLCDBrightness(value)

	def restoreLCDBrightness(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "restoreLCDBrightness"
		if Screens.Standby.inStandby:
			self.setLCDBrightness(config.lcd.standby.getValue())
		else:
			self.setLCDBrightness(config.lcd.bright.getValue())
		self.SJLCDon = True

	def jumpPreviousMark(self,parent,mode):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "jumpPreviousMark"
		self.InfoBar_instance = parent
		self.SJMode=mode
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			show_infobar_on_skip_lastValue = config.usage.show_infobar_on_skip.getValue()
			config.usage.show_infobar_on_skip.setValue(True) # force showing infobar
		InfoBarCueSheetSupport.jumpPreviousMark(self.InfoBar_instance)
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			config.usage.show_infobar_on_skip.setValue(show_infobar_on_skip_lastValue)
		self.SJJumpTime = "jump >*"
		#self.specialJumpStartTimerShowInfoBar(False, config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.specialJumpMute(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.SJJumpTime = 0

	def jumpNextMark(self,parent,mode):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "jumpNextMark"
		self.InfoBar_instance = parent
		self.SJMode=mode
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			show_infobar_on_skip_lastValue = config.usage.show_infobar_on_skip.getValue()
			config.usage.show_infobar_on_skip.setValue(True) # force showing infobar
		InfoBarCueSheetSupport.jumpNextMark(self.InfoBar_instance)
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			config.usage.show_infobar_on_skip.setValue(show_infobar_on_skip_lastValue)
		self.SJJumpTime = "jump *<"
		#self.specialJumpStartTimerShowInfoBar(False, config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.specialJumpMute(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.SJJumpTime = 0

	def toggleMark(self,parent,mode,markType):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "toggleMark"
		self.InfoBar_instance = parent
		self.SJMode=mode
		if markType == InfoBarCueSheetSupport.CUT_TYPE_MARK:
			InfoBarCueSheetSupport.toggleMark(self.InfoBar_instance)
			self.SJJumpTime = "toggle mark"
		else:
			self.myIBGtoggleMark(False, False, 10*90000, False, markType)
			if markType == InfoBarCueSheetSupport.CUT_TYPE_IN:
				self.SJJumpTime = "toggle in"
			else:
				self.SJJumpTime = "toggle out"
			self.specialJumpStartTimerShowInfoBar(True, 0)
			service = self.session.nav.getCurrentService()
			if service is not None:
				cue = service and service.cueSheet()
				if cue is not None:
					# disable cutlists. we want to freely browse around in the movie
					print "cut lists disabled!"
					cue.setCutListEnable(0)

		self.SJJumpTime = 0

	def callMovieCut(self,parent,mode):
		try:
			MovieCut(session=self.session, service=self.session.nav.getCurrentlyPlayingServiceReference())
		except:
			print "callMovieCut failed"

	def callCutListEditor(self,parent,mode):
		try:
			CutListEditor(session=self.session, service=self.session.nav.getCurrentlyPlayingServiceReference())
		except:
			print "callCutListEditor failed"

	#from InfoBarGenerics.py
	#added argument markType, allows setting IN and OUT points
	def myIBGtoggleMark(self, onlyremove=False, onlyadd=False, tolerance=10*90000, onlyreturn=False, markType=InfoBarCueSheetSupport.CUT_TYPE_MARK):
		current_pos = InfoBarCueSheetSupport.cueGetCurrentPosition(self.InfoBar_instance)
		if current_pos is None:
#			print "not seekable"
			return

		if markType == InfoBarCueSheetSupport.CUT_TYPE_MARK:
			nearest_cutpoint = InfoBarCueSheetSupport.getNearestCutPoint(self.InfoBar_instance,current_pos)
		else:
			nearest_cutpoint = self.myIBGgetNearestCutPointInOut(pts=current_pos,markType=markType)
		if config.plugins.SpecialJump.debugEnable.getValue(): print "nearest_cutpoint ",nearest_cutpoint

		if nearest_cutpoint is not None and abs(nearest_cutpoint[0] - current_pos) < tolerance:
			if onlyreturn:
				return nearest_cutpoint
			if not onlyadd:
				InfoBarCueSheetSupport.removeMark(self.InfoBar_instance,nearest_cutpoint)
				if config.plugins.SpecialJump.debugEnable.getValue(): print "removeMark ",nearest_cutpoint
		elif not onlyremove and not onlyreturn:
			InfoBarCueSheetSupport.addMark(self.InfoBar_instance,(current_pos, markType))
			if config.plugins.SpecialJump.debugEnable.getValue(): print "addMark ",markType

		if onlyreturn:
			return None

	#from InfoBarGenerics.py getNearestCutPoint
	#added argument markType, allows searching ONLY among IN or OUT points
	def myIBGgetNearestCutPointInOut(self, pts, cmp=abs, start=False, markType=InfoBarCueSheetSupport.CUT_TYPE_IN):
		service = self.session.nav.getCurrentService()
		if service is not None:
			cue = service and service.cueSheet()
			if cue is not None:
				self.cut_list = cue.getCutList()
			else:
				self.cut_list = [ ]
		else:
			self.cut_list = [ ]
		# can be optimized
		nearest = None
		bestdiff = -1
		if start:
			bestdiff = cmp(0 - pts)
			if bestdiff >= 0:
				nearest = [0, False]
		for cp in self.cut_list:
			print "Fisch",cp,markType,cp[0],pts
			if cp[1] == markType:
				diff = cmp(cp[0] - pts)
				if diff >= 0 and (nearest is None or bestdiff > diff):
					nearest = cp
					bestdiff = diff
				
		return nearest

	#from Plugins/Extensions/Infopanel/plugin.py
	def command(self,commandline, strip=1):
		commandline = commandline + " >/tmp/command.txt"
		print 'LBA1 ',commandline
		os.system(commandline)
		print 'LBA2 ',commandline
		text = ""
		if os.path.exists("/tmp/command.txt") is True:
			file = open("/tmp/command.txt", "r")
			if strip == 1:
				for line in file:
					text = text + line.strip() + '\n'
			else:
				for line in file:
					text = text + line
					if text[-1:] != '\n': text = text + "\n"
			file.close()
		# if one or last line then remove linefeed
		if text[-1:] == '\n': text = text[:-1]
		os.system("rm /tmp/command.txt")
		return text

	def skipTeletext(self,parent):
		# avoid "break" action "startTeletext" when "long" action of the same key is executed quickly without changing the context
		self.skipTeletextActivation = True

	def startTeletext(self,parent):
		if self.skipTeletextActivation is False:
			self.InfoBar_instance = parent
			self.InfoBar_instance.teletext_plugin(session=self.session, service=self.session.nav.getCurrentService())
		self.skipTeletextActivation = False

	def getNumberOfFrontendsFreeForSJ(self):
		numBlockedFrontends = self.getNumberOfFrontendsRecording()
		if numBlockedFrontends is None:
			return self.getNumberOfFrontendsInstalled()
		else:
			return self.getNumberOfFrontendsInstalled() - numBlockedFrontends
		
	def getNumberOfFrontendsInstalled(self):
		return len(nimmanager.nim_slots)
		
	def getNumberOfRecordings(self):
		try:
			recs = self.session.nav.getRecordingsServicesAndTypes()
			numRecordings = 0
			for x in recs:
				if not (x[1] & pNavigation.isFromSpecialJumpFastZap):
					numRecordings += 1
			return numRecordings
		except:
			print "This image does not support 'getRecordingsServicesAndTypes()'"
			return None

	def getNumberOfFrontendsRecording(self):
		try:
			recs = self.session.nav.getRecordingsServicesAndTypesAndSlotIDs()
			numBlockedFrontends = 0
			seen = []
			for x in recs:
				if (x[2] >= 0) and not (x[2] in seen) and not (x[1] & pNavigation.isFromSpecialJumpFastZap):
					numBlockedFrontends += 1
					seen.append(x[2])
			return numBlockedFrontends
		except:
			print "This image does not support 'getRecordingsServicesAndTypesAndSlotIDs()'"
			return self.getNumberOfRecordings()
		
	def isIPTV(self):
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		if ref is not None:
			try:
				mypath = ref.getPath()
			except:
				mypath = ''
		if mypath.startswith('http://'):
			return True
		else:
			return False
	
	def debugmessagebox(self,parent):
		self.InfoBar_instance = parent
		service = self.session.nav.getCurrentService()
		messageString = ""
		import string
		num2alpha = dict(zip(range(0, 26), string.ascii_uppercase))
		if service is None:
			self.session.open(MessageBox,"no service", type = MessageBox.TYPE_ERROR,timeout = 2)
		else:
			seek = service.seek()
			if False:
				if seek is None:
					messageString += "no seek\n\n"
				elif not seek.isCurrentlySeekable():
					length  = seek.getLength()
					playpos = seek.getPlayPosition()
					messageString += "seek not currently seekable.\nLength=%d\nPlayPostition=%d\n\n" % (length[1]/90000, playpos[1]/90000)
				else:
					length  = seek.getLength()
					playpos = seek.getPlayPosition()
					messageString += "seek is currently seekable.\nLength=%d\nPlayPostition=%d\n\n" % (length[1]/90000, playpos[1]/90000)
			
			if False:
				timeshift_file_kB = self.getTimeshiftFileSize_kB()
				messageString += "timeshift file length =%d kbytes / estimated %ds\n\n" % (timeshift_file_kB,timeshift_file_kB/1000)
			
			# audio volume
			if False:
				messageString += "getAudioVolume =%d\n\n" % self.getAudioVolume()
			
			# infobar instance
			if False:
				if isinstance(self.InfoBar_instance, InfoBarShowMovies):
					messageString += _("Infobar is MoviePlayer\n")
				#else:
				#    messageString += _("Infobar is not MoviePlayer\n")
				if isinstance(self.InfoBar_instance, InfoBarEPG):
					messageString += _("Infobar is InfoBar\n")
				#else:
				#    messageString += _("Infobar is not InfoBar\n")  
				messageString += "\n"
				
			# channel number and live TV tuners
			if True:
				if self.isIPTV():
					messageString += "live TV is IPTV.\n\n"
				else:
					channelNo = int(self.InfoBar_instance.servicelist.servicelist.getCurrentIndex())+1
					feinfo    = service and service.frontendInfo()
					data      = feinfo and feinfo.getFrontendData()
					slot_number = data and data.get("tuner_number")
					ref       = self.session.nav.getCurrentlyPlayingServiceReference()
					name      = ref and ServiceReference(ref).getServiceName()
					namespace = ref and ref.getUnsignedData(4) # NAMESPACE
					tsid      = ref and ref.getUnsignedData(2) # TSID
					if (slot_number is not None) and (name is not None):
						messageString += "live %s (ch. %d) tuner %s (%04x,%04x)\n\n" % (name,channelNo,num2alpha[slot_number],namespace,tsid)
					else:
						messageString += "live TV not tuned.\n\n"

			# (pseudo) recordings
			if True:
				try:
					types =    {int(pNavigation.isRealRecording)          : "Recording", \
								int(pNavigation.isStreaming)              : "Streaming", \
								int(pNavigation.isPseudoRecording)        : "PseudoRec", \
								int(pNavigation.isUnknownRecording)       : "Unknown", \
								int(pNavigation.isFromTimer)              : "FromTimer", 
								int(pNavigation.isFromInstantRecording)   : "InstantRec", \
								int(pNavigation.isFromEPGrefresh)         : "EPGrefresh", \
								int(pNavigation.isFromSpecialJumpFastZap) : "SJFastZap"}

					recs = self.session.nav.getRecordingsServicesAndTypesAndSlotIDs()
					records_running = len(recs)
					messageString += "Active recordings: %d\n" % records_running
					for x in recs:
						typeString = ""
						for i in range(0, len(types)):
							if (2**i & x[1]) > 0:
								if typeString != "":
									typeString += " "
								if 2**i in types:
									typeString += "%s" % (types[2**i])
								else:
									typeString += "%d" % (2**i)
						name      = ServiceReference(x[0]).getServiceName()
						namespace = ServiceReference(x[0]).ref.getUnsignedData(4) # NAMESPACE
						tsid      = ServiceReference(x[0]).ref.getUnsignedData(2) # TSID
						if name is None:
							name = _("unknown service")
						if x[2] >= 0:
							tuner = num2alpha[x[2]]
						else:
							tuner = "None"
						messageString += "rec. %s (%s) tuner %s (%04x,%04x)\n" % (name,typeString,tuner,namespace,tsid)
						#print "Active recording: %s of type%s on tuner %s\n" % (x[0],typeString,tuner)				
					messageString += "\n"
					
					messageString += "Tuners in use for non SJ recordings: %d\n" % self.getNumberOfFrontendsRecording()
					messageString += "Active non SJ recordings: %d\n" % self.getNumberOfRecordings()
					messageString += "Tuners installed: %d\n" % self.getNumberOfFrontendsInstalled()
					messageString += "Tuners available for SJ: %d\n" % self.getNumberOfFrontendsFreeForSJ()
					messageString += "\n"
				except:
					messageString += "This image does not support 'getRecordingsServicesAndTypesAndSlotIDs()'\n"

			if False:
				recs = NavigationInstance.instance.record_event
				records_running = len(recs)
				messageString += "Active record_events: %d\n" % records_running
				for x in recs:
					messageString += "Active record_event: %s\n" % (x)
				messageString += "\n"
				
			# PIP
			if False:
				if (InfoBarPiP.pipShown(self.InfoBar_instance) == True):
					messageString += _("pipShown is True\n")
				else:
					messageString += _("pipShown is False\n")
				if (self.fastZapPipActive == True):
					messageString += _("fastZapPipActive is True\n")
				else:
					messageString += _("fastZapPipActive is False\n")
				messageString += "\n"
				
			# infobar seekstate
			if False:
				messageString += "global InfoBar.instance.seekstate = (%s, %s, %s, %s)\n"   % (InfoBar.instance.seekstate[0],InfoBar.instance.seekstate[1],InfoBar.instance.seekstate[2],InfoBar.instance.seekstate[3])
				messageString += "parent InfoBar_instance.seekstate = (%s, %s, %s, %s)\n\n" % (self.InfoBar_instance.seekstate[0],self.InfoBar_instance.seekstate[1],self.InfoBar_instance.seekstate[2],self.InfoBar_instance.seekstate[3])

			# start time
			if False:
				messageString += "self.starttime = %s\n\n" % self.starttime
			
			# HDD status
			if True:
				try:
					from  Components.Harddisk  import  harddiskmanager
					for hdd in harddiskmanager.HDDList():
						messageString += "HDD %s isSleeping: %s\n" % (hdd[1].getDeviceName(),hdd[1].isSleeping())
				except:
					messageString += _("HDD status detection failed\n")               
			messageString += "\n"               

			# video geometries 1
			if True:
				info = service.info()
				video_height = int(info.getInfo(iServiceInformation.sVideoHeight))
				video_width = int(info.getInfo(iServiceInformation.sVideoWidth))
				video_pol = ('i', 'p')[info.getInfo(iServiceInformation.sProgressive)]
				video_rate = int(info.getInfo(iServiceInformation.sFrameRate))
				messageString += "Video content: %ix%i%s %iHz\n" % (video_width, video_height, video_pol, (video_rate + 500) / 1000)

			# video clipping
			if False:
				if path.exists('/proc/stb/vmpeg/0/clip_left'):
					f = open('/proc/stb/vmpeg/0/clip_left', 'r')
					clip_left = int(f.read(), 16)
					f.close()
				else:
					clip_left = -999
				if path.exists('/proc/stb/vmpeg/0/clip_width'):
					f = open('/proc/stb/vmpeg/0/clip_width', 'r')
					clip_width = int(f.read(), 16)
					f.close()
				else:
					clip_width = -999
				if path.exists('/proc/stb/vmpeg/0/clip_top'):
					f = open('/proc/stb/vmpeg/0/clip_top', 'r')
					clip_top = int(f.read(), 16)
					f.close()
				else:
					clip_top = -999
				if path.exists('/proc/stb/vmpeg/0/clip_height'):
					f = open('/proc/stb/vmpeg/0/clip_height', 'r')
					clip_height = int(f.read(), 16)
					f.close()
				else:
					clip_height = -999
				messageString += "/proc/stb/vmpeg/0 clip: left=%i/w=%i / top=%i/h=%i/\n" % (clip_left, clip_width, clip_top, clip_height)
  
			# video geometries 2
			if True:
				if path.exists('/proc/stb/vmpeg/0/yres'):
					f = open('/proc/stb/vmpeg/0/yres', 'r')
					video_height = int(f.read(), 16)
					f.close()
				if path.exists('/proc/stb/vmpeg/0/xres'):
					f = open('/proc/stb/vmpeg/0/xres', 'r')
					video_width = int(f.read(), 16)
					f.close()
				if path.exists('/proc/stb/vmpeg/0/progressive'):
					f = open('/proc/stb/vmpeg/0/progressive', 'r')
					video_pol = 'p' if int(f.read(), 16) else 'i'
					f.close()
				if path.exists('/proc/stb/vmpeg/0/framerate'):
					f = open('/proc/stb/vmpeg/0/framerate', 'r')
					try:
						video_rate = int(f.read())
					except:
						video_rate = -999
					f.close()
				messageString += "/proc/stb/vmpeg/0: %ix%i%s / %i\n" % (video_width, video_height, video_pol, video_rate)
			
			# video mode
			if True:
				f = open('/proc/stb/video/videomode')
				current_mode = f.read()[:-1].replace('\n', '')
				f.close()
				messageString += "/proc/stb/video/videomode=%s\n\n" % current_mode

			# subtitle tracks
			if False:
				(n,SubtitleTrackList,selectedidx) = self.getSubtitleTrackList()
				for x in SubtitleTrackList:
					messageString += "ST (%d, %d, %d, %d) / %s / %s / %s / %s\n" % (x[4][0], x[4][1], x[4][2], x[4][3], x[0],x[1],x[2],x[3])
				if self.InfoBar_instance.selected_subtitle:
					messageString += "self.InfoBar_instance.selected_subtitle=(%d, %d, %d, %d)\n\n" % (self.InfoBar_instance.selected_subtitle[0], self.InfoBar_instance.selected_subtitle[1], self.InfoBar_instance.selected_subtitle[2], self.InfoBar_instance.selected_subtitle[3])
				else:
					messageString += "self.InfoBar_instance.selected_subtitle=None\n\n"

			# audio tracks
			if False:
				(n,AudioTrackList,selectedidx) = self.getAudioTrackList()        
				for x in AudioTrackList:
					messageString += "AudioTrack %s / %s / %s / %s\n" % (x[0],x[1],x[2],x[3])
					
			self.session.open(MessageBox, messageString, type = MessageBox.TYPE_INFO,timeout = 120)
			
			# write getBufferCharge (or other things) to a file periodically
			if False:
				self.executeCyclicTimer.start(500,False)#repetitive

	def executeCyclic(self):
		from Components.Harddisk import harddiskmanager
		f = open("/tmp/executeCyclic.log", "a")
		f.write("%s" % datetime.now())
		for hdd in harddiskmanager.HDDList():
			f.write(" %s sleeping %s" % (hdd[1].getDeviceName(),hdd[1].isSleeping()))
		f.write("\n")
		f.close()

	def executeCyclic2(self):
		if self.session:
			if self.session.nav:
				if self.session.nav.getCurrentService():
					if self.session.nav.getCurrentService().streamed():
						f = open("/tmp/executeCyclic.log", "w")
						bufferInfo = self.session.nav.getCurrentService().streamed().getBufferCharge()
						f.write("%s %s\n" % (datetime.now(),bufferInfo[0]))
						f.close()
					else:
						f = open("/tmp/executeCyclic.log", "w")
						f.write("%s %s\n" % (datetime.now(),"no nav"))
						f.close()
				else:
					f = open("/tmp/executeCyclic.log", "w")
					f.write("%s %s\n" % (datetime.now(),"no CurrentService"))
					f.close()
			else:
				f = open("/tmp/executeCyclic.log", "w")
				f.write("%s %s\n" % (datetime.now(),"not streamed"))
				f.close()
		else:
			f = open("/tmp/executeCyclic.log", "w")
			f.write("%s %s\n" % (datetime.now(),"no session"))
			f.close()

	def executeCyclic3(self):
		f = open('/proc/stb/vmpeg/0/yres', 'r')
		video_height = int(f.read(), 16)
		f.close()
		f = open("/tmp/executeCyclic.log", "a")
		f.write("%s %d\n" % (datetime.now(),video_height))
		f.close()

	
