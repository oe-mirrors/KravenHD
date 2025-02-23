# -*- coding: utf-8 -*-

#  Servive Name Event Nobile Converter
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

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceReference, eEPGCache
from Components.Element import cached
from time import localtime
import re

class KravenHDServiceNameEventNobile(Converter, object):
    NAMEVENT = 0
    NEXTEVENT = 1
    STARTTIME = 2
    DURATION = 3
    ENDTIME = 4
    EXTENDED_DESCRIPTION = 5
    EXTENDED_DESCRIPTION_EVENT = 6

    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgQuery = eEPGCache.getInstance().lookupEventTime
        if type == 'NameAndEvent':
            self.type = self.NAMEVENT
        elif type == 'NextEvent':
            self.type = self.NEXTEVENT
        elif type == 'StartTime':
            self.type = self.STARTTIME
        elif type == 'Duration':
            self.type = self.DURATION
        elif type == 'EndTime':
            self.type = self.ENDTIME
        elif type == 'ExtendedDescription':
            self.type = self.EXTENDED_DESCRIPTION
        elif type == 'ExtendedDescriptionEvent' or type == 'ExtendedDescriptionEventSingle':
            self.type = self.EXTENDED_DESCRIPTION_EVENT

    @cached
    def getText(self):
        no_desc = ''
        if self.type != self.EXTENDED_DESCRIPTION_EVENT:
            service = self.source.service
            if isinstance(service, iPlayableServicePtr):
                info = service and service.info()
                ref = None
            else:
                info = service and self.source.info
                ref = service
            if info is None:
                return no_desc
            if self.type == self.NAMEVENT:
                name = ref and info.getName(ref)
                if name is None:
                    name = info.getName()
                name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                act_event = info and info.getEvent(0)
                if not act_event and info:
                    refstr = info.getInfoString(iServiceInformation.sServiceref)
                    act_event = self.epgQuery(eServiceReference(refstr), -1, 0)
                if act_event is None:
                    return '%s - %s' % (name, no_desc)
                else:
                    return '%s - %s' % (name, act_event.getEventName())
            act_event = None
            try:
                act_event = self.epgQuery(eServiceReference(service.toString()), -1, 1)
            except:
                pass

            if act_event is None:
                return no_desc
        else:
            act_event = self.source.event
            if act_event is None:
                return no_desc
        if self.type == self.NEXTEVENT:
            return act_event.getEventName()
        elif self.type == self.STARTTIME:
            t = localtime(act_event.getBeginTime())
            return '%02d:%02d' % (t.tm_hour, t.tm_min)
        elif self.type == self.ENDTIME:
            t = localtime(act_event.getBeginTime() + act_event.getDuration())
            return '%02d:%02d' % (t.tm_hour, t.tm_min)
        elif self.type == self.DURATION:
            return '%d min' % int(act_event.getDuration() / 60)
        elif self.type == self.EXTENDED_DESCRIPTION or self.type == self.EXTENDED_DESCRIPTION_EVENT:
            short = act_event.getShortDescription()
            tmp = act_event.getExtendedDescription()
            if tmp == '' or tmp is None:
                tmp = short
                if tmp == '' or tmp is None:
                    tmp = no_desc
                else:
                    tmp = tmp.strip()
            else:
                tmp = tmp.strip()
                if short != '' or short is not None:
                    if len(short) > 3:
                        if short[:-2] not in tmp:
                            tmp = short.strip() + '...' + tmp
            tmp = tmp.replace('\r', ' ').replace('\n', ' ').replace('\xc2\x8a', ' ')
            return re.sub('[\\s\t]+', ' ', tmp)
        else:
            return 'Error reading EPG data'

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart, iPlayableService.evUpdatedEventInfo):
            Converter.changed(self, what)
