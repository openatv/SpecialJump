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
#from Components.Sources.EMCCurrentService import EMCCurrentService
from Components.Lcd import LCD
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.PluginComponent import plugins
from Components.config import config, ConfigInteger, ConfigSubsection, ConfigYesNo, ConfigLocations, getConfigListEntry, ConfigText, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.VolumeControl import VolumeControl
from Components.ServiceEventTracker import ServiceEventTracker
from Components.SystemInfo import SystemInfo
from ServiceReference import ServiceReference, isPlayableForCur
import NavigationInstance
from enigma import eTimer, ePoint, eSize
from enigma import eDVBVolumecontrol
from enigma import iServiceInformation
from enigma import iPlayableService
from enigma import eDBoxLCD
from enigma import pNavigation
from datetime import datetime
from random import randint
from Tools.Directories import *
from Tools.BoundFunction import boundFunction
from Tools.ISO639 import LanguageCodes
from Tools import Notifications
from os import path

import xml.sax.xmlreader
import os.path
import os
import time
import keymapparser
#from __init__ import _

fixedJumpValues  = [("-3600", _("-1:00:00")), ("-3000", _("-50:00")), ("-2400", _("-40:00")), ("-1800", _("-30:00")), ("-1500", _("-25:00")), ("-1200", _("-20:00")), ("-900", _("-15:00")), ("-840", _("-14:00")), ("-780", _("-13:00")), ("-720", _("-12:00")), ("-660", _("-11:00")), ("-600", _("-10:00")), ("-540", _("-9:00")), ("-480", _("-8:00")), ("-420", _("-7:00")), ("-360", _("-6:00")), ("-300", _("-5:00")), ("-270", _("-4:30")), ("-240", _("-4:00")), ("-210", _("-3:30")), ("-180", _("-3:00")), ("-165", _("-2:45")), ("-150", _("-2:30")), ("-135", _("-2:15")), ("-120", _("-2:00")), ("-110", _("-1:50")), ("-100", _("-1:40")), ("-90", _("-1:30")), ("-80", _("-1:20")), ("-70", _("-1:10")), ("-60", _("-1:00")), ("-55", _("-0:55")), ("-50", _("-0:50")), ("-45", _("-0:45")), ("-40", _("-0:40")), ("-35", _("-0:35")), ("-30", _("-0:30")), ("-25", _("-0:25")), ("-20", _("-0:20")), ("-15", _("-0:15")), ("-12", _("-0:12")), ("-10", _("-0:10")), ("-9", _("-0:09")), ("-8", _("-0:08")), ("-7", _("-0:07")), ("-6", _("-0:06")), ("-5", _("-0:05")), ("-4", _("-0:04")), ("-3", _("-0:03")), ("-2", _("-0:02")), ("-1", _("-0:01")), ("0", _("0:00")), ("1", _("+0:01")), ("2", _("+0:02")), ("3", _("+0:03")), ("4", _("+0:04")), ("5", _("+0:05")), ("6", _("+0:06")), ("7", _("+0:07")), ("8", _("+0:08")), ("9", _("+0:09")), ("10", _("+0:10")), ("12", _("+0:12")), ("15", _("+0:15")), ("20", _("+0:20")), ("25", _("+0:25")), ("30", _("+0:30")), ("35", _("+0:35")), ("40", _("+0:40")), ("45", _("+0:45")), ("50", _("+0:50")), ("55", _("+0:55")), ("60", _("+1:00")), ("70", _("+1:10")), ("80", _("+1:20")), ("90", _("+1:30")), ("100", _("+1:40")), ("110", _("+1:50")), ("120", _("+2:00")), ("135", _("+2:15")), ("150", _("+2:30")), ("165", _("+2:45")), ("180", _("+3:00")), ("210", _("+3:30")), ("240", _("+4:00")), ("270", _("+4:30")), ("300", _("+5:00")), ("360", _("+6:00")), ("420", _("+7:00")), ("480", _("+8:00")), ("540", _("+9:00")), ("600", _("+10:00")), ("660", _("+11:00")), ("720", _("+12:00")), ("780", _("+13:00")), ("840", _("+14:00")), ("900", _("+15:00")), ("1200", _("+20:00")), ("1500", _("+25:00")), ("1800", _("+30:00")), ("2400", _("+40:00")), ("3000", _("+50:00")), ("3600", _("+1:00:00"))]
fixedJumpActions = [("nothing", _("do nothing")), ("audio1", _("change to audio track 1")), ("audio2", _("change to audio track 2")), ("audio3", _("change to audio track 3")), ("audio4", _("change to audio track 4")), ("sub1", _("activate subtitle track 1")), ("sub2", _("activate subtitle track 2")), ("sub3", _("activate subtitle track 3")), ("sub4", _("activate subtitle track 4"))]
audioVolumes     = [("no_change", _("no change")), ("0", _("0")), ("1", _("1")), ("2", _("2")), ("5", _("5")), ("10", _("10")), ("20", _("20")), ("30", _("30")), ("40", _("40")), ("50", _("50")), ("60", _("60")), ("70", _("70")), ("80", _("80")), ("90", _("90")), ("100", _("100"))]
timeoutValues    = [("500", _("0.5s")), ("1000", _("1s")), ("1500", _("1.5s")), ("2000", _("2s")), ("2500", _("2.5s")), ("3000", _("3s")), ("4000", _("4s")), ("5000", _("5s"))]
protectValues    = [("-1", _("no protection, always zap")), ("5000", _("5s")), ("10000", _("10s")), ("20000", _("20s")), ("30000", _("30s")), ("60000", _("1min")), ("120000", _("2min")), ("300000", _("5min")), ("600000", _("10min")), ("900000", _("15min")), ("1800000", _("30min")), ("3600000", _("60min"))]
zapSpeedLimits   = [("0", _("no limit")),      ("60", _("0.06s")), ("70", _("0.07s")), ("80", _("0.08s")), ("90", _("0.09s")), ("100", _("0.1s")), ("120", _("0.12s")), ("150", _("0.15s")), ("200", _("0.2s")), ("300", _("0.3s")), ("400", _("0.4s")), ("500", _("0.5s")), ("600", _("0.6s")), ("700", _("0.7s")), ("800", _("0.8s")), ("900", _("0.9s")), ("1000", _("1.0s")), ("1100", _("1.1s")), ("1200", _("1.2s")), ("1500", _("1.5s")), ("2000", _("2.0s"))]

config.plugins.SpecialJump = ConfigSubsection()
config.plugins.SpecialJump.enable = ConfigYesNo(default=True)
config.plugins.SpecialJump.zapspeed_enable = ConfigYesNo(default=True)
config.plugins.SpecialJump.mainmenu = ConfigYesNo(default=False)
config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark = ConfigSelection([("yes", _("yes")),("default", _("default"))], default="default")
config.plugins.SpecialJump.show_infobar = ConfigYesNo(default=True)
config.plugins.SpecialJump.debugEnable = ConfigYesNo(default=False)
#config.plugins.SpecialJump.keyPriority = ConfigSelection([("0", _("0")),("-1", _("-1")),("-2", _("-2"))], default="0")

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
config.plugins.SpecialJump.smallSpecialJumpStart  = ConfigSelection([("1", _("1")),("2", _("2")),("3", _("3")),("4", _("4")),("5", _("5")),("6", _("6")),("7", _("7"))], default="3")

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

config.plugins.SpecialJump.timeConstant1                  = ConfigInteger(default = 50,  limits  = (1, 999))
config.plugins.SpecialJump.timeConstant2                  = ConfigInteger(default = 100, limits  = (1, 999))
config.plugins.SpecialJump.algoVersion                    = ConfigSelection([("1", _("1")),("2", _("2")),("3", _("3")),("4", _("4")),("5", _("5")),("6", _("6")),("7", _("7"))], default="1")

config.plugins.SpecialJump.EMCdirsHideOnPowerup           = ConfigYesNo(default=False)
config.plugins.SpecialJump.EMCdirsShowWindowTitle         = ConfigText(default = "EMC parental control")
config.plugins.SpecialJump.EMCdirsShowText                = ConfigText(default = "Enter PIN to show EMC hidden dirs")
config.plugins.SpecialJump.EMCdirsShowPin                 = ConfigInteger(default  = 0000, limits  = (0, 9999))

config.plugins.SpecialJump.fastZapEnable                  = ConfigYesNo(default=True)
config.plugins.SpecialJump.fastZapBenchmarkMode           = ConfigYesNo(default=False)
config.plugins.SpecialJump.fastZapMethod                  = ConfigSelection(choices = [("pip", _("Picture in Picture (debug only)")),("pip_hidden", _("Picture in Picture, hidden (not recommended)")),("record", _("fake recording"))],default = "record")
config.plugins.SpecialJump.zapspeedMeasureTimeout_ms      = ConfigInteger(default = 5500, limits  = (1, 99999))
config.plugins.SpecialJump.fastZapBenchmarkTime_ms        = ConfigInteger(default = 6000, limits  = (1, 99999))

config.plugins.SpecialJump.separator = ConfigSelection([("na", _(" "))], default="na")

SpecialJumpInstance = None
baseInfoBarPlugins__init__ = None
base_InfoBarNumberZap_selectAndStartService = None
base_ChannelSelection_setHistoryPath = None

#----------------------------------------------------------------------

def autostart(reason, **kwargs):
	global baseInfoBarPlugins__init__
	global base_InfoBarNumberZap_selectAndStartService
	global base_ChannelSelection_setHistoryPath
	global SpecialJumpInstance
	if config.plugins.SpecialJump.enable.value:
		print "SpecialJump enabled: ",config.plugins.SpecialJump.enable.getValue()
		print datetime.now()
		session = kwargs['session']
		if SpecialJumpInstance is None:
			SpecialJumpInstance = SpecialJump(session)
		if baseInfoBarPlugins__init__ is None:
			baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
		if base_InfoBarNumberZap_selectAndStartService is None:
			base_InfoBarNumberZap_selectAndStartService = InfoBarNumberZap.selectAndStartService
		if base_ChannelSelection_setHistoryPath is None:
			base_ChannelSelection_setHistoryPath = ChannelSelection.setHistoryPath
		InfoBarNumberZap.selectAndStartService = SJselectAndStartService
		ChannelSelection.setHistoryPath     = SJsetHistoryPath
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
		InfoBarPlugins.specialjump_jumpPreviousMark     = specialjump_jumpPreviousMark
		InfoBarPlugins.specialjump_jumpNextMark         = specialjump_jumpNextMark
		InfoBarPlugins.specialjump_toggleMark           = specialjump_toggleMark
		InfoBarPlugins.specialjump_toggleLCDBlanking    = specialjump_toggleLCDBlanking
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
		return [(_("SpecialJump"), setup, "SpecialJump_menu", 55)]
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
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG isinstance(self, InfoBarShowMovies)"
		if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
		x = {'specialjump_forwards':        (boundFunction(self.specialjump_forwards,"MP","normal"),  _('SpecialJump forwards')),
		 'specialjump_backwards':           (boundFunction(self.specialjump_backwards,"MP","normal"), _('SpecialJump backwards')),
		 'specialjump_forwards_small':      (boundFunction(self.specialjump_forwards,"MP","small"),  _('SpecialJump forwards small')),
		 'specialjump_backwards_small':     (boundFunction(self.specialjump_backwards,"MP","small"), _('SpecialJump backwards small')),
		 'specialjump_jump1':               (boundFunction(self.specialjump_jump,"MP", "J1"), _('programmable jump 1')),
		 'specialjump_jump2':               (boundFunction(self.specialjump_jump,"MP", "J2"), _('programmable jump 2')),
		 'specialjump_jump3':               (boundFunction(self.specialjump_jump,"MP", "J3"), _('programmable jump 3')),
		 'specialjump_jump4':               (boundFunction(self.specialjump_jump,"MP", "J4"), _('programmable jump 4')),
		 'specialjump_jump5':               (boundFunction(self.specialjump_jump,"MP", "J5"), _('programmable jump 5')),
		 'specialjump_jump6':               (boundFunction(self.specialjump_jump,"MP", "J6"), _('programmable jump 6')),
		 'specialjump_jump7':               (boundFunction(self.specialjump_jump,"MP", "J7"), _('programmable jump 7')),
		 'specialjump_jump8':               (boundFunction(self.specialjump_jump,"MP", "J8"), _('programmable jump 8')),
		 'specialjump_jumpkey1':            (boundFunction(self.specialjump_jump,"MP", "K1"), _('programmable jump key 1')),
		 'specialjump_jumpkey4':            (boundFunction(self.specialjump_jump,"MP", "K4"), _('programmable jump key 4')),
		 'specialjump_jumpkey7':            (boundFunction(self.specialjump_jump,"MP", "K7"), _('programmable jump key 7')),
		 'specialjump_jumpkey3':            (boundFunction(self.specialjump_jump,"MP", "K3"), _('programmable jump key 3')),
		 'specialjump_jumpkey6':            (boundFunction(self.specialjump_jump,"MP", "K6"), _('programmable jump key 6')),
		 'specialjump_jumpkey9':            (boundFunction(self.specialjump_jump,"MP", "K9"), _('programmable jump key 9')),
		 'specialjump_channelDown':         (boundFunction(self.specialjump_channelDown,"MP"),    _('KEY_CHANNELDOWN combined pause/zap function')),
		 'specialjump_channelUp':           (boundFunction(self.specialjump_channelUp,  "MP"),    _('KEY_CHANNELUP   combined  play/zap function')),
		 'specialjump_jumpPreviousMark':    (boundFunction(self.specialjump_jumpPreviousMark,"MP"), _('jump to previous mark')),
		 'specialjump_jumpNextMark':        (boundFunction(self.specialjump_jumpNextMark,"MP"),     _('jump to next mark')),
		 'specialjump_toggleMark':          (boundFunction(self.specialjump_toggleMark,"MP"),       _('toggle mark')),
		 'specialjump_doNothing':           (self.specialjump_doNothing, _('do nothing')),
		 'specialjump_toggleSubtitleTrack': (self.specialjump_toggleSubtitleTrack, _('toggle subtitle track')),
		 'specialjump_toggleAudioTrack':    (self.specialjump_toggleAudioTrack,    _('toggle audio track')),
		 'specialjump_toggleLCDBlanking':   (self.specialjump_toggleLCDBlanking,   _('toggle LCD blanking')),
		 'specialjump_emcpin':              (self.specialjump_emcpin,              _('enter parental control PIN for EMC hidden dirs')),
		 'specialjump_debugmessagebox':     (self.specialjump_debugmessagebox,     _('show debug message box')),
		 'specialjump_startTeletext':       (self.specialjump_startTeletext,       _('start teletext')),
		 'specialjump_toggleSubtitleTrack_skipTeletext':        (self.specialjump_toggleSubtitleTrack_skipTeletext,        _('skip teletext activation'))}
		self['SpecialJumpMoviePlayerActions'] = HelpableActionMap(self, 'SpecialJumpMoviePlayerActions', x, prio=-2) # -2 for priority over InfoBarSeek SeekActions seekdef:1 etc.
	elif isinstance(self, InfoBarEPG):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG isinstance(self, InfoBarEPG)"
		if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
		x = {'specialjump_forwards':        (boundFunction(self.specialjump_forwards,"TV","normal"),  _('SpecialJump forwards')),
		 'specialjump_backwards':           (boundFunction(self.specialjump_backwards,"TV","normal"), _('SpecialJump backwards')),
		 'specialjump_forwards_small':      (boundFunction(self.specialjump_forwards,"TV","small"),  _('SpecialJump forwards small')),
		 'specialjump_backwards_small':     (boundFunction(self.specialjump_backwards,"TV","small"), _('SpecialJump backwards small')),
		 'specialjump_jump1':               (boundFunction(self.specialjump_jump,"TV", "J1"), _('programmable jump 1')),
		 'specialjump_jump2':               (boundFunction(self.specialjump_jump,"TV", "J2"), _('programmable jump 2')),
		 'specialjump_jump3':               (boundFunction(self.specialjump_jump,"TV", "J3"), _('programmable jump 3')),
		 'specialjump_jump4':               (boundFunction(self.specialjump_jump,"TV", "J4"), _('programmable jump 4')),
		 'specialjump_jump5':               (boundFunction(self.specialjump_jump,"TV", "J5"), _('programmable jump 5')),
		 'specialjump_jump6':               (boundFunction(self.specialjump_jump,"TV", "J6"), _('programmable jump 6')),
		 'specialjump_jump7':               (boundFunction(self.specialjump_jump,"TV", "J7"), _('programmable jump 7')),
		 'specialjump_jump8':               (boundFunction(self.specialjump_jump,"TV", "J8"), _('programmable jump 8')),
		 'specialjump_jumpkey1':            (boundFunction(self.specialjump_jump,"TV", "K1"), _('programmable jump key 1')),
		 'specialjump_jumpkey4':            (boundFunction(self.specialjump_jump,"TV", "K4"), _('programmable jump key 4')),
		 'specialjump_jumpkey7':            (boundFunction(self.specialjump_jump,"TV", "K7"), _('programmable jump key 7')),
		 'specialjump_jumpkey3':            (boundFunction(self.specialjump_jump,"TV", "K3"), _('programmable jump key 3')),
		 'specialjump_jumpkey6':            (boundFunction(self.specialjump_jump,"TV", "K6"), _('programmable jump key 6')),
		 'specialjump_jumpkey9':            (boundFunction(self.specialjump_jump,"TV", "K9"), _('programmable jump key 9')),
		 'specialjump_jumpkey2':            (boundFunction(self.specialjump_jump,"TV", "K2"), _('number zap key 2')),
		 'specialjump_jumpkey5':            (boundFunction(self.specialjump_jump,"TV", "K5"), _('number zap key 5')),
		 'specialjump_jumpkey8':            (boundFunction(self.specialjump_jump,"TV", "K8"), _('number zap key 8')),
		 'specialjump_channelDown':         (boundFunction(self.specialjump_channelDown,"TV"),      _('KEY_CHANNELDOWN combined pause/zap function')),
		 'specialjump_channelUp':           (boundFunction(self.specialjump_channelUp,  "TV"),      _('KEY_CHANNELUP   combined  play/zap function')),
		 'specialjump_jumpPreviousMark':    (boundFunction(self.specialjump_jumpPreviousMark,"TV"), _('jump to previous mark')),
		 'specialjump_jumpNextMark':        (boundFunction(self,specialjump_jumpNextMark,"TV"),     _('jump to next mark')),
		 'specialjump_toggleMark':          (boundFunction(self.specialjump_toggleMark,"TV"),       _('toggle mark')),
		 'specialjump_doNothing':           (self.specialjump_doNothing, _('do nothing')),
		 'specialjump_toggleSubtitleTrack': (self.specialjump_toggleSubtitleTrack, _('toggle subtitle track')),
		 'specialjump_toggleAudioTrack':    (self.specialjump_toggleAudioTrack,    _('toggle audio track')),
		 'specialjump_toggleLCDBlanking':   (self.specialjump_toggleLCDBlanking,   _('toggle LCD blanking')),
		 'specialjump_emcpin':              (self.specialjump_emcpin,              _('enter parental control PIN for EMC hidden dirs')),
		 'specialjump_debugmessagebox':     (self.specialjump_debugmessagebox,     _('show debug message box')),
		 'specialjump_startTeletext':       (self.specialjump_startTeletext,       _('start teletext')),
		 'specialjump_toggleSubtitleTrack_skipTeletext':        (self.specialjump_toggleSubtitleTrack_skipTeletext,        _('skip teletext activation'))}
		self['SpecialJumpActions'] = HelpableActionMap(self, 'SpecialJumpActions', x, prio=-2) # -2 for priority over InfoBarSeek SeekActions seekdef:1 etc.
	else:
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG NOT isinstance(self, ...)"
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
		InfoBarPlugins.specialjump_toggleAudioTrack = None
		InfoBarPlugins.specialjump_toggleLCDBlanking = None
		InfoBarPlugins.specialjump_channelDown = None
		InfoBarPlugins.specialjump_channelUp = None
		InfoBarPlugins.specialjump_jumpPreviousMark = None
		InfoBarPlugins.specialjump_jumpNextMark = None
		InfoBarPlugins.specialjump_toggleMark = None
	baseInfoBarPlugins__init__(self)

def SJsetHistoryPath(self, doZap=True):
	# history zap is using ChannelSelection.setHistoryPath. Disable pseudo recordings before changing service (freeing the tuner), do predictive zap afterwards.
	SpecialJump.initZapSpeedCounter(SpecialJumpInstance)
	SpecialJump.disablePredictiveRecOrPIP(SpecialJumpInstance)
	base_ChannelSelection_setHistoryPath(self,doZap)
	SpecialJump.zapHandler(SpecialJumpInstance,"zapDown") # P+

def SJselectAndStartService(self, service, bouquet):
	# number zap is using InfoBarNumberZap.selectAndStartService. Disable pseudo recordings before changing service (freeing the tuner), do predictive zap afterwards.
	SpecialJump.initZapSpeedCounter(SpecialJumpInstance)
	SpecialJump.disablePredictiveRecOrPIP(SpecialJumpInstance)
	base_InfoBarNumberZap_selectAndStartService(self, service, bouquet)
	SpecialJump.zapHandlerParent(SpecialJumpInstance,self,"zapDown") # P+

def specialjump_jumpPreviousMark(self,mode):
	SpecialJump.jumpPreviousMark(SpecialJumpInstance,self,mode)

def specialjump_jumpNextMark(self,mode):
	SpecialJump.jumpNextMark(SpecialJumpInstance,self,mode)

def specialjump_toggleMark(self,mode):
	SpecialJump.toggleMark(SpecialJumpInstance,self,mode)

def specialjump_doNothing(self):
	pass
	
def specialjump_channelDown(self,mode):
	SpecialJump.channelDown(SpecialJumpInstance,self,mode)

def specialjump_channelUp(self,mode):
	SpecialJump.channelUp(SpecialJumpInstance,self,mode)

def specialjump_forwards(self,mode,size):
	if   size == 'normal': SpecialJump.specialJumpForwards(SpecialJumpInstance,self,mode,0)
	elif size == 'small':  SpecialJump.specialJumpForwards(SpecialJumpInstance,self,mode,int(config.plugins.SpecialJump.smallSpecialJumpStart.getValue()))

def specialjump_backwards(self,mode,size):
	if   size == 'normal': SpecialJump.specialJumpBackwards(SpecialJumpInstance,self,mode,0)
	elif size == 'small':  SpecialJump.specialJumpBackwards(SpecialJumpInstance,self,mode,int(config.plugins.SpecialJump.smallSpecialJumpStart.getValue()))

def specialjump_jump(self,mode,jumpkey):
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
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG __serviceChanged"
		if not self.parent.SJMuteTimerActive:
			self.SJChangedTimer.start(100,1) #1 = once / false = repetitively

	def serviceChanged_delayed(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG serviceChanged_delayed 1"
		self.SJChangedTimer.stop()
		if self.parent is not None:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG serviceChanged_delayed 2"
			self.parent.checkSetNewVolumeOnChange()

			if not self.parent.SJLCDon and config.plugins.SpecialJump.LCDonOnEventChange.getValue():
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG serviceChanged_delayed turned on LCD"
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
		
		#self['Service'] = EMCCurrentService(session.nav, self.parent) # overwritten in doShow

	def __onShow(self):
		self.instance.move(ePoint(config.plugins.SpecialJump.bar_x.getValue(), config.plugins.SpecialJump.bar_y.getValue()))
		self.refreshInfoBar()

	def __onClose(self):
		self.SJRefreshTimer.stop()

	def doShow(self, parent, grandparent_InfoBar):
		#self['Service'] = EMCCurrentService(self.session.nav, grandparent_InfoBar)
		self.parent = parent
		self.show()

	def doHide(self):
		if self.shown:
			self.hide()

	def refreshInfoBar(self):
		try:
			if self.parent.SJJumpTime < 0:
				self["SJJumpTime"].setText(_("jump -%d:%02d" % (abs(int(self.parent.SJJumpTime)) // 60, abs(int(self.parent.SJJumpTime)) % 60)))
			else:
				self["SJJumpTime"].setText(_("jump +%d:%02d" % (self.parent.SJJumpTime // 60, self.parent.SJJumpTime % 60)))
		except:
			self["SJJumpTime"].setText(_("%s" % self.parent.SJJumpTime)) # not an int
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
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG updateInfo"
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
		<eLabel text="SpecialJump Configuration" position="270,15" size="800,43" font="Regular;35" halign="right" foregroundColor="black" backgroundColor="white" transparent="1" />
		<widget name="config" position="30,90" size="1040,440" itemHeight="30" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/images/sel1040x30.png" backgroundColor="black" transparent="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/buttons/red.png" position=" 30,570" size="35,27" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/buttons/green.png" position="290,570" size="35,27" alphatest="blend" />
		<widget source="key_red" render="Label" position=" 80,573" size="200,26" font="Regular;22" halign="left" foregroundColor="black" backgroundColor="grey" transparent="1" />
		<widget source="key_green" render="Label" position="340,573" size="200,26" font="Regular;22" halign="left" foregroundColor="black" backgroundColor="grey" transparent="1" />
	</screen>
	"""
	
	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)

		self.createConfigList()
		self.onShown.append(self.setWindowTitle)
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.skinName = ["SpecialJump_" + self.__class__.__name__] # 'SpecialJump_SpecialJumpConfiguration'

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

	def createConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry((_("__ General settings __")),                            config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Enable SpecialJump plugin [restart GUI]")),           config.plugins.SpecialJump.enable))
		self.list.append(getConfigListEntry((_("SpecialJump entry in main menu [restart GUI]")),      config.plugins.SpecialJump.mainmenu))
		self.list.append(getConfigListEntry((_("Enable SpecialJump debug output in normal logfile")), config.plugins.SpecialJump.debugEnable))
		#self.list.append(getConfigListEntry((_("Use image color buttons (set to 'no' when using color keys in SpecialJump)")),        config.plisettings.ColouredButtons))
		#self.list.append(getConfigListEntry((_("Key priority (0 for image color buttons, -2 for SJ number keys")),                    config.plugins.SpecialJump.keyPriority))
		self.list.append(getConfigListEntry((_("[OSD settings] Show infobar on skip (set to 'no' when using SpecialJump infobar)")),   config.usage.show_infobar_on_skip))
		self.list.append(getConfigListEntry((_("[Timeshift settings] Show timeshift infobar")),                                        config.timeshift.showinfobar))
		self.list.append(getConfigListEntry((_("Show SpecialJump infobar (set to 'yes')")),           config.plugins.SpecialJump.show_infobar))
		self.list.append(getConfigListEntry((_("Show SpecialJump infobar on jumpNextMark/jumpPreviousMark (set to 'yes')")),           config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Special jump __")),                                config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Special jump 0 (initial value)")),                    config.plugins.SpecialJump.specialJump0))
		self.list.append(getConfigListEntry((_("Special jump 1 after 1st direction change")),         config.plugins.SpecialJump.specialJump1))
		self.list.append(getConfigListEntry((_("Special jump 2 (subsequent jump)")),                  config.plugins.SpecialJump.specialJump2))
		self.list.append(getConfigListEntry((_("Special jump 3 (subsequent jump)")),                  config.plugins.SpecialJump.specialJump3))
		self.list.append(getConfigListEntry((_("Special jump 4 (subsequent jump)")),                  config.plugins.SpecialJump.specialJump4))
		self.list.append(getConfigListEntry((_("Special jump 5 (subsequent jump)")),                  config.plugins.SpecialJump.specialJump5))
		self.list.append(getConfigListEntry((_("Special jump 6 (subsequent jump)")),                  config.plugins.SpecialJump.specialJump6))
		self.list.append(getConfigListEntry((_("Special jump 7 (subsequent jump)")),                  config.plugins.SpecialJump.specialJump7))
		self.list.append(getConfigListEntry((_("Special jump timeout")),                              config.plugins.SpecialJump.specialJumpTimeout_ms))
		self.list.append(getConfigListEntry((_("Mute after SpecialJump")),                            config.plugins.SpecialJump.specialJumpMuteTime_ms))
		self.list.append(getConfigListEntry((_("Small SpecialJump: start at initial value no.")),     config.plugins.SpecialJump.smallSpecialJumpStart))
		self.list.append(getConfigListEntry((_("SpecialJump infobar x position")),                    config.plugins.SpecialJump.bar_x))
		self.list.append(getConfigListEntry((_("SpecialJump infobar y position")),                    config.plugins.SpecialJump.bar_y))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Programmable jumps __")),                          config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Programmable jump 1")),                               config.plugins.SpecialJump.jump1))
		self.list.append(getConfigListEntry((_("Programmable jump 1 action")),                        config.plugins.SpecialJump.jump1action))
		self.list.append(getConfigListEntry((_("Programmable jump 2")),                               config.plugins.SpecialJump.jump2))
		self.list.append(getConfigListEntry((_("Programmable jump 2 action")),                        config.plugins.SpecialJump.jump2action))
		self.list.append(getConfigListEntry((_("Programmable jump 3")),                               config.plugins.SpecialJump.jump3))
		self.list.append(getConfigListEntry((_("Programmable jump 3 action")),                        config.plugins.SpecialJump.jump3action))
		self.list.append(getConfigListEntry((_("Programmable jump 4")),                               config.plugins.SpecialJump.jump4))
		self.list.append(getConfigListEntry((_("Programmable jump 4 action")),                        config.plugins.SpecialJump.jump4action))
		self.list.append(getConfigListEntry((_("Programmable jump 5")),                               config.plugins.SpecialJump.jump5))
		self.list.append(getConfigListEntry((_("Programmable jump 5 action")),                        config.plugins.SpecialJump.jump5action))
		self.list.append(getConfigListEntry((_("Programmable jump 6")),                               config.plugins.SpecialJump.jump6))
		self.list.append(getConfigListEntry((_("Programmable jump 6 action")),                        config.plugins.SpecialJump.jump6action))
		self.list.append(getConfigListEntry((_("Programmable jump 7")),                               config.plugins.SpecialJump.jump7))
		self.list.append(getConfigListEntry((_("Programmable jump 7 action")),                        config.plugins.SpecialJump.jump7action))
		self.list.append(getConfigListEntry((_("Programmable jump 8")),                               config.plugins.SpecialJump.jump8))
		self.list.append(getConfigListEntry((_("Programmable jump 8 action")),                        config.plugins.SpecialJump.jump8action))
		self.list.append(getConfigListEntry((_("Mute after programmable jump")),                      config.plugins.SpecialJump.jumpMuteTime_ms))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Zap (dual function P+/P- and play/pause) __")),    config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Zap speed limit")),                                   config.plugins.SpecialJump.zapSpeedLimit_ms))
		self.list.append(getConfigListEntry((_("Zap from timeshift by pressing P+/P- twice within")), config.plugins.SpecialJump.zapFromTimeshiftTime_ms))
		self.list.append(getConfigListEntry((_("Zap from timeshift, warning message duration")),      config.plugins.SpecialJump.zapFromTimeshiftMessageTime_ms))
		self.list.append(getConfigListEntry((_("Zap from timeshift, warning message x position")),    config.plugins.SpecialJump.zap_x))
		self.list.append(getConfigListEntry((_("Zap from timeshift, warning message y position")),    config.plugins.SpecialJump.zap_y))
		self.list.append(getConfigListEntry((_("Protect large timeshift buffer in live TV (P+ required twice)")), config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms))
		self.list.append(getConfigListEntry((_("Protect large timeshift buffer in live TV (P- required twice)")), config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Subtitle and audio toggling __")),                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Subtitle toggle mode when pressing key only once within infobox timeout")),  config.plugins.SpecialJump.subToggleMode_single))
		self.list.append(getConfigListEntry((_("Subtitle toggle mode when pressing multiple times within infobox timeout")), config.plugins.SpecialJump.subToggleMode_multi))
		self.list.append(getConfigListEntry((_("Subtitle toggle infobox timeout")),                   config.plugins.SpecialJump.subToggleTimeout_ms))
		self.list.append(getConfigListEntry((_("Subtitle toggle infobox verbosity")),                 config.plugins.SpecialJump.subToggleVerbosity))
		self.list.append(getConfigListEntry((_("Subtitle infobox x position")),                       config.plugins.SpecialJump.subs_x))
		self.list.append(getConfigListEntry((_("Subtitle infobox y position")),                       config.plugins.SpecialJump.subs_y))
		self.list.append(getConfigListEntry((_("Subtitle infobox anchor")),                           config.plugins.SpecialJump.subs_anchor))
		self.list.append(getConfigListEntry((_("Audio toggle infobox timeout")),                      config.plugins.SpecialJump.audioToggleTimeout_ms))
		self.list.append(getConfigListEntry((_("Audio toggle infobox verbosity")),                    config.plugins.SpecialJump.audioToggleVerbosity))
		self.list.append(getConfigListEntry((_("Audio toggle infobox x position")),                   config.plugins.SpecialJump.audio_x))
		self.list.append(getConfigListEntry((_("Audio toggle infobox y position")),                   config.plugins.SpecialJump.audio_y))
		self.list.append(getConfigListEntry((_("Audio toggle infobox anchor")),                       config.plugins.SpecialJump.audio_anchor))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Fixed audio volumes (when remove controls TV volume) __")), config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Volume for TV and recorded TV (.ts files)")),         config.plugins.SpecialJump.audioVolumeTVorTSvideo))
		self.list.append(getConfigListEntry((_("Volume for non .ts videos, audio track 1")),          config.plugins.SpecialJump.audioVolumeNonTSVideoTrack1))
		self.list.append(getConfigListEntry((_("Volume for non .ts videos, audio track 2")),          config.plugins.SpecialJump.audioVolumeNonTSVideoTrack2))
		self.list.append(getConfigListEntry((_("Volume for non .ts videos, audio track 3")),          config.plugins.SpecialJump.audioVolumeNonTSVideoTrack3))
		self.list.append(getConfigListEntry((_("Volume for non .ts videos, audio track 4")),          config.plugins.SpecialJump.audioVolumeNonTSVideoTrack4))
		self.list.append(getConfigListEntry((_("Volume for (nearly) muting after a jump")),           config.plugins.SpecialJump.audioVolumeMuteDuringJump))
		self.list.append(getConfigListEntry((_("Volume infobox timeout")),                            config.plugins.SpecialJump.audioVolumeTimeout_ms))
		self.list.append(getConfigListEntry((_("Volume infobox x position")),                         config.plugins.SpecialJump.audioVolume_x))
		self.list.append(getConfigListEntry((_("Volume infobox y position")),                         config.plugins.SpecialJump.audioVolume_y))
		self.list.append(getConfigListEntry((_("Volume infobox verbosity")),                          config.plugins.SpecialJump.audioVolumeVerbosity))
		self.list.append(getConfigListEntry((_("[from AV menu] Audio auto volume level")),            config.av.autovolume))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Toggle LCD brightness by key __")),                config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Turn LCD on again on event change")),                 config.plugins.SpecialJump.LCDonOnEventChange))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Gigablue Quad/Plus driver workaround __")),        config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Use algorithm (2=Quad/Plus, 1=others)")),             config.plugins.SpecialJump.algoVersion))
		self.list.append(getConfigListEntry((_("Quad/Plus time constant 1 (author only)")),           config.plugins.SpecialJump.timeConstant1))
		self.list.append(getConfigListEntry((_("Quad/Plus time constant 2 (author only)")),           config.plugins.SpecialJump.timeConstant2))
		self.list.append(getConfigListEntry((_(" ")),                                                 config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("__ Fast zapping __")),                                config.plugins.SpecialJump.separator))
		self.list.append(getConfigListEntry((_("Enable predictive fast zap mode")),                   config.plugins.SpecialJump.fastZapEnable))
		self.list.append(getConfigListEntry((_("Fast zap mode method of activating next channel")),   config.plugins.SpecialJump.fastZapMethod))
		self.list.append(getConfigListEntry((_("Auto-zap benchmark mode (debug only, random hit/miss/off)")), config.plugins.SpecialJump.fastZapBenchmarkMode))
		self.list.append(getConfigListEntry((_("Enable zap speed measurement")),                      config.plugins.SpecialJump.zapspeed_enable))
		self.list.append(getConfigListEntry((_("Zap speed infobox verbosity")),                       config.plugins.SpecialJump.zapspeedVerbosity))
		self.list.append(getConfigListEntry((_("Zap speed infobox timeout")),                         config.plugins.SpecialJump.zapspeedTimeout_ms))
		self.list.append(getConfigListEntry((_("Zap speed infobox x position")),                      config.plugins.SpecialJump.zapspeed_x))
		self.list.append(getConfigListEntry((_("Zap speed infobox y position")),                      config.plugins.SpecialJump.zapspeed_y))
		self.list.append(getConfigListEntry((_("Zap speed infobox anchor")),                          config.plugins.SpecialJump.zapspeed_anchor))
		self.list.append(getConfigListEntry((_("Zap speed measurement timeout (zap error)")),         config.plugins.SpecialJump.zapspeedMeasureTimeout_ms))
		self.list.append(getConfigListEntry((_("Auto-zap benchmark mode time between zaps")),         config.plugins.SpecialJump.fastZapBenchmarkTime_ms))

	def changedEntry(self):
		self.createConfigList()
		self["config"].setList(self.list)

	def setWindowTitle(self):
		self.setTitle(_("SpecialJump Configuration"))

	def save(self):
		for x in self["config"].list:
			x[1].save()
		self.changedEntry()
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
		
		self.SJLCDon = True                    # for toggling LCD brightness
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG __init__ SJLCDon = True"
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
		self.SJWorkaround1Timer=eTimer()          # timer for a workaround (test)
		self.SJWorkaround1Timer.timeout.get().append(self.specialJumpWorkaround1Timeout)
		self.SJWorkaround2Timer=eTimer()          # timer for a workaround (test)
		self.SJWorkaround2Timer.timeout.get().append(self.specialJumpWorkaround2Timeout)
		self.SJZapBenchmarkTimer=eTimer()         # timer for fast zap benchmark mode
		self.SJZapBenchmarkTimer.timeout.get().append(self.zapDown)
	   
		self.WorkaroundPTS = 0
		
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
		
		self.volctrl = eDVBVolumecontrol.getInstance() # volume control # dirty
		
		# initialize local windows
		self.SpecialJumpInfoBar_instance      = self.session.instantiateDialog(SpecialJumpInfoBar)
		self.SpecialJumpEventTracker_instance = self.session.instantiateDialog(SpecialJumpEventTracker, self)
		self.ZapMessage_instance              = self.session.instantiateDialog(ZapMessage)
		self.AudioToggleInfobox_instance      = self.session.instantiateDialog(AudioSubsInfobox, 'Audio')
		self.AudioVolumeInfobox_instance      = self.session.instantiateDialog(AudioSubsInfobox, 'Volume')
		self.SubsToggleInfobox_instance       = self.session.instantiateDialog(AudioSubsInfobox, 'Subs')
		self.zapspeedInfobox_instance         = self.session.instantiateDialog(AudioSubsInfobox, 'Zapspeed')
		
		# for zap speed display
		self.services_hd_plus = ['1:0:19:2E9B:411:1:C00000:0:0:0:', '1:0:19:2EAF:411:1:C00000:0:0:0:', '1:0:19:5274:41D:1:C00000:0:0:0:', '1:0:19:EF10:421:1:C00000:0:0:0:', '1:0:19:EF11:421:1:C00000:0:0:0:', '1:0:19:EF14:421:1:C00000:0:0:0:', '1:0:19:EF15:421:1:C00000:0:0:0:', '1:0:19:EF74:3F9:1:C00000:0:0:0:', '1:0:19:EF75:3F9:1:C00000:0:0:0:', '1:0:19:EF76:3F9:1:C00000:0:0:0:', '1:0:19:EF77:3F9:1:C00000:0:0:0:', '1:0:19:EF78:3F9:1:C00000:0:0:0:']
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

	def powerOn(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump powerOn"
		self.SJLCDon = True
		self.fastZapPipActive = False
		if config.plugins.SpecialJump.EMCdirsHideOnPowerup.getValue():
			try:
				#/etc/engima2/emc-hide.cfg
				config.EMC.cfghide_enable.setValue(True)
			except:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump could not set config.EMC.cfghide_enable True"
		
	def powerOff(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump powerOff"
		pass

	def _onStandby(self, element):
		if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump _onStandby"
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.powerOn)
		self.powerOff()

	def specialJumpEMCpin(self,parent):
		from Screens.InputBox import PinInput
		self.session.openWithCallback(self.checkEMCpin, PinInput, pinList=[config.plugins.SpecialJump.EMCdirsShowPin.getValue()], triesEntry=config.ParentalControl.retries.servicepin, title=config.plugins.SpecialJump.EMCdirsShowText.getValue(), windowTitle=config.plugins.SpecialJump.EMCdirsShowWindowTitle.getValue())

	def checkEMCpin(self, ret):
		if ret is not None:
			if ret:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump EMC PIN correct"
				try:
					config.EMC.cfghide_enable.setValue(False)
				except:
					if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump could not set config.EMC.cfghide_enable False"
			else:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump EMC PIN incorrect"

		
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

	def specialJumpStartTimerShowInfoBar(self, muteTime_ms):
		self.SJTimer.stop()
		self.SJTimer.start(int(config.plugins.SpecialJump.specialJumpTimeout_ms.getValue()))
		if config.plugins.SpecialJump.show_infobar.getValue():
			self.SpecialJumpInfoBar_instance.doShow(self,self.InfoBar_instance) # grandparent_InfoBar
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
		#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG specialJumpZapspeedPollTimeout ",self.zap_time_event_counter,' ',datetime.now()
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
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG illegal zap time ",datetime.now()
			self.SJZapspeedPollTimer.stop()
			self.zap_error_counter[ind1][ind2] += 1
			self.zap_error_counter[ind1][self.zap_list_ind2.index('tot')] += 1
		else:
			if path.exists('/proc/stb/vmpeg/0/yres'):
				f = open('/proc/stb/vmpeg/0/yres', 'r')
				video_height = int(f.read(), 16)
				f.close()
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
			print 'date:',datetime.now()
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
		if config.plugins.SpecialJump.algoVersion.getValue() == '1':
			self.activateTimeshiftIfNecessaryAndDoSeekRelative_1(pts, MuteTime_ms)
		if config.plugins.SpecialJump.algoVersion.getValue() == '2':
			self.activateTimeshiftIfNecessaryAndDoSeekRelative_2(pts, MuteTime_ms)
			
	def activateTimeshiftIfNecessaryAndDoSeekRelative_1(self, pts, MuteTime_ms):
		if config.plugins.SpecialJump.debugEnable.getValue(): print '[SpecialJump] activateTimeshiftIfNecessaryAndDoSeekRelative_1', pts, ' ', MuteTime_ms
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
				self.specialJumpStartTimerShowInfoBar(MuteTime_ms)
			else:
				self.session.open(MessageBox,_("SpecialJump debug: no seek"), type = MessageBox.TYPE_ERROR,timeout = 2)
		else:
			self.session.open(MessageBox,_("SpecialJump debug: no (InfoBar and self.InfoBar_instance)"), type = MessageBox.TYPE_ERROR,timeout = 2)
			
	def activateTimeshiftIfNecessaryAndDoSeekRelative_2(self, pts, MuteTime_ms):
		if config.plugins.SpecialJump.debugEnable.getValue(): print '[SpecialJump] activateTimeshiftIfNecessaryAndDoSeekRelative_2', pts, ' ', MuteTime_ms
		print datetime.now()
		if InfoBar and self.InfoBar_instance:
			seek = self.getSeek()
			if seek is not None:
				if not seek.isCurrentlySeekable():
					# OK without workarounds on Gigablue Quad with driver up to 2014.11.22
					# Gigablue Quad driver 2014.12.16 requires workarounds:
					# - pauses between steps (by timers)
					# - 4 to 6 calls of "self.fixGigablueDriverProb" for jumping into TS buffer from live TV (95% OK with 6 calls, 85% OK with 4 calls)
					#
					# also the following sequence no longer works with Gigablue Quad driver 2014.12.16:
					# - play a .ts file
					# - jump to A
					# - rewind to B
					# - OK  -> playback continues at A, not at B
					# - infobar combinations:
					# -- SJ-bar + InfoBar   SJ-bar causes the problem during jump
					# -- SJ-bar             SJ-bar causes the problem during jump + "SJ-bar only" is affected during rewind
					# -- InfoBar            nothing
					# -- no bar             nothing
					
					# need to activate timeshift first
					self.fixGigablueDriverProb('activateTimeshiftIfNecessaryAndDoSeekRelative_2 not seekable 1 / mandatory')
					InfoBarTimeshift.activateTimeshiftEndAndPause(self.InfoBar_instance)
					self.fixGigablueDriverProb('activateTimeshiftIfNecessaryAndDoSeekRelative_2 not seekable 2 / mandatory')
					self.WorkaroundPTS = pts
					self.WorkaroundMuteTime_ms = MuteTime_ms
					self.SJWorkaround1Timer.start(config.plugins.SpecialJump.timeConstant1.getValue())
					self.fixGigablueDriverProb('activateTimeshiftIfNecessaryAndDoSeekRelative_2 not seekable 3 started timer')
				else:
					needPauseService = False
					if self.isSeekstatePaused():
						# workaround for the bug that, when paused, multiple jumps are not possible (only the last one has effect at a time)
						self.unPauseService()
						needPauseService = True
					InfoBarSeek.doSeekRelative(self.InfoBar_instance, pts)
					if needPauseService:
						# workaround part II
						self.pauseService()
					self.specialJumpStartTimerShowInfoBar(MuteTime_ms)
			else:
				self.session.open(MessageBox,_("SpecialJump debug: no seek"), type = MessageBox.TYPE_ERROR,timeout = 2)
		else:
			self.session.open(MessageBox,_("SpecialJump debug: no (InfoBar and self.InfoBar_instance)"), type = MessageBox.TYPE_ERROR,timeout = 2)

	def specialJumpWorkaround1Timeout(self):
		self.SJWorkaround1Timer.stop()
		self.fixGigablueDriverProb('activateTimeshiftIfNecessaryAndDoSeekRelative_2 timer 1 a / mandatory')
		InfoBarSeek.unPauseService(self.InfoBar_instance)
		self.fixGigablueDriverProb('activateTimeshiftIfNecessaryAndDoSeekRelative_2 timer 1 b / mandatory')
		self.SJWorkaround2Timer.start(config.plugins.SpecialJump.timeConstant2.getValue())

	def specialJumpWorkaround2Timeout(self):
		self.SJWorkaround2Timer.stop()
		self.fixGigablueDriverProb('activateTimeshiftIfNecessaryAndDoSeekRelative_2 timer 2 a')
		seek = self.getSeek()
		pts = self.WorkaroundPTS
		MuteTime_ms = self.WorkaroundMuteTime_ms
		InfoBarSeek.doSeekRelative(self.InfoBar_instance, pts)
		self.specialJumpStartTimerShowInfoBar(MuteTime_ms)
	
	def channelDown(self,parent,mode):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if mode == "MP":
			self.pauseService()
		if mode == "TV":
			if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
			if self.isCurrentlySeekable(): # timeshift active and play position "in the past"
				if self.SJZapDownTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG A-"
					self.zapUp() # zapUp = P-
				else:
					if self.isSeekstatePaused():
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG B-"
						self.specialJumpStartZapDownTimer()
						self.specialJumpShowZapWarning()
					else:
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG C-"
						self.pauseService()
			else: # live TV
				if self.SJZapDownTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG D-"
					self.zapUp() # zapUp = P-
				else:
					length = self.getTimeshiftFileSize_kB() # length of timeshift buffer (estimated: 1kB ~ 1ms)
					if (length > int(config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms.getValue())) and not (int(config.plugins.SpecialJump.zapM_ProtectTimeshiftBuffer_ms.getValue()) == -1): # protect timeshift buffer unless "no protection" is selected
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG E-"
						self.specialJumpStartZapDownTimer()
						self.specialJumpShowZapWarning()
						InfoBarTimeshift.activateTimeshiftEndAndPause(self.InfoBar_instance) # not just self.pauseService()
					else: # zap with speed limit
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG F-"
						if not self.SJZapTimerActive:
							#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG G-"
							self.zapUp() # zapUp = P-
							self.SJZapDownTimer.stop()

	def channelUp(self,parent,mode):
		self.InfoBar_instance = parent
		self.SJMode=mode
		if mode == "MP":
			self.unPauseService()
		if mode == "TV":
			if config.plugins.SpecialJump.debugEnable.getValue(): print datetime.now()
			if self.isCurrentlySeekable(): # timeshift active and play position "in the past"
				if self.SJZapUpTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG A+"
					#InfoBarTimeshift.stopTimeshift(self.InfoBar_instance) # not just zap, or zapping will be impossible for ~2s -- didn't help
					self.zapDown() # zapDown = P+
				else:
					if not self.isSeekstatePaused():
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG B+"
						self.specialJumpStartZapUpTimer()
						self.specialJumpShowZapWarning()
					else:
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG C+"
						self.unPauseService()
			else: # live TV
				if self.SJZapUpTimerActive:  # quickly pressed twice
					#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG D+"
					self.zapDown() # zapDown = P+
				else:
					length = self.getTimeshiftFileSize_kB() # length of timeshift buffer (estimated: 1kB ~ 1ms)
					if (length > int(config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms.getValue())) and not (int(config.plugins.SpecialJump.zapP_ProtectTimeshiftBuffer_ms.getValue()) == -1): # protect timeshift buffer unless "no protection" is selected
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG E+"
						self.specialJumpStartZapUpTimer()
						self.specialJumpShowZapWarning()
					else: # zap with speed limit
						#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG F+"
						if not self.SJZapTimerActive:
							#if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG G+"
							self.zapDown() # zapDown = P+
							self.SJZapUpTimer.stop()

	def zapUp(self):
		self.initZapSpeedCounter()
		self.specialJumpStartZapTimer()
		self.SJZapBenchmarkTimer.stop()
		self.InfoBar_instance.LongButtonPressed = False # do not treat as PIP zap even when pressed long
		try:
			self.InfoBar_instance.pts_blockZap_timer.stop()
		except:
			print "SpecialJump DEBUG self.InfoBar_instance.pts_blockZap_timer.stop() failed in zapUp"
		InfoBarChannelSelection.zapUp(self.InfoBar_instance)     
		self.zapHandler("zapUp")
				
	def zapDown(self):
		self.initZapSpeedCounter()
		self.specialJumpStartZapTimer()
		self.InfoBar_instance.LongButtonPressed = False # do not treat as PIP zap even when pressed long
		try:
			self.InfoBar_instance.pts_blockZap_timer.stop()
		except:
			print "SpecialJump DEBUG self.InfoBar_instance.pts_blockZap_timer.stop() failed in zapDown"
		InfoBarChannelSelection.zapDown(self.InfoBar_instance)
		self.zapHandler("zapDown")

	def initZapSpeedCounter(self):
		if config.plugins.SpecialJump.zapspeed_enable.value:
			self.SJZapspeedPollTimer.start(self.zap_time_event_counter_ms,False)#repetitive
			self.zap_time_res_0_seen = False
		self.zap_time_event_counter = 0

	def zapHandlerParent(self,parent,direction):
		self.InfoBar_instance = parent
		self.zapHandler(direction)

	def zapHandler(self,direction):
		if config.plugins.SpecialJump.fastZapEnable.value:
			cur = self.InfoBar_instance.servicelist.getCurrentSelection()
			if cur:
				cur = cur.toString()
				if cur == self.zapPredictiveService:
					# fast zap due to previously active PIP on the new channel
					if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG ",self.fastZapDirection," PIP predictive zap success"
					self.zap_success = 'fast'
				else:
					self.zap_success = 'miss'
					if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG ",self.fastZapDirection," PIP predictive zap guessed wrong, is ",cur," exp. ",self.zapPredictiveService
		else:
			self.zap_success = 'off'
		
		if config.plugins.SpecialJump.fastZapBenchmarkMode.value:
			rand = randint(0,2)
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG Benchmark Mode ",rand
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
				
		if config.plugins.SpecialJump.fastZapEnable.value and SystemInfo.get("NumVideoDecoders", 1) > 1:
			self.fastZapDirection = direction
			if (config.plugins.SpecialJump.fastZapMethod.value == "pip") or (config.plugins.SpecialJump.fastZapMethod.value == "pip_hidden"):
				if (self.fastZapPipActive == False):
					if (InfoBarPiP.pipShown(self.InfoBar_instance) == False):
						if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapHandler ",direction," zapPredictive incl. initial showPiP"
						self.postZap_preloadPredictive()
					else:
						if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapHandler ",direction," PIP unexpectedly active, don't touch PIP",InfoBarPiP.pipShown(self.InfoBar_instance)
				else:
					if (InfoBarPiP.pipShown(self.InfoBar_instance) == True):
						if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapHandler ",direction," zapPredictive (PIP already active)"
						self.postZap_preloadPredictive()
					else:
						if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapHandler ",direction," zapPredictive (PIP unexpectedly inactive)",InfoBarPiP.pipShown(self.InfoBar_instance)
						self.postZap_preloadPredictive()
			else:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapHandler ",direction," start zapPredictive (pseudo rec.)"
				self.postZap_preloadPredictive()
		elif config.plugins.SpecialJump.fastZapEnable.value:
			print "SpecialJump DEBUG: fast zap not possible with a single tuner"
		else:
			if (self.fastZapPipActive == True):
				#not using PIP any more, restore size and turn off PIP
				self.session.pip.instance.move(ePoint(config.av.pip.value[0],config.av.pip.value[1]))
				self.session.pip.instance.resize(eSize(*(config.av.pip.value[2],config.av.pip.value[3])))
				self.session.pip["video"].instance.resize(eSize(*(config.av.pip.value[2],config.av.pip.value[3])))
			self.disablePredictiveRecOrPIP()

	def postZap_preloadPredictive(self):
		#start PIP or pseudo recording on the expected next service
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapPredictive 1"
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
		self.enablePredictiveRecOrPIP(fastZapNextService)
		self.zapPredictiveService = fastZapNextService.toString()

		self.InfoBar_instance.servicelist.setCurrentSelection(storeService)
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapPredictive 2"
														
	def enablePredictiveRecOrPIP(self, fastZapNextService):
		if (config.plugins.SpecialJump.fastZapMethod.value == "pip") or (config.plugins.SpecialJump.fastZapMethod.value == "pip_hidden"):
			if (InfoBarPiP.pipShown(self.InfoBar_instance) == False):
				InfoBarPiP.showPiP(self.InfoBar_instance)
				self.fastZapPipActive = True
				fastZapNextService = self.session.pip.resolveAlternatePipService(fastZapNextService)
				if fastZapNextService:
					self.session.pip.playService(fastZapNextService)
					if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapPredictive ",self.fastZapDirection," switched PIP to service ",fastZapNextService.toString()
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
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG zapPredictive ",self.fastZapDirection," pseudo recording service ",fastZapNextService.toString()

	def disablePredictiveRecOrPIP(self):
		if (self.fastZapPipActive == True) and (InfoBarPiP.pipShown(self.InfoBar_instance) == True):
			#disable PIP
			InfoBarPiP.showPiP(self.InfoBar_instance)
			self.fastZapPipActive = False
		if self.fastZapRecService is not None:
			#disable fake recording
			self.session.nav.stopRecordService(self.fastZapRecService)
			self.fastZapRecService = None
			self.zapPredictiveService = None
			
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
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG setNewVolumeWithBox 1"
		if config.plugins.SpecialJump.debugEnable.getValue(): print lastVolume
		if config.plugins.SpecialJump.debugEnable.getValue(): print newVolume
		if newVolume != 'no_change':
			if int(newVolume) != int(lastVolume):
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG setNewVolumeWithBox 2"
				self.setAudioVolume(newVolume)
				self.specialJumpStartTimerShowAudioVolumeBox(newVolume)

	def checkSetNewVolumeOnChange(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG checkSetNewVolumeOnChange 1"
		if InfoBar and self.InfoBar_instance:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG checkSetNewVolumeOnChange 2"
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			if ref is not None:
				try:
					mypath = ref.getPath()
				except:
					mypath = ''
				if mypath != '':
					if mypath.endswith('.ts'):
						if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG __serviceChanged/ playing .ts file"
						serviceType = "TVorTSvideo"
					else:
						if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG __serviceChanged/ playing other (non .ts) file"
						serviceType = "nonTSvideo"
				else:
					if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG __serviceChanged/ no path, presumably live TV"
					serviceType = "TVorTSvideo"
			else:
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG __serviceChanged/ no service reference"
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
		self.SJWorkaround1Timer.callback.remove(self.specialJumpWorkaround1Timeout)
		self.SJWorkaround1Timer = None
		self.SJWorkaround2Timer.callback.remove(self.specialJumpWorkaround2Timeout)
		self.SJWorkaround2Timer = None
		self.SJZapBenchmarkTimer.callback.remove(self.zapDown)
		self.SJZapBenchmarkTimer = None

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
				if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG toggleAudioTrack"
				if config.plugins.SpecialJump.debugEnable.getValue(): print selected_track

	def toggleLCDBlanking(self,parent):
		self.InfoBar_instance = parent
		# config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 10))
		# config.lcd.bright  = ConfigSlider(default=5, limits=(0, 10))
		if self.SJLCDon:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG toggleLCDBlanking if SJLCDon"
			self.setLCDBrightness(0)
			self.SJLCDon = False
		else:
			if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG toggleLCDBlanking if not SJLCDon"
			self.restoreLCDBrightness()

	def setLCDBrightness(self, value):
		#self.LCD_instance.setBright(value)
		value *= 255
		value /= 10
		if value > 255:
			value = 255
		eDBoxLCD.getInstance().setLCDBrightness(value)

	def restoreLCDBrightness(self):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG restoreLCDBrightness"
		if Screens.Standby.inStandby:
			self.setLCDBrightness(config.lcd.standby.getValue())
		else:
			self.setLCDBrightness(config.lcd.bright.getValue())
		self.SJLCDon = True

	def jumpPreviousMark(self,parent,mode):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG jumpPreviousMark"
		self.InfoBar_instance = parent
		self.SJMode=mode
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			show_infobar_on_skip_lastValue = config.usage.show_infobar_on_skip.getValue()
			config.usage.show_infobar_on_skip.setValue(True) # force showing infobar
		InfoBarCueSheetSupport.jumpPreviousMark(self.InfoBar_instance)
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			config.usage.show_infobar_on_skip.setValue(show_infobar_on_skip_lastValue)
		self.SJJumpTime = "jump >*"
		#self.specialJumpStartTimerShowInfoBar(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.specialJumpMute(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.SJJumpTime = 0

	def jumpNextMark(self,parent,mode):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG jumpNextMark"
		self.InfoBar_instance = parent
		self.SJMode=mode
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			show_infobar_on_skip_lastValue = config.usage.show_infobar_on_skip.getValue()
			config.usage.show_infobar_on_skip.setValue(True) # force showing infobar
		InfoBarCueSheetSupport.jumpNextMark(self.InfoBar_instance)
		if config.plugins.SpecialJump.show_infobar_on_jumpPreviousNextMark.getValue() == 'yes':
			config.usage.show_infobar_on_skip.setValue(show_infobar_on_skip_lastValue)
		self.SJJumpTime = "jump *<"
		#self.specialJumpStartTimerShowInfoBar(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.specialJumpMute(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.SJJumpTime = 0

	def toggleMark(self,parent,mode):
		if config.plugins.SpecialJump.debugEnable.getValue(): print "SpecialJump DEBUG toggleMark"
		self.InfoBar_instance = parent
		self.SJMode=mode
		InfoBarCueSheetSupport.toggleMark(self.InfoBar_instance)
		self.SJJumpTime = "toggle mark"
		#self.specialJumpStartTimerShowInfoBar(config.plugins.SpecialJump.jumpMuteTime_ms.getValue())
		self.SJJumpTime = 0

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
		
	def debugmessagebox(self,parent):
		self.InfoBar_instance = parent
		service = self.session.nav.getCurrentService()
		if service is None:
			self.session.open(MessageBox,_("no service"), type = MessageBox.TYPE_ERROR,timeout = 2)
		else:
			seek = service.seek()
			if seek is None:
				self.session.open(MessageBox,_("no seek"), type = MessageBox.TYPE_ERROR,timeout = 2)
				messageString = _("no seek\n")
			elif not seek.isCurrentlySeekable():
				length  = seek.getLength()
				playpos = seek.getPlayPosition()
				messageString = _("seek not currently seekable.\nLength=%d\nPlayPostition=%d\n" % (length[1]/90000, playpos[1]/90000))
			else:
				length  = seek.getLength()
				playpos = seek.getPlayPosition()
				messageString = _("seek is currently seekable.\nLength=%d\nPlayPostition=%d\n" % (length[1]/90000, playpos[1]/90000))
			messageString += _("\n")
			
			timeshift_file_kB = self.getTimeshiftFileSize_kB()
			messageString += _("timeshift file length =%d kbytes / estimated %ds\n\n" % (timeshift_file_kB,timeshift_file_kB/1000))

			# audio volume
			if False:
				messageString += _("getAudioVolume =%d\n\n" % self.getAudioVolume())
			
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
				messageString += _("\n")

			# (pseudo) recordings
			if True:
				try:
					types =    {int(pNavigation.isRealRecording)          : "isRealRecording", \
								int(pNavigation.isStreaming)              : "isStreaming", \
								int(pNavigation.isPseudoRecording)        : "isPseudoRecording", \
								int(pNavigation.isUnknownRecording)       : "isUnknownRecording", \
								int(pNavigation.isFromTimer)              : "isFromTimer", 
								int(pNavigation.isFromInstantRecording)   : "isFromInstantRecording", \
								int(pNavigation.isFromEPGrefresh)         : "isFromEPGrefresh", \
								int(pNavigation.isFromSpecialJumpFastZap) : "isFromSpecialJumpFastZap"}

					recs = self.session.nav.getRecordingsServicesAndTypes()
					records_running = len(recs)
					messageString += _("Active recordings: %d\n" % records_running)
					for x in recs:
						typeString = _(" ")
						for i in range(0, len(types)):
							if (2**i & x[1]) > 0:
								if 2**i in types:
									typeString += _(" %s") % (types[2**i])
								else:
									typeString += _(" %d") % (2**i)
						messageString += _("Active recording: %s of type%s\n" % (x[0],typeString))
						print _("Active recording: %s of type%s\n" % (x[0],typeString))
					messageString += _("\n")
				except:
					messageString += _("This image does not support 'getRecordingsServicesAndTypes()'\n")

			if False:
				recs = NavigationInstance.instance.record_event
				records_running = len(recs)
				messageString += _("Active record_events: %d\n" % records_running)
				for x in recs:
					messageString += _("Active record_event: %s\n" % (x))
				messageString += _("\n")
				
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
				messageString += _("\n")
				
			# infobar seekstate
			if False:
				messageString += _("global InfoBar.instance.seekstate = (%s, %s, %s, %s)\n"   % (InfoBar.instance.seekstate[0],InfoBar.instance.seekstate[1],InfoBar.instance.seekstate[2],InfoBar.instance.seekstate[3]))
				messageString += _("parent InfoBar_instance.seekstate = (%s, %s, %s, %s)\n\n" % (self.InfoBar_instance.seekstate[0],self.InfoBar_instance.seekstate[1],self.InfoBar_instance.seekstate[2],self.InfoBar_instance.seekstate[3]))

			# start time
			if False:
				messageString += _("self.starttime = %s\n\n" % self.starttime)
			
			# HDD status
			if True:
				try:
					from  Components.Harddisk  import  harddiskmanager
					for hdd in harddiskmanager.HDDList():
						messageString += _("HDD %s isSleeping: %s\n" % (hdd[1].getDeviceName(),hdd[1].isSleeping()))
				except:
					messageString += _("HDD status detection failed\n")               
			messageString += _("\n")               

			# video geometries 1
			if True:
				info = service.info()
				video_height = int(info.getInfo(iServiceInformation.sVideoHeight))
				video_width = int(info.getInfo(iServiceInformation.sVideoWidth))
				video_pol = ('i', 'p')[info.getInfo(iServiceInformation.sProgressive)]
				video_rate = int(info.getInfo(iServiceInformation.sFrameRate))
				messageString += _("Video content: %ix%i%s %iHz\n") % (video_width, video_height, video_pol, (video_rate + 500) / 1000)

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
				messageString += _("/proc/stb/vmpeg/0 clip: left=%i/w=%i / top=%i/h=%i/\n" % (clip_left, clip_width, clip_top, clip_height))
  
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
				messageString += _("/proc/stb/vmpeg/0: %ix%i%s / %i\n" % (video_width, video_height, video_pol, video_rate))
			
			# video mode
			if True:
				f = open('/proc/stb/video/videomode')
				current_mode = f.read()[:-1].replace('\n', '')
				f.close()
				messageString += _("/proc/stb/video/videomode=%s\n\n" % current_mode)

			# subtitle tracks
			if False:
				(n,SubtitleTrackList,selectedidx) = self.getSubtitleTrackList()
				for x in SubtitleTrackList:
					messageString += _("ST (%d, %d, %d, %d) / %s / %s / %s / %s\n" % (x[4][0], x[4][1], x[4][2], x[4][3], x[0],x[1],x[2],x[3]))
				if self.InfoBar_instance.selected_subtitle:
					messageString += _("self.InfoBar_instance.selected_subtitle=(%d, %d, %d, %d)\n\n" % (self.InfoBar_instance.selected_subtitle[0], self.InfoBar_instance.selected_subtitle[1], self.InfoBar_instance.selected_subtitle[2], self.InfoBar_instance.selected_subtitle[3]))
				else:
					messageString += _("self.InfoBar_instance.selected_subtitle=None\n\n")

			# audio tracks
			if False:
				(n,AudioTrackList,selectedidx) = self.getAudioTrackList()        
				for x in AudioTrackList:
					messageString += _("AudioTrack %s / %s / %s / %s\n" % (x[0],x[1],x[2],x[3]))
					
			self.session.open(MessageBox, messageString, type = MessageBox.TYPE_ERROR,timeout = 10)
	
