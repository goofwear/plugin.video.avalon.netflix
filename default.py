import cookielib
import os
import re
import sys
import subprocess
import time
import urllib

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs


# get initial plugin settings
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')

# add local lib to sys.path to import local library files
sys.path.append(os.path.join(xbmc.translatePath('special://home/addons/' + addonID), 'resources', 'lib'))
import avalon_kodi_netflix_interop_auth as auth
import avalon_kodi_netflix_menus as menus
import avalon_kodi_utils as utils
import avalon_kodi_netflix_interop_scrape as scraper

# read addon settings
username = addon.getSetting('username')
password = addon.getSetting('password')


# determine additional resource paths
maxrequestsperminute = 50

# set paths for re-use throughout plugin
metaroot = xbmc.translatePath('special://profile/addon_data/' + addonID + '/meta')
playerpath = xbmc.translatePath('special://home/addons/' + addonID + '/resources/LaunchPlayer.exe')
cookiepath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/cookies')
callstackpath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/callstack')
apiurlpath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/apiurl')



# ensure folders
if not os.path.exists(metaroot):
	os.mkdir(metaroot)

if not os.path.isdir(os.path.join(metaroot, "Genres")):
	os.mkdir(os.path.join(metaroot, "Genres"))
if not os.path.isdir(os.path.join(metaroot, "GenreTitles")):
	os.mkdir(os.path.join(metaroot, "GenreTitles"))

# setup the cookies
cookiejar = cookielib.MozillaCookieJar()
if os.path.exists(cookiepath):
	cookiejar.load(cookiepath)

# get path parameters
params = utils.paramStringToDict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode',''))
genre = urllib.unquote_plus(params.get('genre',''))
genrename = urllib.unquote_plus(params.get('genrename', ''))
videoid = urllib.unquote_plus(params.get('title',''))
seriesid = urllib.unquote_plus(params.get('series',''))
seasonid = urllib.unquote_plus(params.get('seasonid', ''))
season = urllib.unquote_plus(params.get('season', ''))
track = urllib.unquote_plus(params.get('track',''))

auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute)
cookiejar.save(cookiepath)


# The real guts start here... which mode are we running?
if mode == 'listgenres':
	# list the genres found in /meta/genres/genres.json
	# def genres(addon, addonID, pluginhandle, metapath                                       , viewpath   , callstackpath, maxrequestsperminute, cookiepath, metaroot)
	menus.genres(addon, addonID, pluginhandle, os.path.join(metaroot, "genres", "genres.json"), sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, metaroot)
elif mode == 'listsubgenres':
	# list the sub-genres of the genre specified by the genre parameter
	# def subGenres(addon, addonID, pluginhandle, metapath                                         , viewpath   , callstackpath, maxrequestsperminute, cookiepath, genreid):
	menus.subGenres(addon, addonID, pluginhandle, os.path.join(metaroot, "genres", genre + ".json"), sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, genre)
elif mode == 'listgenretitles':
	# determine the genre's meta data file path
	genretitlesmetapath = os.path.join(metaroot, "genreTitles", genre + ".json")

	menus.genreTitles(addon, addonID, pluginhandle, genretitlesmetapath, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, genre, metaroot)
elif mode == 'listseasons':
	# determine the mata data folder for the series' title store
	metapath = os.path.join(metaroot, "Titles", seriesid)

	# list the seasons for the specified title
	# def seasons(addon, addonID, pluginhandle, metapath, viewpath   , callstackpath, maxrequestsperminute, cookiepath, seriesid, metaroot)
	menus.seasons(addon, addonID, pluginhandle, metapath, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, seriesid, metaroot)
elif mode == 'listepisodes':
	# determine the meta data folder for the series' title store
	metapath = os.path.join(metaroot, "Titles", seriesid)

	# list the episodes for the specified series and season
	# def episodes(addon, addonid, pluginhandle, metapath, viewpath   , callstackpath, maxreq              , cookiepath, seriesid, seasonid, metaroot)
	menus.episodes(addon, addonID, pluginhandle, metapath, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, seriesid, seasonid, metaroot)
elif mode == 'playvideo':
	# play the video

	# first of all stop the kodi player if it is currently playing
	if(xbmc.Player().isPlaying()):
		xbmc.Player().stop()

	try:
		subprocess.Popen(playerpath + ' /movieid=' + videoid, shell=False)
	except:
		pass


elif mode == 'playepisode':
	# play the episode

	# first of all stop the kodi player if it is currently playing
	if(xbmc.Player().isPlaying()):
		xbmc.Player().stop()
	try:
		subprocess.Popen(playerpath + ' /movieid=' + videoid + ' /seriesid=' + seriesid + ' /savepath=' + os.path.join(metaroot, "titles", seriesid) + ' /un=' + username + ' /pw=' + password, shell=False)
	except:
		pass

elif mode == 'mylist':
	# list MyList titles
	# def myList(viewpath   , pluginhandle, metaroot, addon)
	menus.myList(sys.argv[0], pluginhandle, metaroot, addon, callstackpath, maxrequestsperminute, cookiepath)


elif mode=='search':
	# create a keyboard dialog and take a search string
	keyboard = xbmc.Keyboard('', utils.translation(addon, 30203))
	keyboard.doModal()

	# if something is entered and submitted, get the text and pass it to the search menu
	if keyboard.isConfirmed() and keyboard.getText():
		search_string = keyboard.getText()

		menus.search(addon, addonID, pluginhandle, sys.argv[0], callstackpath, maxrequestsperminute, cookiejar, search_string, metaroot, cookiepath)
else:

	# clear any active states
	if os.path.exists(os.path.join(metaroot, "active")):
		for ffile in os.listdir(os.path.join(metaroot, "active")):
			os.remove(os.path.join(metaroot, "active", ffile))


	# check that the basic meta cache has been saved and has not expired
#	UpdateGenres = False
#	if os.path.exists(os.path.join(metaroot, "Genres", "genres.json")):
#		oneday = 24 * 60 * 60
#		if utils.fileIsOlderThan(os.path.join(metaroot, "Genres", "genres.json"), (oneday * int(addon.getSetting("cacheage")))):
#			UpdateGenres = True
#	else:
#		UpdateGenres = True
#
#	if os.path.exists(os.path.join(metaroot, "active", "scrape_genres")):
#		UpdateGenres = False

	# check if MyList needs to be updated
#	UpdateMyList = False
#	if os.path.isdir(os.path.join(metaroot, "MyList")):

#		oneday = 24 * 60 * 60
#		for ffile in os.listdir(os.path.join(metaroot, "MyList")):
#			if utils.fileIsOlderThan(os.path.join(metaroot, "MyList", ffile), (oneday * int(addon.getSetting("mylistage")))):
#				UpdateMyList = True
#
#		if UpdateMyList:
#			print "Netflix: MyList is out-of-date"
#		else:
#			print "Netflix: MyList is up-to-date"
#	else:
#		print "Netflix: MyList data is not available"
#		UpdateMyList = True
#
#	# don't re-cache if already in progress - this will cause weird bounce on the available titles
#	if os.path.exists(os.path.join(metaroot, "active", "scrape_mylist")):
#		UpdateMyList = False



	# update MyList
#	if UpdateMyList:
#		if addon.getSetting("promptformylist") == "true":
#			dialog = xbmcgui.Dialog()
#			ret = dialog.yesno('Netflix', utils.translation(addon, 30202))
#			if ret:
#				# make sure we can login to the Netflix website
#				while not auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute):
#					d = xbmcgui.Dialog()
#					addon.setSetting("username", d.input(utils.translation(addon, 30004)))
#					addon.setSetting("password", d.input(utils.translation(addon, 30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
#					username = addon.getSetting("username")
#					password = addon.getSetting("password")
#				xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateMyList.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ', ' + metaroot + ')')
#		else:
#			xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateMyList.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ', ' + metaroot + ')')
#
	# make sure the API url is upto date
	scraper.scrapeAPIURL(cookiejar, callstackpath, maxrequestsperminute, metaroot)

	# display the main index
	# def index(addon, addonID, pluginhandle, metapath, viewpath   , callstackpath, maxrequestsperminute, cookiepath)
	menus.index(addon, addonID, pluginhandle, metaroot, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath)
