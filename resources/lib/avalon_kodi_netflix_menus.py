import cookielib
import collections
import os
import re
import simplejson as json
import sys
import urllib

import xbmc
import xbmcgui
import xbmcplugin

import cookielib

import avalon_kodi_utils as utils
import avalon_kodi_netflix_interop_scrape as scraper
import avalon_kodi_netflix_interop_auth as auth


def index(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath):

	# create plugin list item (Browse Genres)
	li = xbmcgui.ListItem(utils.translation(addon,30100))
	ctxitms = []

	#xbmc.executebuiltin('Container.Update(' + sys.argv[0] + '?mode=updategenretitles&genre=' + genre + '&genrename=' + genrename + ')')
	#ctxitms.append((utils.translation(addon, 30110), 'Container.Update(' + viewpath + '?mode=updategenres)', ))
	ctxitms.append((utils.translation(addon, 30110), 'xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metapath + ')'))

	li.addContextMenuItems(ctxitms)
	url = sys.argv[0] + '?mode=listgenres'
	xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	li = xbmcgui.ListItem(utils.translation(addon,30102))
	ctxitms = []

	ctxitms.append((utils.translation(addon, 30113), 'xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateMyList.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ', ' + metapath + ')', ))

	li.addContextMenuItems(ctxitms)
	url = sys.argv[0] + '?mode=mylist'
	xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	li = xbmcgui.ListItem(utils.translation(addon, 30103))
	url = sys.argv[0] + '?mode=search'
	xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

	#end of directory listing
	xbmcplugin.endOfDirectory(pluginhandle)

def search(addon, addonID, pluginhandle, viewpath, callstackpath, maxrequestsperminute, cookies, search_string, metaroot, cookiepath):
	search_query = search_string.replace(' ', '+')

	response = utils.makeGetRequest('http://www.netflix.com/search/' + search_query, cookies, callstackpath, maxrequestsperminute, 0)

	expr = "<div class=\"lockup\" data-titleid=\"(.*?)\" data-trackid=\"(.*?)\">"

	matches = re.compile(expr, re.DOTALL).findall(response)

	itemcount = 0
	for title, track in matches:
		listTitle(title, viewpath, pluginhandle, metaroot, addon, callstackpath, maxrequestsperminute, cookiepath)
		itemcount += 1

	if itemcount >= 1:
		xbmcplugin.endOfDirectory(pluginhandle)
	else:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok('Netflix', utils.translation(addon, 30204))


def genres(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath, metaroot):

	content = ""

	readcache = False

	if addon.getSetting("keepcache") == "true":
		print "Netflix: Attempting to read genres from cache"
		readcache = True
	else:
		print "Netflix: Local cache is disabled get data online"
		readcache = False

	if readcache:
		# is there a local meta cache?
		if(os.path.exists(metapath)):
			fh = open(metapath, 'r')
			content = fh.read()
			fh.close()
		else:
			readcache = False


	itemcount = 0

	if readcache:
		if content != "":
			genres = json.loads(content, object_pairs_hook = collections.OrderedDict)

			for title in genres:
				itemcount += 1
				li = xbmcgui.ListItem(title)
				ctxitms = []
				ctxitms.append((utils.translation(addon, 30101), 'Container.Update(' + viewpath + '?mode=listsubgenres&genre=' + genres[title] + ')', ))
				#ctxitms.append((utils.translation(addon, 30111), 'Container.Update(' + viewpath + '?mode=updategenretitles&genre=' + genres[title] + '&genrename=' + title + ')', ))



				ctxitms.append((utils.translation(addon,30111), 'xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metaroot + ',' + genres[title] + ',' + title + ')', ))
				li.addContextMenuItems(ctxitms)
				url = viewpath + '?mode=listgenretitles&genre=' + genres[title] + "&genrename=" + urllib.quote_plus(title)
				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

		if itemcount >= 1:
			xbmcplugin.endOfDirectory(pluginhandle)
		else:
			#couldn't find any items - attempt to retrieve from online
			readcache = False

	if not readcache:

		try:
			cookiejar = cookielib.MozillaCookieJar()
			if os.path.exists(cookiepath):
				cookiejar.load(cookiepath)


			response = utils.makeGetRequest('http://www.netflix.com', cookiejar, callstackpath, maxrequestsperminute, 0)
			matches = re.compile("<li><a href=\"(.*?)WiGenre\\?agid=(.*?)\">(.*?)</a></li>", re.DOTALL).findall(response)

			genrefile = os.path.join(metapath, "genres", "genres.json")

			genres = ""
			data = collections.OrderedDict()
			for url, genreid, genrename in matches:
				data[utils.cleanstring(genrename)] = genreid

				itemcount += 1
				li = xbmcgui.ListItem(genrename)
				ctxitms = []
				ctxitms.append((utils.translation(addon, 30101), 'Container.Update(' + viewpath + '?mode=listsubgenres&genre=' + genreid + ')', ))
				#ctxitms.append((utils.translation(addon, 30111), 'Container.Update(' + viewpath + '?mode=updategenretitles&genre=' + genres[title] + '&genrename=' + title + ')', ))



				ctxitms.append((utils.translation(addon,30111), 'xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metaroot + ',' + genreid + ',' + genrename + ')', ))
				li.addContextMenuItems(ctxitms)
				url = viewpath + '?mode=listgenretitles&genre=' + genreid + "&genrename=" + urllib.quote_plus(genrename)
				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

			if addon.getSetting("keepcache") == "true":

				if len(data) > 0:
					#genres = "{" + genres + "}"
					genres = json.dumps(data)
					fh = open(metapath, 'w')
					fh.write(genres)
					fh.close()
		except:
			print "Netflix: Error retrieving Genres"


		if itemcount >= 1:
			xbmcplugin.endOfDirectory(pluginhandle)

	if itemcount < 1:
		li = xbmcgui.ListItem(utils.translation(addon, 30120))
		url = viewpath + '?mode=listgenres'
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)
		xbmcplugin.endOfDirectory(pluginhandle)



def subGenres(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath, genreid):


	content = ""

	readcache = False

	if addon.getSetting("keepcache") == "true":
		print "Netflix: Attempting to read genres from cache"
		readcache = True
	else:
		print "Netflix: Local cache is disabled get data online"
		readcache = False

	if readcache:
		if(os.path.exists(metapath)):
			fh = open(metapath, 'r')
			content = fh.read()
			fh.close()

		itemcount = 0
		if content != "":
			genres = json.loads(content, object_pairs_hook = collections.OrderedDict)

			for title in genres:
				itemcount += 1
				li = xbmcgui.ListItem(title)

				url = viewpath + '?mode=listgenretitles&genre=' + genres[title] + "&genrename="
				xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

		if itemcount >= 1:
			xbmcplugin.endOfDirectory(pluginhandle)
		else:
			#couldn't get data from cache
			readcache = False


	if not readcache:
		#try:
			cookiejar = cookielib.MozillaCookieJar()
			if os.path.exists(cookiepath):
				cookiejar.load(cookiepath)


			response = utils.makeGetRequest('http://www.netflix.com/WiGenre?agid=' + genreid, cookiejar, callstackpath, maxrequestsperminute, 0)
		#	apimatch = re.compile('\"BUILD_IDENTIFIER\":\"(.*?)\".*?\"SHAKTI_API_ROOT\":\"(.*?)\"', re.DOTALL).findall(response)
		#	apiurl = ""
		#	for build, root in apimatch:
		#		apiurl = root + "/" + build
		#	if apiurl != "":
		#		fh = open(os.path.join(metapath, "apiurl"), 'w')
		#		fh.write(apiurl)
		#		fh.close()


			if '<div id="subGenres_menu"' in response:
				response = response[response.index('<div id="subGenres_menu"'):]
				response = response[:response.index('</div>')]

				print response

				matches = re.compile("<a.*?WiGenre\\?agid=(.*?)\\&.*?\">.*?<span>(.*?)</span>.*?</a>", re.DOTALL).findall(response)


				subGenres = ""
				data = collections.OrderedDict()
				for genreid, genrename in matches:
					#if subGenres != "":
					#	subGenres += ","
					#subGenres += "'" + genrename + "':'" + genreid + "'"
					data[utils.cleanstring(genrename)] = genreid
					itemcount += 1
					li = xbmcgui.ListItem(utils.cleanstring(genrename))
					url = viewpath + '?mode=listgenretitles&genre=' + genreid + "&genrename="
					xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

				#if subGenres != "":
				if addon.getSetting("keepcache") == "true":
					if len(data) > 0:
						#subGenres = "Genres = {" + subGenres + "}"
						subGenres = json.dumps(data)
						fh = open(metapath, 'w')
						fh.write(subGenres)
						fh.close()
			else:
				dialog = xbmcgui.Dialog()
				ok = dialog.ok('Netflix', utils.translation(addon, 30122))


				xbmc.executebuiltin('Container.Update(' + viewpath + '?mode=listgenres)')
		#except:
		#	print "Netflix: Error retrieving Sub-Genres"

	if itemcount >= 1:
		xbmcplugin.endOfDirectory(pluginhandle)



	if itemcount < 1:

		li = xbmcgui.ListItem(utils.translation(addon, 30121))
		url = viewpath + '?mode=listsubgenres&genre=' + genreid
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)
		xbmcplugin.endOfDirectory(pluginhandle)

def genreTitles(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath, genreid, metaroot):
	content = ""
	if(os.path.exists(metapath)):
		fh = open(metapath, 'r')
		content = fh.read()
		fh.close()

	itemcount = 0
	if content != "":
		titles = json.loads(content)

		for title in titles:
			listTitle(title["titleId"], viewpath, pluginhandle, metaroot, addon, callstackpath, maxrequestsperminute, cookiepath, title["trackid"])
			itemcount += 1

	if itemcount >= 1:
		xbmcplugin.endOfDirectory(pluginhandle)

def seasons(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath, seriesid, metaroot):
	#metapath = os.path.join(metapath, "titles", seriesid, "seasondata.json")


	cookies = cookielib.MozillaCookieJar()
	if os.path.exists(cookiepath):
		cookies.load(cookiepath)

	auth.login(addon.getSetting("username"), addon.getSetting("password"), cookies, callstackpath, maxrequestsperminute)

	scraper.scrapeSeasonData(cookies, callstackpath, maxrequestsperminute, metaroot, seriesid)

	if os.path.exists(os.path.join(metapath, "seasondata.json")):
		xbmcplugin.setContent(pluginhandle, 'seasons')

		fh = open(os.path.join(metapath, "seasondata.json"), 'r')
		content = fh.read()
		fh.close()

		seasondata = json.loads(content)

		for season in seasondata["episodes"]:
			syno = ""
			title = "Season " + str(season[0]["season"])
			url = viewpath + "?mode=listepisodes&series=" + seriesid + "&season=" + str(season[0]["season"]) + "&seasonid=" + str(season[0]["seasonId"])
			if os.path.exists(os.path.join(metapath, "Season " + str(season[0]["season"]), "synopsis")):
				fh = open(os.path.join(metapath, "Season " + str(season[0]["season"]), "synopsis"), 'r')
				syno = fh.read()
				fh.close
			year = seasondata["year"]
			watched = 0
			episodecount = 0
			for episode in season:
				#episodeexpr = '{"title":".*?","season":(.*?),"seasonYear":.*?,"episode":.*?,"synopsis":".*?","seasonId":.*?,"episodeId":.*?,"videoId":.*?,"nonMemberViewable":.*?,"runtime":(.*?),"availableForED":.*?,"availabilityMessage":.*?,"stills":\[.*?\],"bookmarkPosition":(.*?),"lastModified":".*?"}'
				episodecount += 1
				if episode["bookmarkPosition"]:
					if float(episode["bookmarkPosition"])/float(episode["runtime"]) >= 0.9:
						watched += 1
				year = episode["seasonYear"]

			li = xbmcgui.ListItem(title)

			if (episodecount - watched) == 0:
				playcount = 1
			elif watched == 0:
				playcount = 0
			else:
				li.setProperty('TotalTime', '100')
				li.setProperty('ResumeTime', '50')

			li.setProperty('TotalEpisodes', str(episodecount))
			li.setProperty('WatchedEpisodes', str(watched))
			li.setProperty('UnWatchedEpisodes', str(episodecount-watched))


			info = {'plot': syno, 'year': int(year)}

			li.setInfo('video', infoLabels=info)

			xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=True)

		xbmcplugin.endOfDirectory(pluginhandle)


def episodes(addon, addonid, pluginhandle, metapath, viewpath, callstackpath, maxreq, cookiepath, seriesid, seasonid, metaroot):
	if os.path.exists(os.path.join(metapath, "seasondata.json")):
		xbmcplugin.setContent(pluginhandle, "episodes")

		fh = open(os.path.join(metapath, "seasondata.json"), 'r')
		content = fh.read()
		fh.close()

		seasondata = json.loads(content)

		fh = open(os.path.join(metapath, "meta.json"), 'r')
		content = fh.read()
		fh.close()

		seriesdata = json.loads(content)

		for season in seasondata["episodes"]:
			for episode in season:
				if str(episode["seasonId"]) == seasonid:
					url = viewpath + "?mode=playepisode&title=" + str(episode["episodeId"]) + "&series=" + str(episode["videoId"])
					li = xbmcgui.ListItem(str(episode["episode"]).zfill(2) + ". " + episode["title"])
					li.setProperty('TotalTime', str(episode["runtime"]))
					playcount = 0
					#if(episode["runtime"] != episode["bookmarkPosition"]):
					#	li.setProperty('ResumeTime', str(episode["bookmarkPosition"]))
					#elif(episode["bookmarkPosition"] != 0):
					#	playcount =
					if float(episode["bookmarkPosition"])/float(episode["runtime"]) >= 0.9:
						playcount = 1
					elif(episode["runtime"] != episode["bookmarkPosition"]):
						li.setProperty('ResumeTime', str(episode["bookmarkPosition"]))

					synopsis = episode["synopsis"]
					info = {'plot': synopsis, 'season': episode["season"], 'episode': episode["episode"], 'tvshowtitle': seriesdata["title"], 'title': episode["title"], 'playcount': playcount}

					li.setInfo('video', infoLabels = info)

					if(os.path.exists(os.path.join(metapath, "Season " + str(episode["season"]), "S" + str(episode["season"]).zfill(2) + "E" + str(episode["episode"]).zfill(2) + ".jpg"))):
						li.setArt({'thumb': os.path.join(metapath, "Season " + str(episode["season"]), "S" + str(episode["season"]).zfill(2) + "E" + str(episode["episode"]).zfill(2) + ".jpg")})

					xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=False)

		xbmcplugin.endOfDirectory(pluginhandle)

def myList(viewpath, pluginhandle, metaroot, addon, callstackpath, maxrequests, cookiepath):
	if os.path.isdir(os.path.join(metaroot, "MyList")):
		for ffile in os.listdir(os.path.join(metaroot,"MyList")):
			#try:
			listTitle(ffile, viewpath, pluginhandle, metaroot, addon, callstackpath, maxrequests, cookiepath, '')
			#except:
			#	pass

		xbmcplugin.endOfDirectory(pluginhandle)

def listTitle(titleid, viewpath, pluginhandle, metaroot, addon, callstackpath, maxreq, cookiepath, trackid):
	metapath = os.path.join(metaroot, "Titles", titleid)
	UpdateTitle = False
	addonID = addon.getAddonInfo('id')
	if os.path.exists(metapath):
		datafile = os.path.join(metapath, "meta.json")
		thumbfile = os.path.join(metapath, "coverart.jpg")

		if os.path.exists(datafile):
			fh = open(datafile, 'r')
			content = fh.read()
			fh.close()
		else:
			print "Netflix: Title metadata not found - " + str(titleid)
			content = ""
			UpdateTitle = True


		data = json.loads(content)

		li = xbmcgui.ListItem(data["title"], iconImage = thumbfile, thumbnailImage = thumbfile)
		ctxItems = []


		ctxItems.append((utils.translation(addon, 30112), 'xbmc.runscript(special://home/addons/' + str(addonID) + '/resources/scripts/UpdateTitle.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxreq) + ', ' + addonID + ', ' + metaroot + ', ' + titleid + ', ' + str(data["trackId"]) + ')', ))
		#ctxItems.append((utils.translation(addon, 30112), 'Container.Update(' + viewpath + '?mode=updatetitle&title=' + titleid + '&track=' + str(data["trackId"]) + ')', ))

		if os.path.exists(os.path.join(metaroot, "MyList", titleid)):
			ctxItems.append((utils.translation(addon, 30115), 'xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/RemoveFromMyList.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxreq) + ', ' + addonID + ', ' + metaroot + ', ' + titleid + ', ' + str(data["trackId"]) + ')', ))
			#ctxItems.append((utils.translation(addon, 30115), 'Container.Update(' + viewpath + '?mode=removefrommylist&title=' + titleid + '&track=' + str(data["trackId"]) +')', ))
		else:
			ctxItems.append((utils.translation(addon, 30114), 'xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/AddToMyList.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxreq) + ', ' + addonID + ', ' + metaroot + ', ' + titleid + ', ' + str(data["trackId"]) + ')', ))
			#ctxItems.append((utils.translation(addon, 30114), 'Container.Update(' + viewpath + '?mode=addtomylist&title=' + titleid + '&track=' + str(data["trackId"]) +')', ))

		li.addContextMenuItems(ctxItems)

		genres = ""



		if os.path.isdir(os.path.join(metapath, "Genres")):
			for ffile in os.listdir(os.path.join(metapath,"Genres")):
				if genres != "":
					genres += " / "
				genres += ffile

		cast = []
		for castmember in data["actors"]:
			cast += [castmember["name"]]

		if data["isShow"]:
			# TV Series
			xbmcplugin.setContent(pluginhandle, 'tvshows')
			url = viewpath + "?mode=listseasons&series=" + titleid
			isfolder = True
			playcount = 0
			if(os.path.exists(os.path.join(metapath, "seasondata.json"))):
				fh = open(os.path.join(metapath, "seasondata.json"))
				seasoncontent = fh.read()
				fh.close()

				seasondata = json.loads(seasoncontent)
				episodecount = 0
				watched = 0
				for season in seasondata["episodes"]:
					for episode in season:
						#episodeexpr = '{"title":".*?","season":(.*?),"seasonYear":.*?,"episode":.*?,"synopsis":".*?","seasonId":.*?,"episodeId":.*?,"videoId":.*?,"nonMemberViewable":.*?,"runtime":(.*?),"availableForED":.*?,"availabilityMessage":.*?,"stills":\[.*?\],"bookmarkPosition":(.*?),"lastModified":".*?"}'
						episodecount += 1
						try:
							if float(episode["bookmarkPosition"])/float(episode["runtime"]) >= 0.9:
								watched += 1
						except:
							pass

				if (episodecount - watched) == 0:
					playcount = 1
				elif watched == 0:
					playcount = 0
				else:
					li.setProperty('TotalTime', '100')
					li.setProperty('ResumeTime', '50')

			else:
				UpdateTitle = True

			info = {'plot': data['synopsis'], 'year': int(data["year"]), 'mpaa': data["maturityLabel"], "cast": cast, "genre": genres, "playcount": playcount}

		else:
			# Movie/TV Movie or documentary
			xbmcplugin.setContent(pluginhandle, 'movies')
			url = viewpath + "?mode=playvideo&title=" + titleid
			isfolder = False

			info = {'plot': data['synopsis'], 'year': int(data["year"]), 'mpaa': data["maturityLabel"], "cast": cast, "genre": genres}


		li.setInfo('video', infoLabels=info)


#        - genre : string (Comedy)
#        - year : integer (2009)
#        - episode : integer (4)
#        - season : integer (1)
#        - top250 : integer (192)
#        - tracknumber : integer (3)
#        - rating : float (6.4) - range is 0..10
#        - watched : depreciated - use playcount instead
#        - playcount : integer (2) - number of times this item has been played
#        - overlay : integer (2) - range is 0..8. See GUIListItem.h for values
#        - cast : list (Michal C. Hall)
#        - castandrole : list (Michael C. Hall|Dexter)
#        - director : string (Dagur Kari)
#        - mpaa : string (PG-13)
#        - plot : string (Long Description)
#        - plotoutline : string (Short Description)
#        - title : string (Big Fan)
#        - originaltitle : string (Big Fan)
#        - sorttitle : string (Big Fan)
#        - duration : string (3:18)
#        - studio : string (Warner Bros.)
#        - tagline : string (An awesome movie) - short description of movie
#        - writer : string (Robert D. Siegel)
#        - tvshowtitle : string (Heroes)
#        - premiered : string (2005-03-04)
#        - status : string (Continuing) - status of a TVshow
#        - code : string (tt0110293) - IMDb code
#        - aired : string (2008-12-07)
#        - credits : string (Andy Kaufman) - writing credits
#        - lastplayed : string (Y-m-d h:m:s = 2009-04-05 23:16:04)
#        - album : string (The Joshua Tree)
#        - artist : list (['U2'])
#        - votes : string (12345 votes)
#        - trailer : string (/home/user/trailer.avi)
#        - dateadded : string (Y-m-d h:m:s = 2009-04-05 23:16:04)

		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=isfolder)

	else:
		print "Netflix: Title not found - " + str(titleid)
		UpdateTitle = True

	if UpdateTitle:
		xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + str(addonID) + '/resources/scripts/UpdateTitle.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxreq) + ', ' + addonID + ', ' + metaroot + ', ' + titleid + ', ' + str(trackid) + ')')
