import cookielib
import sys
import re
import time
import xbmc
import xbmcaddon
import xbmcvfs
import urllib



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
        #if os.path.exists(cookiepath):
        #	cookies.load(cookiepath)


        crumbs = cookies

        auth.login(sys.argv[1], sys.argv[2], cookies, sys.argv[5], sys.argv[6])
        #def login(username, password, cookies, callstackpath, maxcalls):




        # http://www.netflix.com/AddToQueue?movieid=70153372&evDetail=false&qtype=INSTANT&trkid=13462293&authURL=1424536859109.0FX20tcMm3LhJVtqopdwFPLSgjg%3D&evType=EV2&section=WATCHNOW
        # makeGetRequest(url, cookies, callstackpath, maxcalls):
        # requestUrl = "http://www.netflix.com/AddToQueue?movieid={0}&evDetail=false&qtype=INSTANT&trkid={1}&authURL={2}&evType=EV2&section=WATCHNOW"
        requestUrl = "http://www.netflix.com/QueueDelete?movieid={0}&authURL={2}"
        #auth.login(addon.getSetting("username"), addon.getSetting("password"), cookiejar, callstackpath, str(maxrequestsperminute))
        #login(username, password, cookies, callstackpath, maxcalls):
        #print cookiejar
        #cookiejar.save(cookiepath)
        #print auth.auth



        #Get new authURL
        response = utils.makeGetRequest("http://www.netflix.com", cookies, sys.argv[5], sys.argv[6])

        # find matches - should return <input type="hidden" name="authURL" value="[the_value]" /> instances
        match = re.compile('a.*?authURL=(.*?)["&]', re.DOTALL).findall(str(response))

        # use the last instance found (there should only be one anyway...)
        authURL = ""
        for found in match:
        	if found != "":
        		authURL = found

        requestUrl = requestUrl.format(sys.argv[9], sys.argv[10], authURL, safe='')


        response = utils.makeGetRequest(requestUrl, cookies, sys.argv[5], str(sys.argv[6]))


        #self.ensureFolders()

        #def scrapeGenreTitles(cookies, callstackpath, maxrequestsperminute, metapath, genreid):


        #def scrapeTitle(cookies, callstackpath, maxrequestsperminute, metapath, titleid, trackid):
        #def scrapeMyList(cookies, callstackpath, maxrequestsperminute, metapath):
        scraper.scrapeMyList(cookies, sys.argv[5], sys.argv[6], sys.argv[8])
        #scraper.scrapeMyList(cookies, sys.argv[5], sys.argv[6], sys.argv[8], sys.argv[9], sys.argv[10])
        #scrapeGenres(cookies, callstackpath, maxrequestsperminute, metapath):


        xbmc.executebuiltin('Notification("Netflix", "Title Removed From MyList", 5000, ' + iconpath + ')')


	def ensureFolders(self):
		metapath = xbmc.translatePath('special://profile/addon_data/' + sys.argv[7] + '/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "Genres")):
			os.mkdir(os.path.join(metapath, "Genres"))
		if not os.path.isdir(os.path.join(metapath, "Titles")):
			os.mkdir(os.path.join(metapath, "Titles"))



Main()
