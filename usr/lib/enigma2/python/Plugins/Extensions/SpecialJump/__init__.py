from __future__ import print_function

# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext


def localeInit():
	gettext.bindtextdomain("SpecialJump", resolveFilename(SCOPE_PLUGINS, "Extensions/SpecialJump/locale"))


def _(txt):
	t = gettext.dgettext("SpecialJump", txt)
	if t == txt:
		print("[SpecialJump] fallback to default translation for {}".format(txt))
		t = gettext.gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)
