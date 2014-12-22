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

# args
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


class Main:
	def __init__(self):
		print 'started'
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7])
		iconpath = xbmc.translatePath('special://home/addons/' + sys.argv[7] + '/icon.png')
		cookiepath = sys.argv[4]

		cookies = cookielib.MozillaCookieJar()
		if os.path.exists(cookiepath):
			cookies.load(cookiepath)

		auth.login(sys.argv[1], sys.argv[2], cookies, sys.argv[5], sys.argv[6])
		#def login(username, password, cookies, callstackpath, maxcalls):

		self.ensureFolders()

		#def scrapeGenreTitles(cookies, callstackpath, maxrequestsperminute, metapath, genreid):



		scraper.scrapeTitle(cookies, sys.argv[5], sys.argv[6], sys.argv[8], sys.argv[9], sys.argv[10])
		#scrapeGenres(cookies, callstackpath, maxrequestsperminute, metapath):


		xbmc.executebuiltin('Notification("Netflix", "Titles Updated", 5000, ' + iconpath + ')')
		print 'done'

	def ensureFolders(self):
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7] + '/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "Genres")):
			os.mkdir(os.path.join(metapath, "Genres"))
		if not os.path.isdir(os.path.join(metapath, "Titles")):
			os.mkdir(os.path.join(metapath, "Titles"))

Main()