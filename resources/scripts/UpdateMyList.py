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
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7])
		iconpath = xbmc.translatePath('special://home/addons/' + sys.argv[7] + '/icon.png')
		cookiepath = sys.argv[4]

		cookies = cookielib.MozillaCookieJar()
		if os.path.exists(cookiepath):
			cookies.load(cookiepath)

		auth.login(sys.argv[1], sys.argv[2], cookies, sys.argv[5], sys.argv[6])
		#def login(username, password, cookies, callstackpath, maxcalls):

		self.ensureFolders()


		scraper.scrapeMyList(cookies, sys.argv[5], sys.argv[6], sys.argv[8])

		#xbmc.executebuiltin('Notification("Netflix", "MyList has been Updated", 5000, ' + iconpath + ')')

	def ensureFolders(self):
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7] + '/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "MyList")):
			os.mkdir(os.path.join(metapath, "MyList"))
		if not os.path.isdir(os.path.join(metapath, "Titles")):
			os.mkdir(os.path.join(metapath, "Titles"))


Main()
