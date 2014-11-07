
import os
import re
import string
import sys
import subprocess
import time
import urllib

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs


sys.path.append(os.path.join(xbmc.translatePath('special://home/addons/plugin.video.avalon.netflix/'), "resources", "lib")) 

import netflix_utils as netflixutils # utility methods (incl. request metering)

pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

metapath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/meta')

playerpath = xbmc.translatePath('special://home/addons/' + addonID + '/resources/LaunchPlayer.exe')
tvplayerpath = xbmc.translatePath('special://home/addons/' + addonID + '/resources/LaunchPlayerTV.exe')

username=addon.getSetting("username")
password=addon.getSetting("password")

def index():

	#create plugin list item (Browse Genres)
	li = xbmcgui.ListItem(translation(30100))

	# add context menu to refresh genre list
	ctxItms = []
	ctxItms.append((translation(30111), 'xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ')')) # 30111 = Refresh Genres
	li.addContextMenuItems(ctxItms)

	url = sys.argv[0] + "?mode=listgenres"
	xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)
	

	# create plugin list item (MyList)
	if os.path.isdir(os.path.join(metapath, "MyList")):
		li = xbmcgui.ListItem(translation(30102))

		url = sys.argv[0] + "?mode=mylist"
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	# end of directory listing
	xbmcplugin.endOfDirectory(pluginhandle)

def myList():
	if os.path.isdir(os.path.join(metapath, "MyList")):
		for ffile in os.listdir(os.path.join(metapath,"MyList")):
			listTitle(ffile)
			
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
		ctxItms.append((translation(30111), 'xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + genreid + ', ' + addon.getSetting("cacheage") + ')'))

		li = xbmcgui.ListItem(netflixutils.cleanurlstring(title))
		li.addContextMenuItems(ctxItms)
		url = sys.argv[0] + "?mode=listgenrevideos&genre=" + genreid
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	xbmcplugin.endOfDirectory(pluginhandle)

def listGenreVideos(genreid):

	#xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + genreid + ')')

	cachefile = os.path.join(metapath, 'genretitles', genreid + '.json')


	UpdateGenreTitles = False
	if os.path.exists(cachefile):
		age = xbmcvfs.Stat(cachefile).st_mtime()
		now = time.time()

		oneday = 24 * 60 * 60

		if (now-age) > (oneday*int(addon.getSetting("cacheage"))):
			UpdateGenreTitles = True
	else:
		UpdateGenreTitles = True

	if(UpdateGenreTitles):
		if(addon.getSetting("promptforcache")):
			dialog = xbmcgui.Dialog()
			ret = dialog.yesno('Netflix', translation(30201))
			if(ret):
				xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + genreid + ', ' + addon.getSetting("cacheage") + ')')
		else:
			xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + genreid + ', ' + addon.getSetting("cacheage") + ')')



	if(os.path.exists(cachefile)):
		fh = open(cachefile, 'r')
		content = fh.read()
		fh.close()
	else:
		content = ""

	

	match = re.compile('{"boxart":".*?","titleId":(.*?),"title":".*?","playerUrl":".*?","trackId":.*?}', re.DOTALL).findall(content)
	#{"boxart":"http://cdn0.nflximg.net/images/0542/11130542.jpg","titleId":70180387,"title":"Homeland","playerUrl":"http://www.netflix.com/WiPlayer?movieid=70180387&trkid=50263619","trackId":50263619}

	for titleid in match:
		#print titleid
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


			xbmcplugin.setContent(pluginhandle, 'tvshows')





			url = sys.argv[0] + "?mode=listseasons&series=" + titleid

			for isshow, titleid, title, synopsis, year, trackid, certificate, rating, seasons in match:

				tmpRating = float(rating)*2;


				rating=str(tmpRating)


				li = xbmcgui.ListItem(netflixutils.cleanurlstring(title), iconImage=thumbfile, thumbnailImage=thumbfile)

				# add context menu to refresh genre list
				ctxItms = []
				ctxItms.append((translation(30112), 'xbmc.runscript(special://home/addons/' + addonID + '/UpdateTitle.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + titleid + ', ' + trackid  +')')) # 30112 = Refresh Title
				li.addContextMenuItems(ctxItms)

				fh = open(os.path.join(metapath, 'titles', titleid, 'seasonddata.json'), 'r')
				episodecontent = fh.read()
				fh.close()

				episodeexpr = '{"title":".*?","season":(.*?),"seasonYear":.*?,"episode":.*?,"synopsis":".*?","seasonId":.*?,"episodeId":.*?,"videoId":.*?,"nonMemberViewable":.*?,"runtime":(.*?),"availableForED":.*?,"availabilityMessage":.*?,"stills":\[.*?\],"bookmarkPosition":(.*?),"lastModified":".*?"}'
				matchepisodes = re.compile(episodeexpr, re.DOTALL).findall(episodecontent)

				watched = 0
				episodecount = 0
				for season, runtime, bookmark in matchepisodes:
					episodecount = episodecount + 1;
					playcount=0
					if (float(bookmark)/float(runtime))>=0.9:
						playcount=1
					watched = watched + playcount

				playcount = 0
				if (episodecount - watched) == 0:
					playcount = 1
				elif watched == 0:
					playcount = 0
				else:
					li.setProperty('TotalTime', '100')
					li.setProperty('ResumeTime', '50')


				li.setInfo(type="video", infoLabels={"title": netflixutils.cleanurlstring(title), "plot": netflixutils.cleanurlstring(synopsis), "year": year, "mpaa": certificate, "rating": rating, "playcount": playcount}) # , "director": director, "genre": genre




				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

		else:
			xbmcplugin.setContent(pluginhandle, 'movies')

			match = re.compile('{"isMovie":.*?,"isShow":(.*?),"titleid":(.*?),"title":"(.*?)","mdpLink":".*?","synopsis":"(.*?)","year":(.*?),"profileName":".*?","trackId":(.*?),"showMyList":.*?,"runtime":(.*?),"actors":\[.*?\],"inPlayList":.*?,"maturityLabel":"(.*?)","maturityLevel":.*?,"averageRating":(.*?),"predictedRating":.*?,"yourRating":.*?,"creators":\[.*?\],"directors":\[.*?\]}', re.DOTALL).findall(content)


			url = sys.argv[0] + "?mode=playvideo&title=" + titleid

			for isshow, titleid, title, synopsis, year, trackid, runtime, certificate, rating in match:

				tmpRating = float(rating)*2;


				rating=str(tmpRating)

				li = xbmcgui.ListItem(netflixutils.cleanurlstring(title), iconImage=thumbfile, thumbnailImage=thumbfile)

				ctxItms = []
				ctxItms.append((translation(30112), 'xbmc.runscript(special://home/addons/' + addonID + '/UpdateTitle.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + titleid + ', ' + trackid + ')')) # 30112 = Refresh Title
				li.addContextMenuItems(ctxItms)

				li.setInfo(type="video", infoLabels={"title": netflixutils.cleanurlstring(title), "plot": netflixutils.cleanurlstring(synopsis), "duration": runtime, "year": year, "mpaa": certificate, "rating": rating}) # , "director": director, "genre": genre


				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=False)


def listSeasons(seriesid):
	cachefile = os.path.join(metapath,"titles",seriesid, "seasonddata.json")

	xbmcplugin.setContent(pluginhandle, 'seasons')

	if(os.path.exists(cachefile)):
		fh = open(cachefile, 'r')
		content = fh.read()
		fh.close()
	else:
		content = ""

	expr = '{"title":.*?,"year":.*?,"videoId":.*?,"rating":.*?,"creators":.*?,"episodes":\[\[(.*?)\]\],"nextEpisode":{.*?},"numSeasons":(.*?),"synopses":(.*?)}'
	match = re.compile(expr, re.DOTALL).findall(content)

	for episodes, numSeasons, synopses in match:







		episodeExpr = '{"title":".*?","season":(.*?),"seasonYear":.*?,"episode":.*?,"synopsis":".*?","seasonId":.*?,"episodeId":.*?,"videoId":.*?,"nonMemberViewable":.*?,"runtime":(.*?),"availableForED":.*?,"availabilityMessage":.*?,"stills":\[.*?\],"bookmarkPosition":(.*?),"lastModified":".*?"}'
		matchEpisodes = re.compile(episodeExpr, re.DOTALL).findall(episodes)

		watched = {}
		episodecount = {}
		for season, runtime, bookmark in matchEpisodes:
			episodecount[season] = episodecount.get(season, 0) + 1;
			playcount=0
			if (float(bookmark)/float(runtime))>=0.9:
				playcount=1
			watched[season] = watched.get(season, 0) + playcount



		expr2 = '"(.*?)"'
		matchSynopses = re.compile(expr2, re.DOTALL).findall(synopses.replace("\\\"", "__X__"))


		count = 0
		for synopsis in matchSynopses:
			count = count + 1

			li = xbmcgui.ListItem("Season " + str(count))

			playcount = 0
			if (episodecount[str(count)] - watched[str(count)]) == 0:
				playcount = 1
			elif watched[str(count)] == 0:
				playcount = 0
			else:
				li.setProperty('TotalTime', '100')
				li.setProperty('ResumeTime', '50')



			li.setInfo(type="video", infoLabels={"title": "Season " + str(count), "plot": netflixutils.cleanurlstring(synopsis), "playcount": playcount })

			url = sys.argv[0] + "?mode=listepisodes&series=" + seriesid + "&season=" + str(count)

			li.setProperty('TotalEpisodes', str(episodecount[str(count)]))
			li.setProperty('WatchedEpisodes', str(watched[str(count)]))
			li.setProperty('UnWatchedEpisodes', str(episodecount[str(count)] - watched[str(count)]))

			xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)



	xbmcplugin.endOfDirectory(pluginhandle)

def listEpisodes(seriesid, season):

	xbmcplugin.setContent(pluginhandle, 'episodes')
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

					
					li = xbmcgui.ListItem(str(episode).zfill(2) + ". " + cleanString(title), thumbnailImage=thumb)
					# not a lot of point unless we can force a title to run from the beginning!!!
					#li.setProperty('TotalTime', runtime)
					#li.setProperty('ResumeTime', bookmark)

					
					li.setInfo(type="video", infoLabels={"title":str(episode).zfill(2) + ". " + cleanString(title), "plot": synopsis, "duration": runtime, "season": season, "episode": episode, "playcount": playcount})

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
		('"', '\\"'), 

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
		li = xbmcgui.ListItem(netflixutils.cleanurlstring(title))
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



#xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ')')

# Do we need to download genre data at startup?
UpdateGenres = False
if os.path.exists(os.path.join(metapath, "Genres", "genres.json")):
	age = xbmcvfs.Stat(os.path.join(metapath, "Genres", "genres.json")).st_mtime()
	now = time.time()

	oneday = 24 * 60 * 60

	if (now-age) > (oneday*int(addon.getSetting("cacheage"))):
		UpdateGenres = True
else:
	UpdateGenres = True

if(UpdateGenres):
	if(addon.getSetting("promptforcache")):
		dialog = xbmcgui.Dialog()
		ret = dialog.yesno('Netflix', translation(30200))
		if(ret):
			xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ')')
	else:
		xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ')')


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
elif mode == 'mylist':
	myList()
else:
	index()