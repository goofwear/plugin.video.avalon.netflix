import os
import sys
import re
import urllib
import urllib2
import time

import xbmc
import xbmcaddon
import xbmcvfs

sys.path.append(os.path.join(xbmc.translatePath('special://home/addons/plugin.video.avalon.netflix/'), "resources", "lib")) 

import netflix_interop_auth as auth
import netflix_utils as netflixutils # utility methods (incl. request metering)


class Main:
	def __init__(self):
		metapath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix/meta')
		iconpath = xbmc.translatePath('special://home/addons/plugin.video.avalon.netflix/icon.png')

		self.ensureFolder()

		auth.login(sys.argv[1], sys.argv[2])

		if(sys.argv[3]):
			genrefile = os.path.join(metapath, "genres", sys.argv[3] + ".json")

			fh = open(os.path.join(metapath, "apiurl"), 'r')
			apiurl = fh.read()
			fh.close()


			content = ""

			start = 0
			size = 100

			titles = ""

			while not content.startswith('{"catalogItems":[]}'):
				requesturl = apiurl + "/wigenre?genreId=" + sys.argv[3] + "&full=false&from=" +str(start) + "&to=" + str(start + size)
				start = start + size + 1

				content = netflixutils.makeGetRequest(requesturl, auth.cookiejar)

				print requesturl
				print content

				match = re.compile("{\"boxart\":\"(.*?)\",\"titleId\":(.*?),\"title\":\"(.*?)\",\"playerUrl\":\"(.*?)\",\"trackId\":(.*?)}", re.DOTALL).findall(content)


				for boxart, titleid, title, playerurl, trackid in match:
					if titles != "":
						titles += ","

					title = "{\"boxart\":\"" + boxart + "\",\"titleId\":" + titleid + ",\"title\":\"" + title + "\",\"playerUrl\":\"" + playerurl + "\",\"trackId\":" + trackid + "}"
					titles += title

					if not os.path.isdir(os.path.join(metapath, "genreTitles", sys.argv[3])):
						os.mkdir(os.path.join(metapath, "genreTitles", sys.argv[3]))

					fh = open(os.path.join(metapath, "genreTitles", sys.argv[3], titleid + ".json"), 'w')
					fh.write(title)
					fh.close()

			titles = "{\"catalogItems\":[" + titles + "]}"

			fh = open(os.path.join(metapath, "genreTitles", sys.argv[3] + ".json"), 'w')
			fh.write(titles)
			fh.close()

			if(len(sys.argv) > 4):
				xbmc.executebuiltin('Notification("Netflix", "Titles updated for ' + sys.argv[4] + '", 5000, ' + iconpath + ')')
			else:
				xbmc.executebuiltin('Notification("Netflix", "Titles updated", 5000, ' + iconpath + ')')



	def ensureFolder(self):
		metapath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "genreTitles")):
			os.mkdir(os.path.join(metapath, "genreTitles"))
Main()