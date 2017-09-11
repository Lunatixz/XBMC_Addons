![screenshot](https://github.com/Lunatixz/XBMC_Addons/raw/master/script.module.uepg/icon.png)
# uEPG developed by Lunatixz

- Please only FORK TO IMPROVE. Nothing kills a project quicker then cloning and abuse of the GNU licence. This project was written to be universally used within Kodi. There is no need to fork for individual plugin use. Please respect the work and effort put into this project. Fork to contribute and/or improve the project only. Thank You = )

- [Support forum](https://forum.kodi.tv/showthread.php?tid=321231)
- [Report Issues](https://github.com/Lunatixz/XBMC_Addons/issues/new)

## About

- uEPG features easy Kodi plugin integration using either listitems or a json dump. 
The EPG interface is fully customizable, includes genre colors, button tags (ex. "HD"), Favorite channel flagging and a programmable context menu.

## Controls:

- Navigate using `Up, Down, Left, Right, PageUp, PageDown`. Use `Select, Enter` or `OK` to play selected content. Toggle between fullscreen video and the EPG using `Back, Previous` or `Close`. Open the context menu using your specified context key. Exit the guide by `stopping` the currently playing video and pressing  `Back, Previous` or `Close` twice.

## Plugin Integration:

### URL parameters:

- `skin_path` - Optional path for custom skin

- `refresh_interval` - How often uEPG should refresh guidedata (in Seconds).

- `refresh_path` - Path uEPG can use to retrieve updated guidedata (required for JSON dump only). All other applications should use originating plugins path. EX. `plugin.video.ustvnow`.
 
- `json` - url quoted, json dump contain guidedata.

- `property` - `xbmcgui.Window(10000)` property name containing url quoted, json dump guidedata.

- `listitem` - plugin path that return guidedata listitem.


#### URL parameter Examples:

- JSON dump

`xbmc.executebuiltin("RunScript(script.module.uepg,json=%s&refresh_path=%s&refresh_interval=%s)"%(urllib.quote_plus(json.dumps(USTVnow().uEPG())),urllib.quote_plus(json.dumps(sys.argv[0]+"?mode=20")),urllib.quote_plus(json.dumps("7200"))))`

- Property

`xbmc.executebuiltin("RunScript(script.module.uepg,property=%s&refresh_path=%s&refresh_interval=%s)"%(urllib.quote_plus(ustvnow_guidedata),urllib.quote_plus(json.dumps(sys.argv[0])),urllib.quote_plus(json.dumps("7200”))))`

- ListItem

`xbmc.executebuiltin("RunScript(script.module.uepg,listitem=%s&refresh_path=%s&refresh_interval=%s)"%(urllib.quote_plus(sys.argv[0]+"?mode=20"),urllib.quote_plus(json.dumps(sys.argv[0])),urllib.quote_plus(json.dumps("7200”))))`

### Guidedata Parameters. 

- [Minimum JSON EX.](https://github.com/Lunatixz/XBMC_Addons/raw/master/script.module.uepg/resources/example.json)

#### Per channel parameters:

- `channelname`,`channelnumber`,`channellogo`

- `Isfavorite` - Optional channel favorite flag

- `guidedata`  - List of individual programme elements.

#### Minimum programme parameters:

- `starttime`, `label`

- `url` or `path` - play path

- `runtime` or `duration` - in seconds.

- `label2` - Optional EPG tag ex. “HD”

- `thumb`  - Optional but should be included.

#### Extended parameters:

- [Kodi ListItem Info DOCS.](https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14)

- [Kodi ListItem Art DOCS.](https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#gad3f9b9befa5f3d2f4683f9957264dbbe)

- [Kodi ListItem StreamDetails DOCS.](https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#gaf0c020ba8bc205d61e786dfec9111cdc)

- Kodi file parameters 
`["title","artist","albumartist","genre","year","rating","album","track","duration","comment","lyrics","musicbrainztrackid","musicbrainzartistid","musicbrainzalbumid","musicbrainzalbumartistid","playcount","fanart","director","trailer","tagline","plot","plotoutline","originaltitle","lastplayed","writer","studio","mpaa","cast","country","imdbnumber","premiered","productioncode","runtime","set","showlink","streamdetails","top250","votes","firstaired","season","episode","showtitle","thumbnail","file","resume","artistid","albumid","tvshowid","setid","watchedepisodes","disc","tag","art","genreid","displayartist","albumartistid","description","theme","mood","style","albumlabel","sorttitle","episodeguide","uniqueid","dateadded","size","lastmodified","mimetype","specialsortseason","specialsortepisode"]`

- Kodi pvr parameters  
`["title","plot","plotoutline","starttime","endtime","runtime","progress","progresspercentage","genre","episodename","episodenum","episodepart","firstaired","hastimer","isactive","parentalrating","wasactive","thumbnail","rating","originaltitle","cast","director","writer","year","imdbnumber","hastimerrule","hasrecording","recording","isseries"]`

- Kodi art parameters  
`["thumb","poster","fanart","banner","landscape","clearart","clearlogo"]`


## Customize Skin:

Details coming soon...

