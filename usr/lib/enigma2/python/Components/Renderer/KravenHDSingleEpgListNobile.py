# -*- coding: utf-8 -*-

#  Single EPG List Nobile Renderer
#
#  Coded/Modified/Adapted by oerlgrey
#  Based on openATV image source code
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#
#  If you think this license infringes any rights,
#  please contact me at ochzoetna@gmail.com

from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache
from Components.Renderer.Renderer import Renderer
from time import localtime

class KravenHDSingleEpgListNobile(Renderer, VariableText):
    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.epgcache = eEPGCache.getInstance()

    GUI_WIDGET = eLabel

    def changed(self, what):
        event = self.source.event
        if event is None:
            self.text = ''
            return
        service = self.source.service
        text = ''
        evt = None
        if self.epgcache is not None:
            evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(), 0, -1, -1)])
        if evt:
            maxx = 0
            for x in evt:
                if maxx > 1:
                    if x[4]:
                        t = localtime(x[1])
                        text = text + '%02d:%02d %s\n' % (t[3], t[4], x[4])
                    else:
                        text = text + 'n/a\n'
                maxx += 1
                if maxx > 31:
                    break

        self.text = text
