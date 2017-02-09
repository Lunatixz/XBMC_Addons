#   Copyright (C) 2017 Lunatixz
#
#
# This file is part of Mirror Service.
#
# Mirror Service is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mirror Service is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mirror Service.  If not, see <http://www.gnu.org/licenses/>.

import string, re, socket, json, copy, os, requests, datetime, time
import xbmc, xbmcgui, xbmcaddon, xbmcvfs

# Plugin Info
ADDON_ID      = 'script.mirror.service'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID      = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME    = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH    = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC  = REAL_SETTINGS.getAddonInfo('profile')
ICON          = os.path.join(ADDON_PATH, 'icon.png')
FANART        = os.path.join(ADDON_PATH, 'fanart.jpg')
POLL          = int(REAL_SETTINGS.getSetting('Poll_TIME'))*1000
DEBUG         = REAL_SETTINGS.getSetting('Enable_Debugging') == 'true'
socket.setdefaulttimeout(30)


class Mirror:
    def __init__(self):   
        self.log('__init__')
        self.initUPNP() # collect upnp mirror ips/pw
        self.notPlayingCount = 0
         
    # def onInit(self):
        # self.IPPlst, self.AUTHlst = self.initUPNP() # collect upnp mirror ips/pw
        
        
    def log(self, msg, level = xbmc.LOGDEBUG):
        if DEBUG == True:
            xbmc.log(ADDON_ID + '-Mirror: ' + msg, level)
        
        
    def initUPNP(self):
        self.log('initUPNP')
        self.IPPlst = []
        self.AUTHlst = []

        #UPNP Clients
        if REAL_SETTINGS.getSetting("UPNP1") == "true":
            self.IPPlst.append(REAL_SETTINGS.getSetting("UPNP1_IPP"))
            self.AUTHlst.append(REAL_SETTINGS.getSetting("UPNP1_UPW"))
        if REAL_SETTINGS.getSetting("UPNP2") == "true":
            self.IPPlst.append(REAL_SETTINGS.getSetting("UPNP2_IPP"))
            self.AUTHlst.append(REAL_SETTINGS.getSetting("UPNP2_UPW"))
        if REAL_SETTINGS.getSetting("UPNP3") == "true":
            self.IPPlst.append(REAL_SETTINGS.getSetting("UPNP3_IPP"))
            self.AUTHlst.append(REAL_SETTINGS.getSetting("UPNP3_UPW"))
        if REAL_SETTINGS.getSetting("UPNP4") == "true":
            self.IPPlst.append(REAL_SETTINGS.getSetting("UPNP4_IPP"))
            self.AUTHlst.append(REAL_SETTINGS.getSetting("UPNP4_UPW"))
        if REAL_SETTINGS.getSetting("UPNP5") == "true":
            self.IPPlst.append(REAL_SETTINGS.getSetting("UPNP5_IPP"))
            self.AUTHlst.append(REAL_SETTINGS.getSetting("UPNP5_UPW"))
        
        
    def RequestExtJson(self, IPP, AUTH, params):
        self.log('RequestExtJson, IPP = ' + IPP)
        try:
            xbmc_host, xbmc_port = IPP.split(":")
            user, password = AUTH.split(":")
            kodi_url = 'http://' + xbmc_host +  ':' + xbmc_port + '/jsonrpc'
            headers = {'Content-Type': 'application/json'}
            r = requests.post(
                    kodi_url,
                    data=json.dumps(params),
                    headers=headers,
                    auth=(user,password)) 
            return r.json()
        except Exception,e:
            self.log('RequestExtJson, failed! ' + str(e), xbmc.LOGERROR)
            
            
    def SendExtJson(self, IPP, params):
        self.log('SendExtJson, IPP = ' + IPP)
        try:
            xbmc_host, xbmc_port = IPP.split(":")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((xbmc_host, 9090))
            params2 = copy.copy(params)
            params2["jsonrpc"] = "2.0"
            params2["id"] = 1
            s.send(json.dumps(params2))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except Exception,e:
            self.log('SendExtJson, failed! ' + str(e), xbmc.LOGERROR)


    def isPlayingUPNP(self, IPP, AUTH, label, file):
        self.log('isPlayingUPNP, IPP = ' + IPP)
        params = ({"jsonrpc":"2.0","id":1,"method":"Player.GetItem","params":{"playerid":1,"properties":["title"]}})
        json_detail = self.RequestExtJson(IPP, AUTH, params)

        try:
            playing_label = json_detail['result']['item']['title']
        except:
            playing_label = ''
        try:
            playing_file = json_detail['result']['item']['file']
        except:
            playing_file = ''
    
        self.log('isPlayingUPNP, ' + label.lower() + ' ?=? ' + playing_label.lower())
        self.log('isPlayingUPNP, ' + file + ' ?=? ' + playing_file)
        
        if file == playing_file:
            self.notPlayingCount = 0
            return True       
        elif label.lower() == playing_label.lower():
            self.notPlayingCount = 0
            return True

        self.notPlayingCount += 1
        return False
            
         
    def chkUPNP(self, label, file, seektime): 
        self.log('chkUPNP') 
        for i in range(len(self.IPPlst)):   
            if self.isPlayingUPNP(self.IPPlst[i], self.AUTHlst[i], label, file) == False and self.notPlayingCount > 3:
                self.log('chkUPNP, ' + str(self.IPPlst[i]) + ' not playing') 
                if seektime > 0:
                    seek = str(datetime.datetime.timedelta(seconds=seektime))
                    self.log('chkUPNP, seek = ' + seek)
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
                    millisecondOFFSET = float(REAL_SETTINGS.getSetting("UPNP_OFFSET"))
                    milliseconds + millisecondOFFSET
                    params = ({"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"file": file},"options":{"resume":{"hours":hours,"minutes":minutes,"seconds":seconds,"milliseconds":milliseconds}}}})
                else:
                    params = ({"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"path": file}}})
                self.SendExtJson(self.IPPlst[i],params)


    def SendUPNP(self, label, file, seektime):
        self.log('SendUPNP')
        for i in range(len(self.IPPlst)): 
            if seektime > 0:
                seek = str(datetime.datetime.timedelta(seconds=seektime))
                self.log('SendUPNP, seek = ' + seek)
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
                millisecondOFFSET = float(REAL_SETTINGS.getSetting("UPNP_OFFSET"))
                milliseconds + millisecondOFFSET
                params = ({"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"file": file},"options":{"resume":{"hours":hours,"minutes":minutes,"seconds":seconds,"milliseconds":milliseconds}}}})
            else:
                params = ({"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": {"path": file}}})
            self.SendExtJson(self.IPPlst[i],params)

            
    def StopUPNP(self):
        self.log('StopUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Player.Stop","params":{"playerid":1}})       
        for i in range(len(self.IPPlst)):  
            self.SendExtJson(self.IPPlst[i],params)
        
        
    def PauseUPNP(self):
        self.log('PauseUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Input.ExecuteAction","params":{"action":"pause"}})
        for i in range(len(self.IPPlst)):  
            self.SendExtJson(self.IPPlst[i],params)
        
        
    def ResumeUPNP(self):
        self.log('ResumeUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Input.ExecuteAction","params":{"action":"play"}})       
        for i in range(len(self.IPPlst)):  
            self.SendExtJson(self.IPPlst[i],params)
        
        
    def RWUPNP(self):
        self.log('RWUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Input.ExecuteAction","params":{"action":"stepback"}})          
        for i in range(len(self.IPPlst)):  
            self.SendExtJson(self.IPPlst[i],params)
        
        
    def FFUPNP(self):
        self.log('FFUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Input.ExecuteAction","params":{"action":"stepforward"}})
        for i in range(len(self.IPPlst)):  
            self.SendExtJson(self.IPPlst[i],params)
        
        
    def PlaylistUPNP(self, IPP, file):
        self.log('PlaylistUPNP')
        params = ({"jsonrpc":"2.0","id":1,"method":"Player.Open","params":{"item": {"file": file}}})
        for i in range(len(self.IPPlst)):  
            self.SendExtJson(self.IPPlst[i],params) 
           
class MyPlayer(xbmc.Player):
    def __init__(self):
        self.log('__init__')
        xbmc.Player.__init__(self, xbmc.Player())   
        self.Upnp = Mirror()


    def log(self, msg, level = xbmc.LOGDEBUG):
        if DEBUG == True:
            xbmc.log(ADDON_ID + '-MyPlayer: ' + msg, level)
        
        
    def getPlayerFile(self):
        self.log('getPlayerFile')
        try:
            return (self.getPlayingFile()).replace("\\\\","\\")
        except:
            return ''
            
            
    def getPlayerTime(self):
        self.log('getPlayerTime')
        try:
            return self.getTime()
        except:
            return 0
             
             
    def getPlayerTitle(self):
        self.log('getPlayerTitle')
        try:
            title = xbmc.getInfoLabel('Player.Title')
            if not title:
                title = xbmc.getInfoLabel('VideoPlayer.Title')
        except:
            title = ''
        return title
        
        
    def isPlaybackValid(self):
        Playing = False
        xbmc.sleep(10)
        if self.isPlaying():
            Playing = True
        self.log('isPlaybackValid = ' + str(Playing))
        return Playing
        
        
    def onPlayBackPaused(self):
        self.log('onPlayBackPaused')
        self.UPNPcontrol('pause')

        
    def onPlayBackResumed(self):
        self.log('onPlayBackResumed')
        self.UPNPcontrol('resume')

        
    def onPlayBackStarted(self):
        self.log('onPlayBackStarted')     
        self.UPNPcontrol('play', self.getPlayerTitle(), self.getPlayerFile(), self.getPlayerTime())          
            
            
    def onPlayBackStopped(self):
        self.log('onPlayBackStopped')
        self.UPNPcontrol('stop')

        
    def UPNPcontrol(self, func, label='', file='', seektime=0):
        self.log('UPNPcontrol')
        self.Upnp.initUPNP()
        if len(self.Upnp.IPPlst) > 0:
            if func == 'play':
                self.Upnp.SendUPNP(label, file, seektime)
            elif func == 'stop':
                self.Upnp.StopUPNP()
            elif func == 'resume':
                self.Upnp.ResumeUPNP()
            elif func == 'pause':
                self.Upnp.PauseUPNP()
            elif func == 'rwd':
                self.Upnp.RWUPNP()
            elif func == 'fwd':
                self.Upnp.FFUPNP()
            elif func == 'chkplay':
                self.Upnp.chkUPNP(label, file, seektime)     
   
class Service():
    def __init__(self):
        self.myPlayer = MyPlayer() 
        while not xbmc.abortRequested:
            if self.myPlayer.isPlaybackValid() and xbmcgui.Window(10000).getProperty('PseudoTVRunning') != 'True':
                self.myPlayer.log(monitor.getPlayerTitle() +','+ monitor.getPlayerFile() +','+ str(monitor.getPlayerTime()))
                self.myPlayer.Upnp.chkUPNP(monitor.getPlayerTitle(), monitor.getPlayerFile(), monitor.getPlayerTime())
            xbmc.sleep(POLL)
Service()