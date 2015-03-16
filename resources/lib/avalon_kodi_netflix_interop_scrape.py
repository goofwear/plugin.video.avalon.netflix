import collections
import os
import re
import simplejson as json
import sys
import time

import xbmc
import xbmcaddon
import xbmcvfs

import avalon_kodi_netflix_interop_auth as auth
import avalon_kodi_utils as utils

def scrapeGenres(cookies, callstackpath, maxrequestsperminute, metapath, cacheage):

	if not os.path.isdir(os.path.join(metapath, "active")):
		os.mkdir(os.path.join(metapath, "active"))

	if not os.path.exists(os.path.join(metapath, "active", "scrape_genres")):

		fh = open(os.path.join(metapath, "active", "scrape_genres"), 'w')
		fh.write("currently scraping Genres")
		fh.close()

		response = utils.makeGetRequest('http://www.netflix.com', cookies, callstackpath, maxrequestsperminute)
		matches = re.compile("<li><a href=\"(.*?)WiGenre\\?agid=(.*?)\">(.*?)</a></li>", re.DOTALL).findall(response)

		genrefile = os.path.join(metapath, "genres", "genres.json")

		genres = ""
		data = collections.OrderedDict()
		for url, genreid, genrename in matches:
			print "Netflix: DEBUG: " + url
			url = "http://www.netflix.com/WiGenre?agid=" + genreid

			data[utils.cleanstring(genrename)] = genreid


			UpdateSubGenres = False
			if os.path.exists(os.path.join(metapath, "Genres", genreid + ".json")):
				oneday = 24 * 60 * 60
				if utils.fileIsOlderThan(os.path.join(metapath, "Genres", genreid + ".json"), (oneday * int(cacheage))):
					UpdateSubGenres = True
			else:
				UpdateSubGenres = True

			if(UpdateSubGenres):
				scrapeSubGenre(cookies, callstackpath, maxrequestsperminute, metapath, url)


		#if genres != "":
		if len(data) > 0:
			#genres = "{" + genres + "}"
			genres = json.dumps(data)
			fh = open(genrefile, 'w')
			fh.write(genres)
			fh.close()

		os.remove(os.path.join(metapath, "active", "scrape_genres"))


def scrapeSubGenre(cookies, callstackpath, maxrequestsperminute, metapath, url):

	response = utils.makeGetRequest(url, cookies, callstackpath, maxrequestsperminute)
	apimatch = re.compile('\"BUILD_IDENTIFIER\":\"(.*?)\".*?\"SHAKTI_API_ROOT\":\"(.*?)\"', re.DOTALL).findall(response)
	apiurl = ""
	for build, root in apimatch:
		apiurl = root + "/" + build
	if apiurl != "":
		fh = open(os.path.join(metapath, "apiurl"), 'w')
		fh.write(apiurl)
		fh.close()


	if '<div id="subGenres"' in response:
		response = response[response.index('<div id="subGenres"'):]

		matches = re.compile("<a.*?WiGenre\\?agid=(.*?)\\&.*?\">.*?<span>(.*?)</span>.*?</a>", re.DOTALL).findall(response)


		subGenres = ""
		data = collections.OrderedDict()
		for genreid, genrename in matches:
			#if subGenres != "":
			#	subGenres += ","
			#subGenres += "'" + genrename + "':'" + genreid + "'"
			data[utils.cleanstring(genrename)] = genreid

		#if subGenres != "":
		if len(data) > 0:
			#subGenres = "Genres = {" + subGenres + "}"
			subGenres = json.dumps(data)
			fh = open(os.path.join(metapath, "genres", genreid + ".json"), 'w')
			fh.write(subGenres)
			fh.close()


def scrapeGenreTitles(cookies, callstackpath, maxrequestsperminute, metapath, genreid, cacheage, genrename):

	if(os.path.exists(os.path.join(metapath, "apiurl"))):
		fh = open(os.path.join(metapath, "apiurl"), 'r')
		apiurl = fh.read()
		fh.close()
		print "Netflix: Scraping titles for " + genrename
		content = ""

		start = 0
		size = 100
		titles = ""

		if not os.path.isdir(os.path.join(metapath, "GenreTitles")):
			os.mkdir(os.path.join(metapath, "GenreTitles"))
		if not os.path.isdir(os.path.join(metapath, "Titles")):
			os.mkdir(os.path.join(metapath, "Titles"))

		titles = []

		while not content.startswith('{"catalogItems":[]}'):
			requesturl = apiurl + "/wigenre?genreId=" + genreid + "&full=false&from=" + str(start) + "&to=" + str(start + size)
			# increment for next call
			start = start + size + 1

			content = utils.makeGetRequest(requesturl, cookies, callstackpath, maxrequestsperminute)

			match = re.compile("{\"boxart\":\"(.*?)\",\"titleId\":(.*?),\"title\":\"(.*?)\",\"playerUrl\":\"(.*?)\",\"trackId\":(.*?)}", re.DOTALL).findall(content)

			for boxart, titleid, title, playerurl, trackid in match:
				titledata = collections.OrderedDict()
				titledata["boxart"] = boxart
				titledata["titleId"] = titleid
				titledata["title"] = title
				titledata["playerurl"] = playerurl
				titledata["trackid"] = trackid

				if not os.path.isdir(os.path.join(metapath, "GenreTitles", genreid)):
					os.mkdir(os.path.join(metapath, "GenreTitles", genreid))

				if not os.path.isdir(os.path.join(metapath, "Titles", titleid)):
					os.mkdir(os.path.join(metapath, "Titles", titleid))

				coverart = utils.makeGetRequest(boxart, cookies, callstackpath, maxrequestsperminute)

				fh = open(os.path.join(metapath, "Titles", titleid, "folder.jpg"), 'wb')
				fh.write(coverart)
				fh.close()
				fh = open(os.path.join(metapath, "Titles", titleid, "coverart.jpg"), 'wb')
				fh.write(coverart)
				fh.close()

				# write genre tags
				if not os.path.isdir(os.path.join(metapath, "Titles", titleid, "Genres")):
					os.mkdir(os.path.join(metapath, "Titles", titleid, "Genres"))
				if genrename != "":
					fh = open(os.path.join(metapath, "Titles", titleid, "Genres", genrename), 'w')
					fh.write(genrename)
					fh.close()

				fh = open(os.path.join(metapath, "GenreTitles", genreid, titleid + ".json"), 'w')
				fh.write(json.dumps(titledata))
				fh.close()

				UpdateTitle = False
				titlefile = os.path.join(metapath, "Titles", titleid, "meta.json")
				if os.path.exists(titlefile):
					oneday = 24 * 60 * 60
					if utils.fileIsOlderThan(titlefile, (oneday * int(cacheage))):
						UpdateTitle = True
				else:
					UpdateTitle = True

				if UpdateTitle:
					scrapeTitle(cookies, callstackpath, maxrequestsperminute, metapath, titleid, trackid)

				titles = titles + [titledata]



		fh = open(os.path.join(metapath, "genreTitles", genreid + ".json"), 'w')
		fh.write(json.dumps(titles))
		fh.close()

def scrapeSeasonData(cookies, callstackpath, maxrequestsperminute, metapath, titleid):
	seasondataurl = "http://api-global.netflix.com/desktop/odp/episodes?forceEpisodes=true&routing=redirect&video=" + titleid
	seasondata = utils.makeGetRequest(seasondataurl, cookies, callstackpath, maxrequestsperminute)

	fh = open(os.path.join(metapath, "Titles", titleid, "seasondata.json"),'w')
	fh.write(seasondata)
	fh.close()



	data = json.loads(seasondata)
	seasoncounter = 0
	for season in data["episodes"]:

		#http://www.netflix.com/WiMovie/70136119?trkid=50263680&actionMethod=seasonDetails&seasonId=70061401&seasonKind=ELECTRONIC



		for episode in season:
			if not os.path.exists(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]))):
				os.mkdir(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"])))
			fname = "S" + str(episode["season"]).zfill(2) + "E" + str(episode["episode"]).zfill(2)
			fh = open(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]), fname + ".json"), 'w')
			fh.write(json.dumps(episode))
			fh.close()

			stillswidth = 0
			stillspath = ""
			if not os.path.exists(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]), fname + ".jpg")):
				if "stills" in episode:
					for still in episode["stills"]:
						width = still["width"]
						try:
							if(int(width) > stillswidth):
								stillswidth = int(width)
								stillspath = still["url"]
						except:
							pass

					if stillspath != "":
						try:
							stillimage = utils.makeGetRequest(stillspath, cookies, callstackpath, maxrequestsperminute)
							fh = open(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]), fname + ".jpg"), 'wb')
							fh.write(stillimage)
							fh.close()
						except:
							pass

						#http://www.netflix.com/WiMovie/70297439?actionMethod=seasonDetails&seasonId=70296034&seasonKind=ELECTRONIC
		if not os.path.exists(os.path.join(metapath, "Titles", titleid, "Season " + str(season[0]["season"]), "synopsis")):
			seasoninfourl = "http://www.netflix.com/WiMovie/" + titleid + "?&actionMethod=seasonDetails&seasonId=" + str(season[0]["seasonId"]) + "&seasonKind=ELECTRONIC"
			seasoninforesponse = utils.makeGetRequest(seasoninfourl, cookies, callstackpath, maxrequestsperminute)

			seasoninfo = json.loads(seasoninforesponse)

			seasoninfosynopsismatch = re.compile('<\/h2><p class=\"synopsis\".*?>(.*?)<\/p>', re.DOTALL).findall(seasoninfo["html"])
			synopsis = ""
			for syno in seasoninfosynopsismatch:
				synopsis += syno

			fh = open(os.path.join(metapath, "Titles", titleid, "Season " + str(season[0]["season"]), "synopsis"), 'w')
			fh.write(json.dumps(synopsis))
			fh.close()

		

def scrapeTitle(cookies, callstackpath, maxrequestsperminute, metapath, titleid, trackid):

	if not os.path.isdir(os.path.join(metapath, "active")):
		os.mkdir(os.path.join(metapath, "active"))

	if not os.path.exists(os.path.join(metapath, "active", "scrape_title_" + titleid)):

		fh = open(os.path.join(metapath, "active", "scrape_title_" + titleid), 'w')
		fh.write("currently scraping MyList")
		fh.close()

		if(os.path.exists(os.path.join(metapath, "apiurl"))):
			fh = open(os.path.join(metapath, "apiurl"), 'r')
			apiurl = fh.read()
			fh.close()

			titleurl = apiurl + "/bob?titleid=" + titleid + "&trackid=" + trackid

			content = utils.makeGetRequest(titleurl, cookies, callstackpath, maxrequestsperminute)

			data = json.loads(content)

			if not os.path.isdir(os.path.join(metapath, "Titles")):
				os.mkdir(os.path.join(metapath, "Titles"))
			if not os.path.isdir(os.path.join(metapath, "Titles", titleid)):
				os.mkdir(os.path.join(metapath, "Titles", titleid))

			fh = open(os.path.join(metapath, "Titles", titleid, "meta.json"), 'w')
			fh.write(content)
			fh.close()

			if os.path.exists(os.path.join(metapath, "Titles", titleid, "coverart.jpg")):
				iconpath = os.path.join(metapath, "Titles", titleid, "coverart.jpg")
			else:
				iconpath = ""

			thetitle = data["title"]
			mdplink = data["mdpLink"]
			trackid = data["trackId"]

			if data["isShow"]:

				seasondataurl = "http://api-global.netflix.com/desktop/odp/episodes?forceEpisodes=true&routing=redirect&video=" + titleid
				seasondata = utils.makeGetRequest(seasondataurl, cookies, callstackpath, maxrequestsperminute)

				fh = open(os.path.join(metapath, "Titles", titleid, "seasondata.json"),'w')
				fh.write(seasondata)
				fh.close()



				data = json.loads(seasondata)
				seasoncounter = 0
				for season in data["episodes"]:

					#http://www.netflix.com/WiMovie/70136119?trkid=50263680&actionMethod=seasonDetails&seasonId=70061401&seasonKind=ELECTRONIC



					for episode in season:
						if not os.path.exists(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]))):
							os.mkdir(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"])))
						fname = "S" + str(episode["season"]).zfill(2) + "E" + str(episode["episode"]).zfill(2)
						fh = open(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]), fname + ".json"), 'w')
						fh.write(json.dumps(episode))
						fh.close()

						stillswidth = 0
						stillspath = ""


						if "stills" in episode:
							for still in episode["stills"]:
								width = still["width"]
								try:
									if(int(width) > stillswidth):
										stillswidth = int(width)
										stillspath = still["url"]
								except:
									pass

							if stillspath != "":
								try:
									stillimage = utils.makeGetRequest(stillspath, cookies, callstackpath, maxrequestsperminute)
									fh = open(os.path.join(metapath, "Titles", titleid, "Season " + str(episode["season"]), fname + ".jpg"), 'wb')
									fh.write(stillimage)
									fh.close()
								except:
									pass

									#http://www.netflix.com/WiMovie/70297439?actionMethod=seasonDetails&seasonId=70296034&seasonKind=ELECTRONIC

					seasoninfourl = "http://www.netflix.com" + mdplink + "?&actionMethod=seasonDetails&seasonId=" + str(season[0]["seasonId"]) + "&seasonKind=ELECTRONIC"
					seasoninforesponse = utils.makeGetRequest(seasoninfourl, cookies, callstackpath, maxrequestsperminute)

					seasoninfo = json.loads(seasoninforesponse)

					seasoninfosynopsismatch = re.compile('<\/h2><p class=\"synopsis\".*?>(.*?)<\/p>', re.DOTALL).findall(seasoninfo["html"])
					synopsis = ""
					for syno in seasoninfosynopsismatch:
						synopsis += syno

					fh = open(os.path.join(metapath, "Titles", titleid, "Season " + str(season[0]["season"]), "synopsis"), 'w')
					fh.write(json.dumps(synopsis))
					fh.close()

			print "Netflix: " + thetitle.encode('utf-8') + " has been updated"
			xbmc.executebuiltin('Notification("Netflix", "' + thetitle.encode('utf-8') + ' has been updated", 5000, ' + iconpath + ')')

		os.remove(os.path.join(metapath, "active", "scrape_title_" + titleid))

def scrapeMyList(cookies, callstackpath, maxrequestsperminute, metapath):

	if not os.path.isdir(os.path.join(metapath, "active")):
		os.mkdir(os.path.join(metapath, "active"))

	if not os.path.exists(os.path.join(metapath, "active", "scrape_mylist")):



		fh = open(os.path.join(metapath, "active", "scrape_mylist"), 'w')
		fh.write("currently scraping MyList")
		fh.close()



		#def makeGetRequest(url, cookies, callstackpath, maxcalls):
		content = utils.makeGetRequest("https://www.netflix.com/MyList", cookies, callstackpath, maxrequestsperminute)
		#expr = "<div.*?class=\"agMovie agMovie-lulg\".*?<img.*?src=\"(.*?)\".*?>.*?<a.*?WiPlayer\\?movieid=(.*?)&trkid=(.*?)&";
		expr = '<div class="agMovie agMovie-lulg">.*?<img.*?src="(.*?)" ><a .*? href=".*?WiPlayer\\?movieid=(.*?)&trkid=(.*?)&'
		#content = content.decode('utf-8')


		if '<div id="yui-main">' in content:
			content = content[content.index('<div id="yui-main">'):]


			for ffile in os.listdir(os.path.join(metapath,"MyList")):
				os.remove(os.path.join(metapath, "MyList", ffile))

			matches = re.compile(expr, re.DOTALL).findall(content)
			counter = 0
			for boxart, titleid, trackid in matches:
				counter += 1
				fh = open(os.path.join(metapath, "MyList", titleid), 'w')
				fh.write(str(counter))
				fh.close()

				titlefile = os.path.join(metapath, 'Titles', titleid, 'meta.json')
				coverart = utils.makeGetRequest(boxart, cookies, callstackpath, maxrequestsperminute)
				if not os.path.isdir(os.path.join(metapath, "Titles", titleid)):
					os.mkdir(os.path.join(metapath, "Titles", titleid))

				fh = open(os.path.join(metapath, "Titles", titleid, "folder.jpg"), 'wb')
				fh.write(coverart)
				fh.close()
				fh = open(os.path.join(metapath, "Titles", titleid, "coverart.jpg"), 'wb')
				fh.write(coverart)
				fh.close()

				if os.path.exists(os.path.join(metapath, "Titles", titleid, "coverart.jpg")):
					iconpath = os.path.join(metapath, "Titles", titleid, "coverart.jpg")
				else:
					iconpath = ""

				UpdateTitle = False
				if os.path.exists(titlefile):
					age = xbmcvfs.Stat(titlefile).st_mtime()
					now = time.time()

					oneday = 24 * 60 * 60

					if (now-age) > (oneday*int(sys.argv[3])):
						UpdateTitle = True
				else:
					UpdateTitle = True

				if UpdateTitle:
					scrapeTitle(cookies, callstackpath, maxrequestsperminute, metapath, titleid, trackid)

		os.remove(os.path.join(metapath, "active", "scrape_mylist"))
		#xbmc.executebuiltin('Notification("Netflix", "MyList has been Updated", 5000, ' + iconpath + ')')
# 1 UserName
# 2 Password
# 3 CacheAge
# 4 CookiePath
# 5 CallStackPath
# 6 MaxRequestsPerMinute
# 7 AddonID
# 8 MetaRoot
# 9 TitleID
# 10 TrackID


def scrapeAPIURL(cookies, callstackpath, maxrequestsperminute, metapath):
	response = utils.makeGetRequest("http://www.netflix.com/WiGenre?agid=83", cookies, callstackpath, maxrequestsperminute)

	apimatch = re.compile('\"BUILD_IDENTIFIER\":\"(.*?)\".*?\"SHAKTI_API_ROOT\":\"(.*?)\"', re.DOTALL).findall(response)
	apiurl = ""
	for build, root in apimatch:
		apiurl = root + "/" + build
	if apiurl != "":
		fh = open(os.path.join(metapath, "apiurl"), 'w')
		fh.write(apiurl)
		fh.close()
