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

# read addon settings
username = addon.getSetting('username')
password = addon.getSetting('password')


# determine additional resource paths
maxrequestsperminute = 50

metaroot = xbmc.translatePath('special://profile/addon_data/' + addonID + '/meta')
playerpath = xbmc.translatePath('special://home/addons/' + addonID + '/resources/LaunchPlayer.exe')
blankvideo = xbmc.translatePath('special://home/addons/' + addonID + '/resources/blank.mp4')
cookiepath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/cookies')
callstackpath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/callstack')
apiurlpath = xbmc.translatePath('special://profile/addon_data/' + addonID + '/apiurl')


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

# make sure we can login to the Netflix website
#while not auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute):
#	d = xbmcgui.Dialog()
#	addon.setSetting("username", d.input(utils.translation(addon, 30004)))
#	addon.setSetting("password", d.input(utils.translation(addon, 30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
#	username = addon.getSetting("username")
#	password = addon.getSetting("password")

cookiejar.save(cookiepath)

# check that the basic meta cache has been saved and has not expired
UpdateGenres = False
if os.path.exists(os.path.join(metaroot, "Genres", "genres.json")):
	oneday = 24 * 60 * 60
	if utils.fileIsOlderThan(os.path.join(metaroot, "Genres", "genres.json"), (oneday * int(addon.getSetting("cacheage")))):
		UpdateGenres = True
else:
	UpdateGenres = True

if UpdateGenres:
	if addon.getSetting("promptforcache") == "true":
		dialog = xbmcgui.Dialog()
		ret = dialog.yesno('Netflix', utils.translation(addon, 30200))
		if(ret):
			# make sure we can login to the Netflix website
			while not auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute):
				d = xbmcgui.Dialog()
				addon.setSetting("username", d.input(utils.translation(addon, 30004)))
				addon.setSetting("password", d.input(utils.translation(addon, 30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
				username = addon.getSetting("username")
				password = addon.getSetting("password")
			xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metaroot + ')')
	else:
# make sure we can login to the Netflix website
		while not auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute):
			d = xbmcgui.Dialog()
			addon.setSetting("username", d.input(utils.translation(addon, 30004)))
			addon.setSetting("password", d.input(utils.translation(addon, 30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
			username = addon.getSetting("username")
			password = addon.getSetting("password")
		xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenres.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metaroot + ')')

if mode == 'listgenres':
	#def genres(addon, addonID, pluginhandle, metapath, viewpath):
	menus.genres(addon, addonID, pluginhandle, os.path.join(metaroot, "genres", "genres.json"), sys.argv[0], callstackpath, maxrequestsperminute, cookiepath)
elif mode == 'listsubgenres':
	#def subGenres(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath):
	menus.subGenres(addon, addonID, pluginhandle, os.path.join(metaroot, "genres", genre + ".json"), sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, genre)
elif mode == 'listgenretitles':
	#def genreTitles(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath, genreid):
	genretitlesmetapath = os.path.join(metaroot, "genreTitles", genre + ".json")
	updateGenreTitles = False
	if os.path.exists(genretitlesmetapath):
		oneday = 24 * 60 * 60
		if utils.fileIsOlderThan(genretitlesmetapath, (oneday * int(addon.getSetting("cacheage")))):
			updateGenreTitles = True
	else:
		updateGenreTitles = True

	if updateGenreTitles:
		if addon.getSetting("promptforcache") == "true":
			dialog = xbmcgui.Dialog()
			ret = dialog.yesno('Netflix', utils.translation(addon, 30200))
			if(ret):
				# make sure we can login to the Netflix website
				while not auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute):
					d = xbmcgui.Dialog()
					addon.setSetting("username", d.input(utils.translation(addon, 30004)))
					addon.setSetting("password", d.input(utils.translation(addon, 30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
					username = addon.getSetting("username")
					password = addon.getSetting("password")
				xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metaroot + ',' + genre + ',' + genrename + ')')
		else:
			# make sure we can login to the Netflix website
			while not auth.login(username, password, cookiejar, callstackpath, maxrequestsperminute):
				d = xbmcgui.Dialog()
				addon.setSetting("username", d.input(utils.translation(addon, 30004)))
				addon.setSetting("password", d.input(utils.translation(addon, 30005), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT))
				username = addon.getSetting("username")
				password = addon.getSetting("password")
			xbmc.executebuiltin('xbmc.runscript(special://home/addons/' + addonID + '/resources/scripts/UpdateGenreTitles.py, ' + addon.getSetting("username") + ', ' + addon.getSetting("password") + ', ' + addon.getSetting("cacheage") + ', ' + cookiepath + ', ' + callstackpath + ', ' + str(maxrequestsperminute) + ', ' + addonID + ',' + metaroot + ',' + genre + ',' + genrename + ')')

	menus.genreTitles(addon, addonID, pluginhandle, genretitlesmetapath, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, genre, metaroot)
elif mode == 'listseasons':
	metapath = os.path.join(metaroot, "Titles", seriesid)

	#def seasons(addon, addonID, pluginhandle, metapath, viewpath, callstackpath, maxrequestsperminute, cookiepath, seriesid, metaroot)
	menus.seasons(addon, addonID, pluginhandle, metapath, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, seriesid, metaroot)
elif mode == 'listepisodes':
	metapath = os.path.join(metaroot, "Titles", seriesid)
	menus.episodes(addon, addonID, pluginhandle, metapath, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath, seriesid, seasonid, metaroot)
elif mode == 'playvideo':
	if(xbmc.Player().isPlaying()):
		xbmc.Player().stop()
#	xbmc.Player().play(blankvideo)
	try:
		subprocess.Popen(playerpath + ' /movieid=' + videoid, shell=False)
	except:
		pass
elif mode == 'playepisode':
	if(xbmc.Player().isPlaying()):
		xbmc.Player().stop()

	print playerpath + ' /movieid=' + videoid + ' /seriesid=' + seriesid + ' /savepath=' + os.path.join(metaroot, "titles", seriesid) + ' /un=' + username + ' /pw=' + password
	print addon.getSetting("username")

	subprocess.Popen(playerpath + ' /movieid=' + videoid + ' /seriesid=' + seriesid + ' /savepath=' + os.path.join(metaroot, "titles", seriesid) + ' /un=' + username + ' /pw=' + password, shell=False)

elif mode == 'mylist':
	menus.myList(sys.argv[0], pluginhandle, metaroot)
else:
	menus.index(addon, addonID, pluginhandle, metaroot, sys.argv[0], callstackpath, maxrequestsperminute, cookiepath);