
import os
import re
import subprocess
import urllib

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs




pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

metapath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/meta')

playerpath = xbmc.translatePath('special://home/addons/' + addonID + '/resources/LaunchPlayer.exe')
tvplayerpath = xbmc.translatePath('special://home/addons/' + addonID + '/resources/LaunchPlayerTV.exe')

username=addon.getSetting("username")
password=addon.getSetting("password")

def index():
	li = xbmcgui.ListItem(translation(30100))
	url = sys.argv[0] + "?mode=listgenres"
	xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	xbmcplugin.endOfDirectory(pluginhandle)

def listGenres():
	cachefile = os.path.join(metapath, 'genres','genres.json')
	if(os.path.exists(cachefile)):
		fh = open(cachefile, 'r')
		content = fh.read()
		fh.close()
	else:
		content = ""

	match = re.compile("'(.*?)':'(.*?)'", re.DOTALL).findall(content)

	for title, genreid in match:
		ctxItms = []

		ctxItms.append((translation(30101), 'Container.Update(' + sys.argv[0] + '?mode=listsubgenres&genre=' + genreid + ')',))

		li = xbmcgui.ListItem(cleanString(title))
		li.addContextMenuItems(ctxItms)
		url = sys.argv[0] + "?mode=listgenrevideos&genre=" + genreid
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	xbmcplugin.endOfDirectory(pluginhandle)

def listGenreVideos(genreid):
	cachefile = os.path.join(metapath, 'genretitles', genreid + '.json')

	if(os.path.exists(cachefile)):
		fh = open(cachefile, 'r')
		content = fh.read()
		fh.close()
	else:
		content = ""

	match = re.compile('{"boxart":".*?","titleId":(.*?),"title":".*?","playerUrl":".*?","trackId":.*?}', re.DOTALL).findall(content)
	#{"boxart":"http://cdn0.nflximg.net/images/0542/11130542.jpg","titleId":70180387,"title":"Homeland","playerUrl":"http://www.netflix.com/WiPlayer?movieid=70180387&trkid=50263619","trackId":50263619}

	for titleid in match:
		listTitle(titleid)

	xbmcplugin.endOfDirectory(pluginhandle)

def listTitle(titleid):
	cachepath = os.path.join(metapath, 'titles', titleid)

	if(os.path.exists(cachepath)):
		cachefile = os.path.join(metapath, 'titles', titleid, 'meta.json')
		thumbfile = os.path.join(metapath, 'titles', titleid, 'coverart.jpg')

		if(os.path.exists(cachefile)):
			fh = open(cachefile, 'r')
			content = fh.read()
			fh.close()
		else:
			content = ""

		if(os.path.exists(os.path.join(metapath, 'titles', titleid, 'seasonddata.json'))):
			match = re.compile('{"isMovie":.*?,"isShow":(.*?),"titleid":(.*?),"title":"(.*?)","mdpLink":".*?","synopsis":"(.*?)","year":(.*?),"profileName":".*?","trackId":(.*?),"showMyList":.*?,"actors":\[.*?\],"inPlayList":.*?,"maturityLabel":"(.*?)","maturityLevel":.*?,"averageRating":(.*?),"predictedRating":.*?,"yourRating":.*?,"numSeasons":(.*?),"creators":\[.*?\],"directors":\[.*?\]}', re.DOTALL).findall(content)




			url = sys.argv[0] + "?mode=listseasons&series=" + titleid

			for isshow, titleid, title, synopsis, year, trackid, certificate, rating, seasons in match:


				li = xbmcgui.ListItem(cleanString(title), iconImage=thumbfile, thumbnailImage=thumbfile)
				li.setInfo(type="video", infoLabels={"title": cleanString(title), "plot": cleanString(synopsis), "year": year, "mpaa": certificate, "rating": rating}) # , "director": director, "genre": genre


				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

		else:
			match = re.compile('{"isMovie":.*?,"isShow":(.*?),"titleid":(.*?),"title":"(.*?)","mdpLink":".*?","synopsis":"(.*?)","year":(.*?),"profileName":".*?","trackId":(.*?),"showMyList":.*?,"runtime":(.*?),"actors":\[.*?\],"inPlayList":.*?,"maturityLabel":"(.*?)","maturityLevel":.*?,"averageRating":(.*?),"predictedRating":.*?,"yourRating":.*?,"creators":\[.*?\],"directors":\[.*?\]}', re.DOTALL).findall(content)


			url = sys.argv[0] + "?mode=playvideo&title=" + titleid

			for isshow, titleid, title, synopsis, year, trackid, runtime, certificate, rating in match:

				li = xbmcgui.ListItem(cleanString(title), iconImage=thumbfile, thumbnailImage=thumbfile)
				li.setInfo(type="video", infoLabels={"title": cleanString(title), "plot": cleanString(synopsis), "duration": runtime, "year": year, "mpaa": certificate, "rating": rating}) # , "director": director, "genre": genre


				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=False)


def listSeasons(seriesid):
	cachefile = os.path.join(metapath,"titles",seriesid, "seasonddata.json")

	if(os.path.exists(cachefile)):
		fh = open(cachefile, 'r')
		content = fh.read()
		fh.close()
	else:
		content = ""

	expr = '{"title":.*?,"year":.*?,"videoId":.*?,"rating":.*?,"creators":.*?,"episodes":\[\[(.*?)\]\],"nextEpisode":{.*?},"numSeasons":(.*?),"synopses":(.*?)}'
	match = re.compile(expr, re.DOTALL).findall(content)

	for episodes, numSeasons, synopses in match:
		count = 0



		expr2 = '"(.*?)"'
		matchSynopses = re.compile(expr2, re.DOTALL).findall(synopses)

		for synopsis in matchSynopses:
			count = count + 1

			li = xbmcgui.ListItem("Season " + str(count))
			li.setInfo(type="video", infoLabels={"title": "Season " + str(count), "plot": cleanString(synopsis) })

			url = sys.argv[0] + "?mode=listepisodes&series=" + seriesid + "&season=" + str(count)

			xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)


	xbmcplugin.endOfDirectory(pluginhandle)

def listEpisodes(seriesid, season):
	cachepath = os.path.join(metapath,"titles",seriesid, "Season " + str(season))
	if os.path.exists(cachepath):
		for ffile in os.listdir(os.path.join(metapath,"titles",seriesid, "Season " + str(season))):
			if ffile.endswith('.json'):

				fh = open(os.path.join(cachepath,ffile), 'r')
				content = fh.read()
				fh.close()

				expr = '{"title":"(.*?)","season":(.*?),"seasonYear":.*?,"episode":(.*?),"synopsis":"(.*?)","seasonId":(.*?),"episodeId":(.*?),"videoId":(.*?),"nonMemberViewable":.*?,"runtime":(.*?),"availableForED":.*?,"availabilityMessage":.*?,"stills":\[.*?\],"bookmarkPosition":(.*?),"lastModified":.*?}'

				match = re.compile(expr, re.DOTALL).findall(content)

				for title, season, episode, synopsis, seasonid, episodeid, videoid, runtime, bookmark in match:
					thumb = os.path.join(cachepath, ffile.replace(".json", ".jpg"))
					
					playcount=0
					if (float(bookmark)/float(runtime))>=0.9:
						playcount=1


					
					li = xbmcgui.ListItem(title, thumbnailImage=thumb)
					li.setInfo(type="video", infoLabels={"title":title, "plot": synopsis, "duration": runtime, "season": season, "episode": episode, "playcount": playcount})

					url = sys.argv[0] + "?mode=playepisode&title=" + episodeid + "&series=" + videoid;

					xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=False)

		xbmcplugin.endOfDirectory(pluginhandle)					

def cleanString(inputstring):
	s=inputstring

	htmlCodes = (
		("'", '&#39;'),
		('"', '&quot;'),
		('>', '&gt;'),
		('<', '&lt;'),
		('&', '&amp;'),
		('"', '\\"')
	)

	for code in htmlCodes:
		s = s.replace(code[1], code[0])
	return s

def listSubGenres(genreid):
	cachefile = os.path.join(metapath, 'genres', genreid + '.json')
	if(os.path.exists(cachefile)):
		fh = open(cachefile, 'r')
		content = fh.read()
		fh.close()

	else:
		content = ""


	match = re.compile("'(.*?)':'(.*?)'", re.DOTALL).findall(content)

	for title, genreid in match:
		li = xbmcgui.ListItem(cleanString(title))
		url = sys.argv[0] + "?mode=listgenrevideos&genre=" + genreid
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(videoid):
	xbmc.Player().stop()
	print '"'+playerpath+'" '+videoid
	subprocess.Popen(playerpath + ' /movieid='+videoid, shell=False)


def playEpisode(videoid, seriesid):
	xbmc.Player().stop()
	print '"'+tvplayerpath+'" '+videoid
	subprocess.Popen(playerpath + ' /movieid=' + videoid + ' /seriesid=' + seriesid + ' /savepath=' + os.path.join(metapath, "titles", seriesid) + ' /un=' + addon.getSetting("username") + ' /pw=' + addon.getSetting("password"), shell=False)



# Utiltity methods
def translation(id):
	return addon.getLocalizedString(id).encode('utf-8')

def paramStringToDict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for pair in paramPairs:
			paramSplits = pair.split('=')
			if len(paramSplits) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict




params = paramStringToDict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode',''))
videoid = urllib.unquote_plus(params.get('title',''))
seriesid = urllib.unquote_plus(params.get('series',''))
season = urllib.unquote_plus(params.get('season',''))
genre = urllib.unquote_plus(params.get('genre',''))

while(username == "" or password == ""):
	d = xbmcgui.Dialog()
	addon.setSetting("username", d.input(translation(30004)))
	addon.setSetting("password", d.input(translation(30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
	username=addon.getSetting("username")
	password=addon.getSetting("password")




if mode == 'listgenres':
	listGenres()
elif mode == 'listsubgenres':
	listSubGenres(genre)
elif mode == 'listgenrevideos':
	listGenreVideos(genre)
elif mode == 'listseasons':
	listSeasons(seriesid)
elif mode == 'listepisodes':
	listEpisodes(seriesid, season)
elif mode == 'playvideo':
	playVideo(videoid)
elif mode == 'playepisode':
	playEpisode(videoid, seriesid)
else:
	index()