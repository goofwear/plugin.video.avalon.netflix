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

		content = netflixutils.makeGetRequest("http://www.netflix.com/MyList", auth.cookiejar)
		expr = "<div class=\"agMovie agMovie-lulg\">.*?<img  .*?src=\"(.*?)\" >.*?<a.*?WiPlayer\\?movieid=(.*?)&trkid=(.*?)&";

		print content

		matches = re.compile(expr, re.DOTALL).findall(content)

		counter = 0
		for boxart, titleid, trackid in matches:
			counter += 1
			fh = open(os.path.join(metapath, "mylist", titleid), 'w')
			fh.write(str(counter))
			fh.close()

			titlefile = os.path.join(metapath, 'titles', titleid, 'meta.json')
			coverart = netflixutils.makeGetRequest(boxart, auth.cookiejar)
			if not os.path.isdir(os.path.join(metapath, "titles", titleid)):
				os.mkdir(os.path.join(metapath, "titles", titleid))

			fh = open(os.path.join(metapath, "titles", titleid, "folder.jpg"), 'wb')
			fh.write(coverart)
			fh.close()
			fh = open(os.path.join(metapath, "titles", titleid, "coverart.jpg"), 'wb')
			fh.write(coverart)
			fh.close()


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
				xbmc.executebuiltin('xbmc.runscript(special://home/addons/plugin.video.avalon.netflix/UpdateTitle.py, ' + sys.argv[1] + ', ' + sys.argv[2] + ', ' + titleid + ', ' + trackid + ')')


		xbmc.executebuiltin('Notification("Netflix", "MyList has been updated", 5000, ' + iconpath + ')')

	def ensureFolder(self):
		metapath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "mylist")):
			os.mkdir(os.path.join(metapath, "mylist"))
Main()