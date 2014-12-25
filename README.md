SpecialJump
===========

Plugin zum schnellen manuellen Überspringen von Werbung (und mehr)
------------------------------------------------------------------
by Fischreiher

Algorithmus:
------------

Beim Topfield TF5000-PVR gab es ein geniales Plugin (QuickJump) zum schnellen Überspringen von Werbung, das nach dem Prinzip der "binären Suche" funktionierte.  
Der Anwender musste dabei anhand des dargestellten Bildinhalts entscheiden, ob bereits zu weit gesprungen wurde (Sendung nach der Werbepause) oder noch nicht weit genug.  
Gesprungen wurde mit zwei Tasten vor und zurück, wobei sich der Sprungabstand ab dem ersten Richtungswechsel halbierte, z.B. bei einer Werbepause von 7:41:

>">"  springt +2:00  zu +2:00 vor  
>">"  springt +2:00  zu +4:00 vor  
>">"  springt +2:00  zu +6:00 vor  
>">"  springt +2:00  zu +8:00 vor - oops, zu weit ...  
>"<"  springt -1:00  zu +7:00 zurück  
>">"  springt +0:30  zu +7:30 vor  
>">"  springt +0:15  zu +7:45 vor - zu weit ..  
>"<"  springt -0:08  zu +7:37 zurück  
>">"  springt +0:04  zu +7:41 vor - Treffer

Aufgrund von Patenten auf ähnliche Algorithmen (Loewe Opta GmbH DE200410036013, DE102008055504) würde ich nie auf die Idee kommen, so etwas zu schreiben oder zu veröffentlichen.  
Patentiert u.a. ist ein Algorithmus, der bei jedem Richtungswechel die Sprungdistanz um einen konstanten Faktor ändert.
Während der patentierte Algorithmus die Sprungdistanz nur bei jedem Richtungswechel ändert, geschieht dies bei SpecialJump bei jedem Sprung ab dem ersten Richtungswechsel. In dieser Hinsicht entspricht SpecialJump besser dem Prinzip der "binären Suche" und benötigt weniger Tastendrücke.  
Allerdings verwendet SpecialJump, abweichend vom Patent, programmierbare Einträge einer Liste als Sprungdistanzen. Diese stehen per default in keinem konstanten Verhältnis zueinander, und die Sprungdistanz wird teils verringert, teils vergrößert. Darunter leidet der Nutzen erheblich.  
Falls ein User in der Liste z.B. 2:00, 1:00, 0:30, 0:15, 0:08 und 0:04 eintragen würde, um das Plugin zur "binären Suche" zu missbrauchen, könnte dies eine Patentverletzung darstellen.

Features Sprungfunktionen:
--------------------------

- SpecialJump zum schnellen Überspringen von Werbung mit 2 Tasten
- 8 programmierbare feste Sprünge
- Audio Stummschaltung für programmierbare Zeit nach jedem Sprung (angenehme Ruhe beim Überspringen der Werbung)
- feste Sprünge erlauben gleichzeitige Umschaltung auf einen einstellbaren Audio-Track ("sag das nochmal auf Deutsch")
- feste Sprünge erlauben gleichzeitige Umschaltung auf einen einstellbaren Subtitle-Track ("sag das nochmal mit Untertiteln")
- Tastenfunktion zum schnellen Toggeln des Audio- oder Subtitle-Tracks mit einer Taste (ohne sich durch Menüs zu hangeln)
- Tastenfunktion zum Dunkelschalten des Displays (für puristische Cineasten)
- Optional verschiedene feste Lautstärkewerte für TV-Betrieb und die einzelnen Tracks von Videos (Angleichen der Lautstärke verschiedener Tracks, nur sinnvoll, wenn die Fernbedienung die Lautstärke des Fernsehers steuert)
- Tastenbelegung aller Funktionen nur über die keymap (/usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/keymap.xml bzw. /usr/share/enigma2/keymap.usr)

Verbesserungen im Bedienkomfort:
--------------------------------

- Direktes Zurückspringen in den Timeshift-Buffer aus dem Live-TV-Betrieb möglich (ohne SpecialJump nur über Pause oder Rewind möglich)
- Mehrfachsprünge im pausierten Zustand möglich (ohne SpecialJump wird bei mehreren Sprüngen nicht um die Summe der Sprünge gesprungen, sondern nur um die Distanz des jeweils letzten Sprunges)
- Nach dem Wegzappen aus dem Timeshift ist ein erneutes Zappen sofort möglich (ohne SpecialJump erst nach 3 Sekunden).

Doppelbelegung der P+ und P- Tasten (KEY\_CHANNELUP und KEY\_CHANNELDOWN):
------------------------------------------------------------------------

- Zappen im Live-TV-Betrieb
- Pause (P-) / Play (P+) bei der Wiedergabe von Videos
- Pause (P-) / Play (P+) während Timeshift
- Schutz des Timeshift-Buffers im Live-TV-Betrieb:
  - ab einer einstellbaren Buffer-Größe kein Zappen, sondern Pause/Play mit Warnung
  - Zappen ist dann durch Doppelbetätigung P+ / P- möglich
  - empfohlene Einstellung: 5s für P- (zum bequemen Pausieren des live-TV mit P- auch recht kurz nach dem Senderwechsel) / 30min für P+ (Zappen klappt fast immer, nur ein großer Timeshift-Buffer wird geschützt)

Status:
-------

- Prinzipiell funktioniert alles auf Gigablue Quad unter openATV. Andere Boxen habe ich nicht, andere Images werde ich erst einmal nicht testen, aber auf Zuruf getestete Patches einbauen, um Problem mit anderen Boxen und Images zu beheben.
- Die Infoboxen, die den Audio- und Untertitel-Track anzeigen, haben manchmal einen dünnen hellen Rahmen, manchmal nicht. Ursache unbekannt. Wen stört's?
- Wird im pausierten Zustand drei mal der Audio-Track getoggelt (bei einem Video mit 2 Audiotracks), gibt's einen Spinner.
- Das Konzept der Doppelbelegung von P+/P- ist nicht optimal. Der User weiß nicht, wann P- pausiert und wann P- zappt. P+ ist klar. Daher sind für den Schutz von "P-" nur kleine Werte sinnvoll. 
- Für den Schutz des Timeshift-Buffers kann die Größe des Buffers nur in kByte, nicht in Sekunden ermittelt werden, da die timeshift position am EOF (live TV) ist. Ich rechne mit geschätzter Datenrate um (1kB=1ms).
- Statt die SpecialJumpInfoBar in jeder Skin individuell zu skinnen, könnte es sinnvoller sein, die einzig neue Information (SJJumpTime) in die vorhandenen Infobars "einzublenden".


Build (das macht nur der Autor):
--------------------------------

> cd /tmp; chmod 755 /usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/ipkg-build ; /usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/ipkg-build

Installation:
-------------

> cd /tmp  
> opkg install /tmp/enigma2-plugin-extensions-specialjump\_0.7-20140502-r0\_mips32el.ipk  
> reboot

FAQ:
----

1. Warum SpecialJump? Ich habe doch die Zifferntasten zum Springen?  
      Das Springen mit nur zwei Tasten ist wesentlich komfortabler und kann deutlich schneller und genauer zum Ziel führen. Dies ist abhängig von den eingestellten Sprungwerten: Ideal wäre die (leider patentierte) "binäre Suche", für die das Plugin rein theoretisch missbraucht werden könnte.

2. Warum kann die Tastenbelegung nicht im Konfigurationsmenü des Plugins eingestellt werden?  
      Es gibt Plugins, die diesen Komfort für wenige Tasten bieten, z.B. Multiquickbutton. Ein Plugin, das viele Tasten auf diese Weise verwaltet, wird aber schnell groß, langsam und inkompatibel mit anderen Plugins.  
      Unter /usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/keymap.xml findet sich ein Template für eine Tastenbelegung, die unter openATV auf Gigablue Quad lauffähig ist.  
      Ich empfehle, den Inhalt der /usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/keymap.xml in die /usr/share/enigma2/keymap.usr zu kopieren und dort weiter zu ändern, dann bleiben die Änderungen nach einem Update von SpecialJump erhalten.  
      Änderungen der Tastenbelegung sind in dieser Datei einfach möglich, die Namen sollten halbwegs selbsterklärend sein.  
      Tipp: Unerwünschte Doppel-Aktionen können entstehen, wenn z.B. die gewünschte neue Tastenfunktion beim Drücken (flags="m") und die bisherige Tastenfunktion beim Loslassen (flags="b") ausgelöst wird.  
      In diesem Fall kann die bisherige Tastenfunktion durch den folgenden Eintrag "ausgeschaltet" werden:  
      `<key id="KEY_XXXX"   mapto="specialjump_doNothing"   flags="b" />`

3. Und warum wird in dieses Anleitung nicht die default-Tastenbelegung beschrieben?  
      SpecialJump ist in dieser Hinsicht kein "ready to use"-Plugin. Ich möchte die User motivieren, selbst in die lokale keymap.xml zu gucken und sie an die eigenen Bedürfnisse anzupassen. Meine private Version der keymap ist im gleichen Verzeichnis abgelegt, die enthält aber mehr, als die meisen User brauchen, und sie erfordert ein paar Änderungen der globalen keymap, das ist darin beschrieben.

4. Wozu dient das "Zap speed limit"?  
      Die Begrenzung der Zap-Geschwindigkeit macht nur Sinn, wenn die keymap.xml so eingestellt ist, dass ein langer Tastendruck auf P+ bzw. P- zum fortlaufenden Kanalwechsel führt:  
      `<key id="KEY_CHANNELDOWN" mapto="specialjump_channelDown" flags="mr" />`  
      `<key id="KEY_CHANNELUP"   mapto="specialjump_channelUp"   flags="mr" />`  
      `<key id="KEY_CHANNELDOWN" mapto="specialjump_doNothing"   flags="bl" />`  
      `<key id="KEY_CHANNELUP"   mapto="specialjump_doNothing"   flags="bl" />`  

      Die Begrenzung verhindert, dass dabei Kanäle übersprungen werden. Allerdings geht durch diese keymap-Variante die Doppelbelegung der Tasten (PIP zap) verloren.
      
5. Warum die Doppelbelegung von P+/P-?  
      Bei manchen Universal-Fernbedienungen (z.B. Sony RM-VLZ620T) sind P+ und P- wesentlich besser zugänglich als PLAY und PAUSE.  
      Mindestens im MoviePlayer ist es daher sehr komfortabel, den Film mit P- pausieren und mit P+ fortsetzen zu können.
      Die Funktion, auch das live-TV mit P- pausieren zu können, wenn der Timeshift-Buffer eine gewisse Größe erreicht hat, ist sicher nicht jedermanns Sache und lässt sich daher deaktivieren.

6. Wird die Sprungzeit (z.B. "jump +0:15") immer korrekt angezeigt?  
      Angezeigt wird die Summe der Sprungzeiten seit dem letzten Timeout, also seit die Infobar sichtbar ist.
      Wird innerhalb einer Aufnahme oder innerhalb des Timeshift-Buffers gesprungen, ist diese Zeitangabe korrekt und gibt z.B. am Ende an, wie lang die Werbepause war, die man übersprungen hat.  
      An den Dateigrenzen (SOF, EOF) können Sprünge aber evtl. nicht voll ausgeführt werden. In diesem Fall wird die gewollte, nicht die tatsächliche Sprungdistanz weiter aufsummiert, ebenso bei nicht ausgeführten Sprüngen nach vorn beim live-TV.

7. Wie kann ich die SpecialJump-Infobar skinnen?  
      Die Skins aller Screens sind in plugin.py eingebettet, können aber durch Einträge in anderen skins, z.B. der skin\_user.xml, überschrieben werden.  
      Ein Template dafür, das auch die richtigen Screen-Namen enthält, liegt unter /usr/lib/enigma2/python/Plugins/Extensions/SpecialJump/skin.xml - Diese Datei wird aber an dieser Stelle nicht verwendet und dient nur als Vorlage für Zusätze zur eigenen skin\_user.xml.

8. Wie lassen sich die Farbtasten mit den neuen Funktionen belegen?  
      Hierzu ist es erforderlich, die Normalbelegung der Farbtasten zu deaktivieren:  
      menu - system - settings - button setup - use image color buttons - no (bzw. in den settings: config.plisettings.ColouredButtons=false)  
      Außerdem kann es noch weitere Funktionen im Image geben, die in der keymap deaktiviert werden müssen (vgl. Q2). Daraus ergibt sich z.B. ein keymap-Eintrag wie folgt:  
      `<map context="SpecialJumpActions">`  
      ` <key id="KEY_RED" mapto="specialjump_jump1" flags="m" />`  
      `  <key id="KEY_RED" mapto="specialjump_doNothing" flags="brl" />`  
      `</map>`  
      `<map context="SpecialJumpMoviePlayerActions">`  
      `  <key id="KEY_RED" mapto="specialjump_jump1" flags="m" />`  
      `  <key id="KEY_RED" mapto="specialjump_doNothing" flags="brl" />`  
      `</map>`

9. Wer hat Dir geholfen, dieses Plugin zu schreiben?  
      So direkt eigentlich niemand. Die meisten Fragen, die ich in diversen Foren gestellt habe, waren leider so speziell, dass ich sie mir nur selbst durch Suchen und Probieren beantworten konnte. "Print" und Google waren meine besten Freunde.
      Die wertvollste Hilfe kam aus dem Quellcode anderer Plugins, ich danke insbesondere Dr.Best (Quickbutton), Emanuel (MultiQuickButton) und vlamo (Record Infobar), bei denen ich Anleihen genommen habe.




Revision History:
-----------------

0.1  
Initial version

0.2  
Removed EMC stuff, should work without EMC.  
Corrected skin names, added template skin.xml

0.3  
Changed default, SpecialJump not in main menu  
Packed public keymap.xml into .ipk

0.4  
Changes of settings (window positions, jump distance and actions) take effect immediately  
Stable startup (self.Infobar\_instance before self.SpecialJumpEventTracker\_instance)

0.5  
Added "small SpecialJump"  
Handle number keys also outside movie player: NumberZap in live TV, jump in timeshift including optional muting
    
0.6  
Control file: "Architecture: mips32el"

0.7  
Fixed zap blocking problem (system time is sometimes adjusted by several seconds when switching channels, causing zap block due to wrong speed limit detection, now using timers instead of system time)  
Added display blanking

0.8  
Fixed wrong "display blanking" state variable after power-on from standby, this sometimes required pressing the "toggleLCDBlanking" key twice  
When mixing "short" and "long" SpecialJumps, now the initial jump distance is used for every new type of SpecialJumps

0.9  
Fixed potential issues with empty subtitlelist

1.0  
Workaround for Gigablue Quad/Plus driver 2014.12.16 for jumping into TS buffer from live TV (config.plugins.SpecialJump.algoVersion=2)  
Added EMC parental control  
Fix infobar control by show_infobar_on_jumpPreviousNextMark

Postponed:  
Replaced config.xxx.getValue() by config.xxx.value / postponed for compatibility with old images where .value always returned a string for int's

Optional future features:  
Jump back from live TV into active recording after switching to the same channel
