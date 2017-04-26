#   Copyright (C) 2017 Lunatixz
#
#
# This file is part of MediaMirror
#
# MediaMirror is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaMirror is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MediaMirror.  If not, see <http://www.gnu.org/licenses/>.

import re, socket, json, copy, os, traceback, requests, datetime, time
import xbmc, xbmcgui, xbmcaddon

# Plugin Info
ADDON_ID = 'service.mediamirror'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
LANGUAGE = REAL_SETTINGS.getLocalizedString
DEBUG = REAL_SETTINGS.getSetting('enableDebug') == "true"
POLL = int(REAL_SETTINGS.getSetting('pollTIME'))
socket.setdefaulttimeout(30)

def log(msg, level = xbmc.LOGDEBUG):
    if DEBUG == False and level != xbmc.LOGERROR:
        return
    elif level == xbmc.LOGERROR:
        msg += ' ,' + traceback.format_exc()
    xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + str(msg), level)
       
def ascii(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('ascii', 'ignore')
    return string
    
def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('utf-8', 'ignore' )
        else:
           string = ascii(string)
    return string
     
def sendJSON(command):
    data = ''
    try:
        data = xbmc.executeJSONRPC(uni(command))
    except UnicodeEncodeError:
        data = xbmc.executeJSONRPC(ascii(command))
    return uni(data)

def SendRemote(IPP, AUTH, CNUM, params):
    log('SendRemote, IPP = ' + IPP)
    try:
        xbmc_host, xbmc_port = IPP.split(":")
        user, password = AUTH.split(":")
        kodi_url = 'http://' + xbmc_host +  ':' + xbmc_port + '/jsonrpc'
        headers = {'Content-Type': 'application/json'}
        time_before = time.time()
        r = requests.post(
                kodi_url,
                data=json.dumps(params),
                headers=headers,
                auth=(user,password))
        time_after = time.time() 
        time_taken = time_after-time_before
        REAL_SETTINGS.setSetting("Client%d_latency"%CNUM,("%.2f" % round(time_taken,2)))
        xbmc.sleep(1000) #arbitrary sleep to avoid network flood
        return r.json()
    except Exception,e:
        log('SendRemote, failed! ' + str(e), xbmc.LOGERROR)
    
    
class Player(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self, xbmc.Player())
        
        
    def onPlayBackStarted(self):
        log('onPlayBackStarted')
        self.playClient(self.Service.Monitor.IPPlst)
        
        
    def onPlayBackEnded(self):
        log('onPlayBackEnded')
            
        
    def onPlayBackStopped(self):
        log('onPlayBackStopped')
        self.stopClient(self.Service.Monitor.IPPlst)
        
        
    def onPlayBackPaused(self):
        log('onPlayBackPaused')
        self.pauseClient(self.Service.Monitor.IPPlst)

        
    def onPlayBackResumed(self):
        log('onPlayBackResumed')
        self.resumeClient(self.Service.Monitor.IPPlst)
        
        
    def onPlayBackSpeedChanged(self):
        log('onPlayBackSpeedChanged')
        self.playClient(self.Service.Monitor.IPPlst)
        
        
    def onPlayBackSeekChapter(self):
        log('onPlayBackSeekChapter')
        self.playClient(self.Service.Monitor.IPPlst)
        
        
    def onPlayBackSeek(self):
        log('onPlayBackSeek')
        self.playClient(self.Service.Monitor.IPPlst)

        
    def getPlayerFile(self):
        log('getPlayerFile')
        try:
            return (self.getPlayingFile()).replace("\\\\","\\")
        except:
            return ''
            
            
    def getPlayerTime(self):
        log('getPlayerTime')
        try:
            return self.getTime()
        except:
            return 0
             
             
    def getPlayerTitle(self):
        log('getPlayerTitle')
        try:
            return (xbmc.getInfoLabel('VideoPlayer.TVShowTitle') or xbmc.getInfoLabel('VideoPlayer.Title') or xbmc.getInfoLabel('Player.Title'))
        except:
            return ''

            
    def playClient(self, IPPlst):
        log('playClient')
        file = self.getPlayerFile()
        seekValue = self.getPlayerTime()
        for IPP in IPPlst:
            if seekValue > 0:
                seek = str(datetime.timedelta(seconds=seekValue))
                log('playClient, seek = ' + seek)
                seek = seek.split(":")
                try:
                    hours = int(seek[0])
                except:
                    hours = 0
                try:
                    minutes = int(seek[1])
                except:
                    minutes = 0
                Mseconds = str(seek[2])
                seconds = int(Mseconds.split(".")[0])
                try:
                    milliseconds = int(Mseconds.split(".")[1])
                    milliseconds = int(str(milliseconds)[:3])
                except:
                    milliseconds = 0        
                milliseconds + IPP[2] #add user offset.
                params = ({"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"file": file},"options":{"resume":{"hours":hours,"minutes":minutes,"seconds":seconds,"milliseconds":milliseconds}}}})
            else:
                params = ({"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"path": file}}})
            SendRemote(IPP[0], IPP[1], IPP[3], params)

            
    def stopClient(self, IPPlst):
        log('stopClient')
        params = ({"jsonrpc":"2.0","id":1,"method":"Player.Stop","params":{"playerid":1}})       
        for IPP in IPPlst: 
            SendRemote(IPP[0], IPP[1], IPP[3], params)
        
        
    def pauseClient(self, IPPlst):
        log('pauseClient')
        params = ({"jsonrpc":"2.0","id":1,"method":"Input.ExecuteAction","params":{"action":"pause"}})
        for IPP in IPPlst: 
            SendRemote(IPP[0], IPP[1], IPP[3], params)
        
        
    def resumeClient(self, IPPlst):
        log('resumeClient')
        params = ({"jsonrpc":"2.0","id":1,"method":"Input.ExecuteAction","params":{"action":"play"}})       
        for IPP in IPPlst: 
            SendRemote(IPP[0], IPP[1], IPP[3], params)
        
        
    def playlistClient(self, IPPlst, file):
        log('PlaylistUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Player.Open","params":{"item": {"file": file}}})
        for IPP in IPPlst: 
            SendRemote(IPP[0], IPP[1], IPP[3], params)
             

class Monitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self, xbmc.Monitor())
        self.IPPlst = []
      
      
    def onSettingsChanged(self):
        log("onSettingsChanged")
        DEBUG = REAL_SETTINGS.getSetting('enableDebug') == "true"
        POLL = int(REAL_SETTINGS.getSetting('pollTIME'))
        self.initClients()
        
        
    def initClients(self):
        log('initClients')
        self.IPPlst = []
        for i in range(1,6):
            if REAL_SETTINGS.getSetting("Client%d"%i) == "true":
                self.IPPlst = [[REAL_SETTINGS.getSetting("Client%d_IPP"%i),REAL_SETTINGS.getSetting("Client%d_UPW"%i),float(REAL_SETTINGS.getSetting('Client%d_offSet'%i)),i]]
        log('initClients, IPPlst = ' + str(self.IPPlst))
        
        
class Service():
    def __init__(self):
        self.Player = Player()
        self.Monitor = Monitor()
        self.Player.Service  = self
        self.start()

    #todo disable client screensaver, restore on stop and quit

    def chkClients(self):
        #check if clients are playing the same content, ie "insync", return "outofsync"
        failedLst = []
        for IPPlst in self.Monitor.IPPlst:
            for i in range(3):
                try:
                    # try to find clients activeplayer... no known json request?
                    params = ({"jsonrpc":"2.0","id":1,"method":"Player.GetItem","params":{"playerid":i,"properties":["title"]}})
                    json_responce = SendRemote(IPPlst[0], IPPlst[1], IPPlst[3], params)
                    if json_responce:
                        break
                except:
                    log("chkClients, Invalid ActivePlayer %d"%i)
            log("chkClients, IPP = " + str(IPPlst[0]))
            if 'result' in json_responce and 'item' in json_responce['result']:
                if 'file' in json_responce['result']['item']:
                    clientFile  = json_responce['result']['item']['file']
                    log("chkClients, clientFile = " + clientFile)       
                    if clientFile != self.Player.getPlayerFile():
                        failedLst.append(IPPlst)
                else:
                    #not all items contain a file, ex. pvr, playlists. so check title.
                    clientTitle = (json_responce['result']['item'].get('title','') or json_responce['result']['item'].get('label',''))
                    log("chkClients, clientTitle = " + clientTitle) 
                    if clientTitle != self.Player.getPlayerTitle():
                        failedLst.append(IPPlst)
            else:
                log("chkClients, json_responce = " + str(json_responce))
        return failedLst
        
        
    def syncClients(self, IPPlst):
        self.Player.playClient(IPPlst)
        
        
    def start(self):
        sleep = 0
        self.Monitor.initClients()
        while not self.Monitor.abortRequested():
            if xbmcgui.Window(10000).getProperty("PseudoTVRunning") != "True":
                if self.Player.isPlayingVideo() == True and len(self.Monitor.IPPlst) > 0:
                    if sleep > POLL:
                        sleep = 0
                        self.syncClients(self.chkClients())
                    else:
                        sleep += 1
            if self.Monitor.waitForAbort(1):
                break
        self.Player.stopClient(self.Monitor.IPPlst)
Service()