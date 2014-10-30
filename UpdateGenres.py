import sys
import re
import time

import xbmc
import xbmcaddon
import xbmcvfs

# add project library folder to the system path so custom libs can be imported 
sys.path.append(os.path.join(xbmc.translatePath('special://home/addons/plugin.video.avalon.netflix/'), "resources", "lib")) 

import netflix_interop_auth as auth # utility methods for authentication
import netflix_utils as netflixutils # utility methods (incl. request metering)

# TODO: additional paramteres to handle passing of cache age from xbmc config - that or find a way to read the config from here!!! 
class Main:
	def __init__(self):


		metapath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix/meta')
		iconpath = xbmc.translatePath('special://home/addons/plugin.video.avalon.netflix/icon.png')

		self.ensureFolder()

		auth.login(sys.argv[1], sys.argv[2])

		# check file age

		genrefile = os.path.join(metapath, "genres", "genres.json")

		#doit = False
		doit = True

		#if(os.path.exists(genrefile)):
		#	age = xbmcvfs.Stat(genrefile).st_mtime()
		#	now = time.time()

		#	oneday = 24 * 60 * 60

		#	if (now-age) > oneday:
		#		doit = True
		#else:
		#	doit = True


		

		if doit:

			#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(auth.cookiejar))
			response = netflixutils.makeGetRequest("http://www.netflix.com", auth.cookiejar) # switched to using request metering

			#"<li><a href=\"(.*?)WiGenre\\?agid=(.*?)\">(.*?)</a></li>"
			matches = re.compile("<li><a href=\"(.*?)WiGenre\\?agid=(.*?)\">(.*?)</a></li>", re.DOTALL).findall(response)

			genres = ""
			for url, genreid, genrename in matches:
				url =  url + "WiGenre?agid=" + genreid
				if genres != "":
					genres += ","
				genres += "'" + genrename + "':'" + genreid + "'"
				try:
					response = netflixutils.makeGetRequest(url, auth.cookiejar)

					apimatch = re.compile('\"BUILD_IDENTIFIER\":\"(.*?)\",\"host\":\".*?\",\"SHAKTI_API_ROOT\":\"(.*?)\"', re.DOTALL).findall(response)
					apiurl = ""
					for build, root in apimatch:
						apiurl = root + "/" + build

					fh = open(os.path.join(metapath, "apiurl"), 'w')
					fh.write(apiurl)
					fh.close()

                	#string apimatchpattern = "\"BUILD_IDENTIFIER\":\"(.*?)\",\"host\":\".*?\",\"SHAKTI_API_ROOT\":\"(.*?)\"";
                	#Match apimatch = Regex.Match(content, apimatchpattern);

                	#apiurl = apimatch.Groups[2] + @"/" + apimatch.Groups[1];

					if '<div id="subGenres"' in response:
						response = response[response.index('<div id="subGenres"'):]

						matches = re.compile("<a.*?WiGenre\\?agid=(.*?)\\&.*?\">.*?<span>(.*?)</span>.*?</a>", re.DOTALL).findall(response)


						subGenres = ""
						for genreid, genrename in matches:
							if subGenres != "":
								subGenres += ","
							subGenres += "'" + genrename + "':'" + genreid + "'"



						if subGenres != "":
							subGenres = "Genres = {" + subGenres + "}"

							fh = open(os.path.join(metapath, "genres", genreid + ".json"), 'w')
							fh.write(subGenres)
							fh.close()
				except:
					pass


			if genres != "":
				grenres = "Genres = {" + genres + "}"

				fh = open(genrefile, 'w')
				fh.write(genres)
				fh.close()

				xbmc.executebuiltin('Notification("Netflix", "Genres Updated", 5000, ' + iconpath + ')')

	def ensureFolder(self):
		metapath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "genres")):
			os.mkdir(os.path.join(metapath, "genres"))
Main();