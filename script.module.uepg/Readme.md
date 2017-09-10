![screenshot](https://github.com/Lunatixz/XBMC_Addons/raw/master/script.module.uepg/icon.png)
# uEPG developed by Lunatixz

- Warning this project is FORK TO IMPROVE ONLY!. I will not tolerate code cloning, nor abuse of the GNU licence. This project was written to be universally used within Kodi so their is no need to fork for individual plugin use. Please respect the work and effort put into this project. Fork to contribute and/or improve the project.

- [Support forum](https://forum.kodi.tv/showthread.php?tid=321231)
- [Report Issues](https://github.com/Lunatixz/XBMC_Addons/issues/new)

## About

- uEPG features easy Kodi plugin integration using either listitems or a json dump. 
The EPG interface is fully customizable, includes genre colors, button tags (ex. "HD"), Favorite channel flagging and a programmable context menu.

## Controls:

- Navigate using `Up, Down, Left, Right, PageUp, PageDown`. Use `Select, Enter` or `OK` to play selected content. Toggle between fullscreen video and the EPG using `Back, Previous` or `Close`. Open the context menu using your specified context key. Exit the guide by `stopping` the currently playing video and pressing  `Back, Previous` or `Close` twice.

## Plugin Integration:

## JSON Parameters. 

- [Minimum JSON EX.](https://github.com/Lunatixz/XBMC_Addons/raw/master/script.module.uepg/resources/example.json)

### Per channel parameters:

- `channelname`,`channelnumber`,`channellogo`

- `Isfavorite` - Optional channel favorite flag

- `guidedata`  - List of individual programme elements.

### Program element parameters:

- `starttime`, `label`

- `url` or `path` - play path

- `runtime` or `duration` - in seconds.

- `label2` - Optional EPG tag ex. “HD”

### Kodi listitems parameters:

- [ListItem Info DOCS.](https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14)

- [ListItem Art DOCS.](https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#gad3f9b9befa5f3d2f4683f9957264dbbe)

- FILE_PARAMS 
`["title","artist","albumartist","genre","year","rating","album","track","duration","comment","lyrics","musicbrainztrackid","musicbrainzartistid","musicbrainzalbumid","musicbrainzalbumartistid","playcount","fanart","director","trailer","tagline","plot","plotoutline","originaltitle","lastplayed","writer","studio","mpaa","cast","country","imdbnumber","premiered","productioncode","runtime","set","showlink","streamdetails","top250","votes","firstaired","season","episode","showtitle","thumbnail","file","resume","artistid","albumid","tvshowid","setid","watchedepisodes","disc","tag","art","genreid","displayartist","albumartistid","description","theme","mood","style","albumlabel","sorttitle","episodeguide","uniqueid","dateadded","size","lastmodified","mimetype","specialsortseason","specialsortepisode"]`

- PVR_PARAMS  
`["title","plot","plotoutline","starttime","endtime","runtime","progress","progresspercentage","genre","episodename","episodenum","episodepart","firstaired","hastimer","isactive","parentalrating","wasactive","thumbnail","rating","originaltitle","cast","director","writer","year","imdbnumber","hastimerrule","hasrecording","recording","isseries"]`

- ART_PARAMS  
`["thumb","poster","fanart","banner","landscape","clearart","clearlogo"]`





### Customize Skin:


url parmas:
skinPath
refreshIntvl (seconds)
refreshPath
json
property
listitem

required keys:



optional keys
isFavorite
genre - epg color
label2 - epg tag
all pvr/file infolabels, infoart


