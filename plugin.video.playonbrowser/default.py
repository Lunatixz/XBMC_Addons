#   Copyright (C) 2017 Lunatixz
#
#
# This file is part of Playon Browser
#
# Playon Browser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Playon Browser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Playon Browser.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, re, sys, random, traceback
import urlparse, urllib, urllib2, htmllib, threading, socket
import xbmc, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs
import xml.etree.ElementTree as ElementTree 

if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json
    
# Plugin Info
ADDON_ID      = 'plugin.video.playonbrowser'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID      = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME    = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH    = REAL_SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
ICON          = os.path.join(ADDON_PATH, 'icon.png')
FANART        = os.path.join(ADDON_PATH, 'fanart.jpg')

# Playon Info
MEDIA_PATH    = ADDON_PATH + '/resources/media/' 
PLAYON_ICON   = '/images/play_720.png'
PLAYON_DATA   = '/data/data.xml'
BASE_URL      = sys.argv[0]
BASE_HANDLE   = int(sys.argv[1])
args          = urlparse.parse_qs(sys.argv[2][1:])
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
TIMEOUT       = 15
random.seed()
socket.setdefaulttimeout(TIMEOUT)
playDirect       = REAL_SETTINGS.getSetting("playDirect") == "true"
if xbmcgui.Window(10000).getProperty('PseudoTVRunning') == "True":
    playDirect   = False
    
kodiLibrary      = False #todo strm contextMenu
debug            = REAL_SETTINGS.getSetting("debug") == "true"
useUPNP          = REAL_SETTINGS.getSetting("useUPNP") == "true"
cache            = REAL_SETTINGS.getSetting('cache') == "true"

try:
    from metahandler import metahandlers
    metaget = metahandlers.MetaData(preparezip=False, tmdb_api_key=REAL_SETTINGS.getSetting("TMDB_API_KEY"))
    Meta_Enabled = REAL_SETTINGS.getSetting("meta") == "true"
except Exception,e:
    print str(e)
    Meta_Enabled = False
    
# Commoncache plugin import
try:
    import StorageServer
except Exception,e:
    import storageserverdummy as StorageServer
    cache = False 
cachedata = StorageServer.StorageServer(ADDON_PATH,1)

displayCategories = {'MoviesAndTV': 3,
                    'Comedy': 128,
                    'News': 4,
                    'Sports': 8,
                    'Kids': 16,
                    'Music': 32,
                    'VideoSharing': 64,
                    'LiveTV': 2048,
                    'MyMedia': 256,
                    'Plugins': 512,
                    'Other': 1024}
                        
displayTitles = {'MoviesAndTV': 'Movies And TV',
                'News': 'News',
                'Popular': 'Popular',
                'All': 'All',
                'Sports': 'Sports',
                'Kids': 'Kids',
                'Music': 'Music',
                'VideoSharing': 'Video Sharing',
                'Comedy': 'Comedy',
                'MyMedia': 'My Media',
                'Plugins': 'Plugins',
                'Other': 'Other',
                'LiveTV': 'Live TV'}
                    
displayImages = {'MoviesAndTV': '/images/categories/movies.png',
                'News': '/images/categories/news.png',
                'Popular': '/images/categories/popular.png',
                'All': '/images/categories/all.png',
                'Sports': '/images/categories/sports.png',
                'Kids': '/images/categories/kids.png',
                'Music': '/images/categories/music.png',
                'VideoSharing': '/images/categories/videosharing.png',
                'Comedy': '/images/categories/comedy.png',
                'MyMedia': '/images/categories/mymedia.png',
                'Plugins': '/images/categories/plugins.png',
                'Other': '/images/categories/other.png',
                'LiveTV': '/images/categories/livetv.png'}

def log(msg, level = xbmc.LOGDEBUG):
    print msg
    # if level == xbmc.LOGERROR:
        # msg += ' ,' + traceback.format_exc()
    # if debug != True and level == xbmc.LOGDEBUG:
        # return
    # xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + msg, level)

def chkUPNP(url):
    json_query = ('{"jsonrpc":"2.0","method":"Files.GetDirectory","params":{"directory":"%s"},"id":1}'%url)      
    data       = json.loads(xbmc.executeJSONRPC(json_query))
    try:
        if not data['result']['files'][0]['file'].endswith('/playonprovider/'):
            url = ''
    except:
        url = ''
    log('chkUPNP, url = ' + url)
    return url
        
def getUPNP():
    log('getUPNP')
    upnpID = chkUPNP(REAL_SETTINGS.getSetting("playonUPNPid"))
    if len(upnpID) > 0:
        return upnpID
    else:
        json_query = ('{"jsonrpc":"2.0","method":"Files.GetDirectory","params":{"directory":"upnp://"},"id":1}')      
        data       = json.loads(xbmc.executeJSONRPC(json_query))
        if 'result' in data and len(data['result']['files']) != 0:
            for item in data['result']['files']:
                if (item['label']).lower().startswith('playon'):
                    REAL_SETTINGS.setSetting("playonUPNPid",item['file'].rstrip('/'))
                    return item['file']
        upnpID = xbmcgui.Dialog().browse(0, 'Select Playon: Server, Click "OK"', 'files', '', False, False, 'upnp://')
        if upnpID != -1:
            REAL_SETTINGS.setSetting("playonUPNPid",upnpID.rstrip('/'))
            return upnpID
    
def folderIcon(val):
    log('folderIcon')
    return random.choice(['/images/folders/folder_%s_0.png' %val,'/images/folders/folder_%s_1.png' %val])

def addDir(name,description,u,thumb=ICON,ic=ICON,fan=FANART,infoList=False,infoArt=False,content_type='movies'):
    log('addDir: ' + name)
    liz = xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'false')

    if kodiLibrary == True:
        contextMenu = []
        contextMenu.append(('Create Strms','XBMC.RunPlugin(%s)'%(build_url({'mode': 'strmDir', 'url':u}))))
        liz.addContextMenuItems(contextMenu)

    if infoList == False:
        liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "mediatype": content_type})
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
        
    if infoArt == False:
        liz.setArt({'thumb': ic, 'fanart': fan})
    else:
        liz.setArt(infoArt) 
    xbmcplugin.addDirectoryItem(handle=BASE_HANDLE,url=u,listitem=liz,isFolder=True)
      
def addLink(name,description,u,thumb=ICON,ic=ICON,fan=FANART,infoList=False,infoArt=False,content_type='movies',total=0):
    log('addLink: ' + name)
    liz = xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'true')
    
    if kodiLibrary == True:
        log('addLink: kodiLibrary = True')
        contextMenu = []
        contextMenu.append(('Create Strm','XBMC.RunPlugin(%s)'%(build_url({'mode': 'strmFile', 'url':u}))))
        liz.addContextMenuItems(contextMenu)

    if infoList == False:
        liz.setInfo(type="video", infoLabels={ "title": name, "plot": description})
        liz.setArt({'thumb': ICON, 'fanart': fan})
    else:
        log('addLink: infoList = True')
        liz.setInfo(type="Video", infoLabels=infoList)
        liz.setArt(infoArt)
    xbmcplugin.addDirectoryItem(handle=BASE_HANDLE,url=u,listitem=liz,totalItems=total)
              
def get_xml(url):
    if cache == True:
        try:
            result = cachedata.cacheFunction(url)
            if len(result) == 0 or result == 'null':
                raise
        except:
            result = get_xml_NEW(url)
    else:
        result = get_xml_NEW(url)
    if not result:
        result = 'null'
    return result  
         
def get_xml_NEW(url):
    log('get_xml: ' + url)
    """ This will pull down the XML content and return a ElementTree. """
    try:
        usock = urllib2.urlopen(url)
        response = usock.read()
        usock.close()
        return ElementTree.fromstring(response)
    except: return False 

def get_argument_value(name):
    log('get_argument_value: ' + name)
    """ pulls a value out of the passed in arguments. """
    if args.get(name, None) is None:
        return None
    else:
        return args.get(name, None)[0]

def build_url(query):
    log('build_url')
    """ This will build and encode the URL for the addon. """
    log(query)
    return BASE_URL + '?' + urllib.urlencode(query)

def build_playon_url(href = ""):
    log('build_playon_url')
    """ This will generate the correct URL to access the XML pushed out by the machine running playon. """
    log('build_playon_url: '+ href)
    if not href:
        return playonInternalUrl + PLAYON_DATA
    else:
        return playonInternalUrl + href

def build_playon_search_url(id, searchterm):
    """ Generates a search URL for the given ID. Will only work with some providers. """
    #TODO: work out the full search term criteria.
    #TODO: Check international encoding.
    searchterm = urllib.quote_plus(searchterm)
    log('build_playon_search_url: '+ id + "::" + searchterm)
    return playonInternalUrl + PLAYON_DATA + "?id=" + id + "&searchterm=dc:description%20contains%20" + searchterm
 
def build_menu_for_mode_none():
    """
        This generates a static structure at the top of the menu tree. 
        It is the same as displayed by m.playon.tv when browsed to. 
    """
    log('build_menu_for_mode_none')
    
    for key, value in sorted(displayCategories.iteritems(), key=lambda (k,v): (v,k)):
        url = build_url({'mode': 'category', 'category':displayCategories[key]})
        image = playonInternalUrl + displayImages[key]
        addDir(displayTitles[key],displayTitles[key],url,image,image)   
    xbmcplugin.endOfDirectory(BASE_HANDLE, cacheToDisc=True)

def build_menu_for_mode_category(category):
    log('build_menu_for_mode_category:' + category)
    ranNum = random.randrange(9)
    """
        This generates a menu for a selected category in the main menu. 
        It uses the category value to & agains the selected category to see if it
        should be shown. 
    """
    """ Pull back the whole catalog
        Sample XMl blob:
            <catalog apiVersion="1" playToAvailable="true" name="server" href="/data/data.xml?id=0" type="folder" art="/images/apple_touch_icon_precomposed.png" server="3.10.13.9930" product="PlayOn">
                <group name="PlayMark" href="/data/data.xml?id=playmark" type="folder" childs="0" category="256" art="/images/provider.png?id=playmark" />
                <group name="PlayLater Recordings" href="/data/data.xml?id=playlaterrecordings" type="folder" childs="0" category="256" art="/images/provider.png?id=playlaterrecordings" />
                <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" childs="0" searchable="true" id="netflix" category="3" art="/images/provider.png?id=netflix" />
                <group name="Amazon Instant Video" href="/data/data.xml?id=amazon" type="folder" childs="0" searchable="true" id="amazon" category="3" art="/images/provider.png?id=amazon" />
                <group name="HBO GO" href="/data/data.xml?id=hbogo" type="folder" childs="0" searchable="true" id="hbogo" category="3" art="/images/provider.png?id=hbogo" />
                ...
    """
    try:
        for group in get_xml(build_playon_url()).getiterator('group'):
            # Category number. 
            if group.attrib.get('category') == None:
                nodeCat = 1024
            else:
                nodeCat = group.attrib.get('category')

            # Art if there is any. 
            if group.attrib.get('art') == None:
                image = playonInternalUrl + folderIcon(ranNum)
            else:
                image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                
            # if we & them and it is not zero add it to this category. otherwise ignore as it is another category.                        
            if int(nodeCat) & int(category) != 0:
                name = group.attrib.get('name').encode('ascii', 'ignore') #TODO: Fix for international characters.
                url = build_url({'mode': group.attrib.get('type'), 
                                 'foldername': name, 
                                 'href': group.attrib.get('href'), 
                                 'nametree': name})
                addDir(name,name,url,image,image)
        xbmcplugin.endOfDirectory(BASE_HANDLE, cacheToDisc=True)
    except:
        pass

def build_menu_for_search(xml):
    log('build_menu_for_search')
    ranNum = random.randrange(9)
    """ 
        Will generate a list of directory items for the UI based on the xml values. 
        This breaks the normal name tree approach for the moment

        Results can have folders and videos. 
        
        Example XML Blob:
        http://192.168.0.140:54479/data/data.xml?id=netflix&searchterm=dc:description%20contains%20american+dad
        <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" art="/images/provider.png?id=netflix" searchable="true" id="netflix" childs="0" category="3">
            <group name="American Dad!" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
        </group>

        http://192.168.0.140:54479/data/data.xml?id=netflix&searchterm=dc:description%20contains%20dog

        <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" art="/images/provider.png?id=netflix" searchable="true" id="netflix" childs="0" category="3">
            <group name="Clifford the Big Red Dog" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="Courage the Cowardly Dog" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="Dogs with Jobs" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="The 12 Dogs of Christmas" href="/data/data.xml?id=netflix-..." type="video" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="12 Dogs of Christmas: Great Puppy Rescue" href="/data/data.xml?id=netflix-..." type="video" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
    """
    try:
        for group in xml.getiterator('group'):
            log(group.attrib.get('href'))
            # This is the top group node, just need to check if we can search. 
            if group.attrib.get('searchable') != None:
                # We can search at this group level. Add a list item for it. 
                name  = "Search" #TODO: Localize
                url   = build_url({'mode': 'search', 'id': group.attrib.get('id')})
                image = playonInternalUrl + folderIcon(ranNum)
                addDir(name,name,url,image,image)  
            else:
                # Build up the name tree.
                name = group.attrib.get('name').encode('ascii', 'ignore')
                desc = group.attrib.get('description')
                
                if group.attrib.get('type') == 'folder':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + folderIcon(ranNum)
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                        
                elif group.attrib.get('type') == 'video':
                    if group.attrib.get('art') == None:
                        image = (playonInternalUrl + PLAYON_ICON)
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')

                url = build_url({'mode': group.attrib.get('type'), 
                                'foldername': name, 
                                'href': group.attrib.get('href'), 
                                'image': image, 
                                'desc': desc, 
                                'parenthref': group.attrib.get('href')}) #,'nametree': nametree + '/' + name
                getMeta('null', name, desc, url, image, group.attrib.get('type'),cnt=len(xml.getiterator('group')))
    except:
        pass
    xbmcplugin.endOfDirectory(BASE_HANDLE, cacheToDisc=True)
                        
def build_menu_for_mode_folder(href, foldername, nametree):
    log("Entering build_menu_for_mode_folder")
    ranNum = random.randrange(9)
    """ 
        Will generate a list of directory items for the UI based on the xml values. 

        The folder could be at any depth in the tree, if the category is searchable
        then we can render a search option. 
        
        Example XML Blob:
            <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" art="/images/provider.png?id=netflix" searchable="true" id="netflix" childs="0" category="3">
                <group name="My List" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
                <group name="Browse Genres" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
                <group name="Just for Kids" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
                <group name="Top Picks for Jon" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
    """
    for group in get_xml(build_playon_url(href)).getiterator('group'):
        try:
            log(group.attrib.get('href') + href)
            # This is the top group node, just need to check if we can search. 
            if group.attrib.get('href') == href:
                if group.attrib.get('searchable') != None:
                    # We can search at this group level. Add a list item for it. 
                    name = "Search" #TODO: Localize
                    url = build_url({'mode': 'search', 'id': group.attrib.get('id')})
                    addDir(name,name,url)
            else:
                # Build up the name tree.
                name = group.attrib.get('name').encode('ascii', 'ignore')
                desc = group.attrib.get('description')
                
                if group.attrib.get('type') == 'folder':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + folderIcon(ranNum)
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')        
                elif group.attrib.get('type') == 'video':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + PLAYON_ICON
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large') 

                if nametree == None:
                    nametree = name
                    url = build_url({'mode': group.attrib.get('type'), 
                                    'foldername': name, 
                                    'href': group.attrib.get('href'), 
                                    'image': image, 
                                    'desc': desc, 
                                    'parenthref': href})
                else:
                    url = build_url({'mode': group.attrib.get('type'), 
                                    'foldername': name, 
                                    'href': group.attrib.get('href'), 
                                    'image': image, 
                                    'desc': desc, 
                                    'parenthref': href, 
                                    'nametree': nametree + '/' + name})
                getMeta(nametree, name, desc, url, image, group.attrib.get('type'),cnt=len(get_xml(build_playon_url(href)).getiterator('group')))
        except Exception,e:
            log("Entering build_menu_for_mode_folder, failed! " + str(e))
    xbmcplugin.endOfDirectory(BASE_HANDLE, cacheToDisc=True)
        
def generate_list_items(xml, href, foldername, nametree):
    log("Entering generate_list_items")
    ranNum = random.randrange(9)
    """ Will generate a list of directory items for the UI based on the xml values. """
    try:
        for group in xml.getiterator('group'):
            if group.attrib.get('href') == href:
                continue
            
            # Build up the name tree. 
            name = group.attrib.get('name').encode('ascii', 'ignore')
            desc = group.attrib.get('description')
            if group.attrib.get('type') == 'folder':
                if group.attrib.get('art') == None:
                    image = playonInternalUrl + folderIcon(ranNum)
                else:
                    image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                    
            elif group.attrib.get('type') == 'video':
                if group.attrib.get('art') == None:
                    image = playonInternalUrl + PLAYON_ICON
                else:
                    image = ((playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')).replace('&size=tiny','&size=large')
                
                url  = build_url({'mode': group.attrib.get('type'), 
                                'foldername': name, 
                                'href': group.attrib.get('href'), 
                                'parenthref': href, 
                                'desc': desc, 
                                'image': image, 
                                'nametree': nametree + '/' + name})
            getMeta(nametree, name, desc, url, image, group.attrib.get('type'),cnt=len(xml.getiterator('group')))
    except:
        pass
    xbmcplugin.endOfDirectory(BASE_HANDLE, cacheToDisc=True)
       
def getTitleYear(showtitle, showyear=0):  
    # extract year from showtitle, merge then return
    try:
        showyear = int(showyear)
    except:
        showyear = showyear
    try:
        labelshowtitle = re.compile('(.+?) [(](\d{4})[)]$').findall(showtitle)
        title = labelshowtitle[0][0]
        year = int(labelshowtitle[0][1])
    except Exception,e:
        try:
            year = int(((showtitle.split(' ('))[1]).replace(')',''))
            title = ((showtitle.split('('))[0])
        except Exception,e:
            if showyear != 0:
                showtitle = showtitle + ' ('+str(showyear)+')'
                year, title, showtitle = getTitleYear(showtitle, showyear)
            else:
                title = showtitle
                year = 0
    if year == 0 and int(showyear) !=0:
        year = int(showyear)
    if year != 0 and '(' not in title:
        showtitle = title + ' ('+str(year)+')' 
    log("getTitleYear, return " + str(year) +', '+ title +', '+ showtitle) 
    return year, title, showtitle
   
def SEinfo(SEtitle):
    season = 0
    episode = 0
    title         = '' 
    titlepattern1 = ' '.join(SEtitle.split(' ')[1:])
    titlepattern2 = re.search('[0-9]+x[0-9]+ (.+)', SEtitle)
    titlepattern3 = re.search('s[0-9]+e[0-9]+ (.+)', SEtitle)
    titlepattern4 = SEtitle
    titlepattern = [titlepattern1,titlepattern2,titlepattern3,titlepattern4]
    for n in range(len(titlepattern)):
        if titlepattern[n]:
            try:
                title = titlepattern[n].group()
            except:
                title = titlepattern[n]
            break
    pattern1 = re.compile(r"""(?:s|season)(?:\s)(?P<s>\d+)(?:e|x|episode|\n)(?:\s)(?P<ep>\d+) # s 01e 02"""                 , re.VERBOSE)
    pattern2 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:e|x|episode|\n)(?:\s)(?P<ep>\d+) # s01e 02"""                        , re.VERBOSE)
    pattern3 = re.compile(r"""(?:s|season)(?:\s)(?P<s>\d+)(?:e|x|episode|\n)(?P<ep>\d+) # s 01e02"""                        , re.VERBOSE)
    pattern4 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:e|x|episode|\n)(?P<ep>\d+) # s01e02"""                               , re.VERBOSE)
    pattern5 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:.*)(?:e|x|episode|\n)(?P<ep>\d+) # s01 random123 e02"""              , re.VERBOSE)
    pattern6 = re.compile(r"""(?:s|season)(?:\s)(?P<s>\d+)(?:.*)(?:e|x|episode|\n)(?:\s)(?P<ep>\d+) # s 01 random123 e 02""", re.VERBOSE)
    pattern7 = re.compile(r"""(?:s|season)(?:\s)(?P<s>\d+)(?:.*)(?:e|x|episode|\n)(?P<ep>\d+) # s 01 random123 e02"""       , re.VERBOSE)
    pattern8 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:.*)(?:e|x|episode|\n)(?:\s)(?P<ep>\d+) # s01 random123 e 02"""       , re.VERBOSE)
    patterns = [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8 ]

    for idx, p in enumerate(patterns):
        m = re.search(p, SEtitle)
        if m:
            season = int( m.group('s'))
            episode = int( m.group('ep')) 
    log("SEinfo, return " + str(season) +', '+ str(episode) +', '+ title) 
    return season, episode, title
    
def utf(string, encoding = 'utf-8'):
    if isinstance(string, basestring):
        if not isinstance(string, unicode):
            string = unicode(string, encoding, 'ignore')
    return string
  
def ascii(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('ascii', 'ignore')
    return string
    
def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('utf-8', 'ignore' )
    return string

def getMeta(nametree, name, desc, url, image, type=False, cnt=0):
    log("getMeta")
    print nametree, name, desc, url, image, type
    season, episode, swtitle = SEinfo(name)
    year, title, showtitle = getTitleYear(name)
    
    if type == 'player':
        infoList = ''
        infoArt  = ''
        if season != 0 and episode != 0:
            name, desc, url, thumb, thumb, fanart, infoList, infoArt, content_type = getEPmeta(nametree, name, desc, url, image, season, episode, swtitle)
        elif 'movie' in nametree.lower():
            name, desc, url, thumb, thumb, fanart, infoList, infoArt, content_type = getMovieMeta(nametree, name, desc, url, image)
        xlistitem = xbmcgui.ListItem(name, path=url)
        xlistitem.setInfo(type="Video", infoLabels=infoList)
        xlistitem.setArt(infoArt)
        xlistitem.setPath(url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xlistitem)
        
    elif type == 'folder':
        #todo regex detect type
        if nametree.lower() in ['shows','tvshow','season','tv']:
            name, desc, url, poster, poster, fanart, infoList, infoArt, content_type = getTVmeta(nametree, name, desc, url, image)
            addDir(name, desc, url, poster, poster, fanart, infoList, infoArt ,content_type) 
        elif 'movie' in nametree.lower():
            name, desc, url, poster, poster, fanart, infoList, infoArt, content_type = getMovieMeta(nametree, name, desc, url, image)
            addDir(name, desc, url, poster, poster, fanart, infoList, infoArt ,content_type)  
        else:
            addDir(name, desc, url, image, image)
    
    elif type == 'video':
        #todo regex detect type
        if season != 0 and episode != 0:
            name, desc, url, poster, poster, fanart, infoList, infoArt, content_type = getEPmeta(nametree, name, desc, url, image, season, episode, swtitle)
            addLink(name, desc, url, poster, poster, fanart, infoList, infoArt, content_type, cnt)
        elif nametree.lower() in ['shows','tvshow','season','tv']:
            name, desc, url, poster, poster, fanart, infoList, infoArt, content_type = getTVmeta(nametree, name, desc, url, image)
            addLink(name, desc, url, poster, poster, fanart, infoList, infoArt, content_type, cnt)
        elif 'movie' in nametree.lower():
            name, desc, url, poster, poster, fanart, infoList, infoArt, content_type = getMovieMeta(nametree, name, desc, url, image)
            addLink(name, desc, url, poster, poster, fanart, infoList, infoArt ,content_type, cnt)  
        else:
            addLink(name, desc, url, image, image,total=cnt)

def getMovieMeta(nametree, name, desc, url, image):
    log("getMovieMeta")
    try:
        content_type              = 'movie'
        thumb = image
        fanart = FANART
        title                 = name
        year, title, showtitle    = getTitleYear(title)
        log("getMovieMeta: " + title)
        
        if Meta_Enabled == False:
            log("getMovieMeta, Meta_Enabled = False")
            raise Exception()
            
        meta                      = metaget.get_meta('movie', title, str(year))       
        desc                      = (meta['plot']                       or desc)
        title                     = (meta['title']                or title)        
        thumb                     = (image                              or (meta['cover_url']))
        poster                    = (meta['cover_url']                  or (image))
        fanart                    = (meta['backdrop_url']               or FANART)
        
        infoList                  = {}
        infoList['mediatype']     = content_type
        infoList['duration']      = (int(meta['duration']               or '0'))*60
        infoList['mpaa']          = (meta['mpaa']                       or 'NR')
        infoList['tagline']       = (meta['tagline']                    or '')
        infoList['title']         = title
        infoList['studio']        = (meta['studio']                     or '')
        infoList['genre']         = (meta['genre']                      or 'Unknown')
        infoList['Plot']          = uni(desc)
        infoList['code']          = (meta['imdb_id']                    or '0')
        infoList['year']          = int(meta['year']                    or (year                or '0'))
        infoList['playcount']     = int((meta['playcount']              or '0'))
        infoList['rating']        = float(meta['rating']                or (meta['rating']      or '0.0'))
        
        infoArt                   = {}
        infoArt['thumb']          = thumb
        infoArt['poster']         = poster
        infoArt['fanart']         = fanart
    except Exception, e:
        infoList = False
        infoArt  = False
    log("getMovieMeta return")
    return name, desc, url, thumb, thumb, fanart, infoList, infoArt, content_type
    
def getTVmeta(nametree, name, desc, url, image):
    try:
        content_type              = 'tvshow'
        thumb = image
        fanart = FANART
        if 'season' in name.lower():
            result                = re.search('/(.*)', nametree)
            title                  = (result.group(1)).split('/')[-1:][0]
        else:
            title                 = name
        year, title, showtitle    = getTitleYear(title)
        log("getTVmeta: " + title)
        
        if Meta_Enabled == False:
            log("getTVmeta, Meta_Enabled = False")
            raise Exception()
            
        meta                      = metaget.get_meta('tvshow', title, str(year))        
        desc                      = (meta['plot']                       or desc)
        title                     = (meta['TVShowTitle']                or title)        
        thumb                     = (image                              or (meta['cover_url']))
        poster                    = (meta['cover_url']                  or (image))
        fanart                    = (meta['backdrop_url']               or FANART)
        
        infoList                  = {}
        infoList['mediatype']     = content_type
        infoList['duration']      = (int(meta['duration']               or '0'))*60
        infoList['mpaa']          = (meta['mpaa']                       or 'NR')
        infoList['tvshowtitle']   = title
        infoList['title']         = title
        infoList['studio']        = (meta['studio']                     or '')
        infoList['genre']         = (meta['genre']                      or 'Unknown')
        infoList['Plot']          = uni(desc)
        infoList['code']          = (meta['tvdb_id']                    or '0')
        infoList['year']          = int(meta['year']                    or (year                or '0'))
        infoList['playcount']     = int((meta['playcount']              or '0'))
        infoList['rating']        = float(meta['rating']                or (meta['rating']      or '0.0'))
        
        infoArt                   = {}
        infoArt['thumb']          = thumb
        infoArt['poster']         = poster
        infoArt['fanart']         = fanart
        infoArt['banner']         = (meta['banner_url']                 or '')
    except Exception, e:
        infoList = False
        infoArt  = False
    log("getTVmeta return")
    return name, desc, url, thumb, thumb, fanart, infoList, infoArt, content_type
     
def getEPmeta(nametree, name, desc, url, image, season, episode, swtitle):
    try:        
        content_type              = 'episode'
        thumb = image
        fanart = FANART
        result                    = re.search('(.*)/Season', nametree)
        title                     = (result.group(1)).split('/')[-1:][0]
        year, title, showtitle    = getTitleYear(title)
        log("getEPmeta: " + title + ' - ' + swtitle)
        
        if Meta_Enabled == False:
            log("Meta_Enabled = False")
            raise Exception()
        
        meta                      = metaget.get_meta('tvshow', title, str(year))
        id                        = meta['imdb_id']
        SEmeta                    = metaget.get_episode_meta(title, id, season, episode)
        
        desc                      = (SEmeta['plot']                       or desc)
        title                     = (SEmeta['TVShowTitle']                or title)
        eptitle                   = (SEmeta['title']                      or swtitle)
        name                      = str("%02d" % (episode,)) + '. ' + eptitle
        
        thumb                     = (image                                or (SEmeta['cover_url'] or meta['cover_url']))
        poster                    = (meta['cover_url']                    or (SEmeta['cover_url'] or image))
        fanart                    = (meta['backdrop_url']                 or FANART)
        
        infoList                  = {}
        infoList['mediatype']     = content_type
        infoList['duration']      = (int(SEmeta['duration']               or '0'))*60
        infoList['mpaa']          = (meta['mpaa']                         or 'NR')
        infoList['tvshowtitle']   = title
        infoList['title']         = eptitle
        infoList['studio']        = (meta['studio']                       or '')
        infoList['genre']         = (meta['genre']                        or 'Unknown')
        infoList['Plot']          = uni(desc)
        infoList['code']          = (meta['tvdb_id']                      or '0')
        infoList['year']          = int(meta['year']                      or (year                or '0'))
        infoList['playcount']     = int((SEmeta['playcount']              or '0'))
        infoList['season']        = season
        infoList['episode']       = episode
        infoList['rating']        = float(SEmeta['rating']                or (meta['rating']      or '0.0'))
        
        infoArt                   = {}
        infoArt['thumb']          = thumb
        infoArt['poster']         = poster
        infoArt['fanart']         = fanart
        infoArt['banner']         = (meta['banner_url']                   or '')
    except Exception, e:
        infoList = False
        infoArt  = False
    log("getEPmeta return")
    return name, desc, url, thumb, thumb, fanart, infoList, infoArt, content_type
  
def parseURL(nametree):
    log("parseURL")
    # Run though the name tree! No restart issues but slower.
    nametreelist = nametree.split('/')
    roothref = None
    for group in get_xml(build_playon_url()).getiterator('group'):
        if group.attrib.get('name') == nametreelist[0]:
            roothref = group.attrib.get('href')

    if roothref != None:
        for i, v in enumerate(nametreelist):
            log("Level:" + str(i) + " Value:" + v)
            if i != 0:
                xml = get_xml(build_playon_url(roothref))
                for group in xml.getiterator('group'):
                    if group.attrib.get('name') == v:
                        roothref = group.attrib.get('href')
                        type = group.attrib.get('type')
                        if type == 'video':
                            mediaNode = get_xml(build_playon_url(group.attrib.get('href'))).find('media')
                            return mediaNode.attrib.get('src'), group.attrib.get('name').encode('ascii', 'ignore'), mediaNode.attrib.get('art'), group.attrib.get('description')

def direct_play(nametree, src, name, image, desc):
    log("direct_play")
    if useUPNP == False:
        url = playonInternalUrl + '/' + src
    else:
        url = playonExternalUrl + '/' + src.split('.')[0].split('/')[0] + '/'        
    getMeta(nametree, name, desc, url, image, 'player')

#    Main Loop
log("Base URL:" + BASE_URL)
log("Addon Handle:" + str(BASE_HANDLE))
log("Arguments")
log(args)

# Pull out the URL arguments for usage. 
mode = get_argument_value('mode')
foldername = get_argument_value('foldername')
nametree = get_argument_value('nametree')
href = get_argument_value('href')
searchable = get_argument_value('searchable')
category = get_argument_value('category')
art = (get_argument_value('image') or ICON)
desc = (get_argument_value('desc') or "N/A")
id = get_argument_value('id')

playonInternalUrl = REAL_SETTINGS.getSetting("playonserver").rstrip('/')
playonExternalUrl = getUPNP().rstrip('/')
log('playonInternalUrl = ' + playonInternalUrl)
log('playonExternalUrl = ' + playonExternalUrl)

if mode is None: #building the main menu... Replicate the XML structure. 
    build_menu_for_mode_none()

elif mode == 'search':
    searchvalue = xbmcgui.Dialog().input("What are you looking for?")
    log("Search Request:" + searchvalue)
    searchurl = build_playon_search_url(id, searchvalue)
    xml = get_xml(searchurl)
    log(xml)
    build_menu_for_search(xml)

elif mode == 'category': # Category has been selected, build a list of items under that category. 
    build_menu_for_mode_category(category)

elif mode == 'folder': # General folder handling. 
    build_menu_for_mode_folder(href, foldername, nametree)

elif mode == 'video' : # Video link from Addon or STRM. Parse and play. 
    """ We are doing a manual play to handle the id change during playon restarts. """
    log("In a video:" + foldername + "::" + href +"::" + nametree)  
    try:
        if playDirect == False:
            raise Exception()
        # Play the href directly. 
        playonUrl = build_playon_url(href)
        name = foldername.encode('ascii', 'ignore')
        mediaXml = get_xml(playonUrl)
        mediaNode = mediaXml.find('media')
        src = mediaNode.attrib.get('src')
        art = ICON
        desc = ''
    except Exception:
        src, name, art, desc = parseURL(nametree)  
    direct_play(nametree, src, name, art, desc)  
    
#todo cache build folder and change from metahandler to artutil