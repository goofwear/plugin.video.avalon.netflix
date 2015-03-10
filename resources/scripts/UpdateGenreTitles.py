import cookielib
import sys
import re
import time
import xbmc
import xbmcaddon
import xbmcvfs



sys.path.append(os.path.join(xbmc.translatePath('special://home/addons/' + sys.argv[7]), "resources", "lib"))

import avalon_kodi_netflix_interop_auth as auth
import avalon_kodi_utils as utils
import avalon_kodi_netflix_interop_scrape as scraper

class Main:
	def __init__(self):
		print "Netflix: Updating Genre Titles (" + sys.argv[10] + ")"
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7])
		iconpath = xbmc.translatePath('special://home/addons/' + sys.argv[7] + '/icon.png')
		cookiepath = sys.argv[4]

		cookies = cookielib.MozillaCookieJar()
		if os.path.exists(cookiepath):
			cookies.load(cookiepath)

		auth.login(sys.argv[1], sys.argv[2], cookies, sys.argv[5], sys.argv[6])
		#def login(username, password, cookies, callstackpath, maxcalls):

		cookies.save(cookiepath)

		self.ensureFolders()

		#   def scrapeGenreTitles(cookies, callstackpath, maxrequestsperminute, metapath, genreid, cacheage, genrename):
		scraper.scrapeGenreTitles(cookies, sys.argv[5], sys.argv[6], sys.argv[8], sys.argv[9], sys.argv[3], sys.argv[10])

		print "Netflix: " + sys.argv[10] + " Titles Updated"
		xbmc.executebuiltin('Notification("Netflix", "' + sys.argv[10] + ' Titles Updated", 5000, ' + iconpath + ')')

	def ensureFolders(self):
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7] + '/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "Genres")):
			os.mkdir(os.path.join(metapath, "Genres"))
		if not os.path.isdir(os.path.join(metapath, "Titles")):
			os.mkdir(os.path.join(metapath, "Titles"))

Main()
