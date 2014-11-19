import os
import sys
import re
import urllib
import urllib2
import time

import xbmc
import xbmcaddon
import xbmcvfs
import codecs

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

			fh = open(os.path.join(metapath, "apiurl"), 'r')
			apiurl = fh.read()
			fh.close()

			titleUrl = apiurl + "/bob?titleid=" + sys.argv[3] + "&trackid=" + sys.argv[4]

			content = netflixutils.makeGetRequest(titleUrl, auth.cookiejar)

			match = re.compile("{\"isMovie\":(.*?),\"isShow\":(.*?),\"titleid\":(.*?),\"title\":\"(.*?)\",", re.DOTALL).findall(content)
			
			if not os.path.isdir(os.path.join(metapath, "titles", sys.argv[3])):
				os.mkdir(os.path.join(metapath, "titles", sys.argv[3]))



			thetitle = ""
			coverartpath = ""
			for ismovie, isshow, titleid, title in match:
				thetitle = title
				coverartpath = os.path.join(metapath, "titles", sys.argv[3], "coverart.jpg")

				if isshow == "true":

					#update the tv series info

					#http://api-global.netflix.com/desktop/odp/episodes?forceEpisodes=true&routing=redirect&video=70185014
					seasondataurl = "http://api-global.netflix.com/desktop/odp/episodes?forceEpisodes=true&routing=redirect&video=" + titleid
					seasondata = netflixutils.makeGetRequest(seasondataurl, auth.cookiejar)

					fh = open(os.path.join(metapath, "titles", sys.argv[3],  "seasonddata.json"), 'w')
					fh.write(seasondata)
					fh.close()

					#Split out seasons and episodes
					# searchsting = seasondata episode substring
					searchstring = seasondata[seasondata.index('"episodes":'):]
					searchexpr = "{\"title\":\"(.*?)\",\"season\":(.*?),\"seasonYear\":.*?,\"episode\":(.*?),\"synopsis\":\".*?\",\"seasonId\":.*?,\"episodeId\":.*?,\"videoId\":.*?,\"nonMemberViewable\":.*?,\"runtime\":.*?,\"availableForED\":.*?,\"availabilityMessage\":.*?,\"stills\":\\[(.*?)\\],\"bookmarkPosition\":(.*?),\"lastModified\":\".*?\"}"
					#matches = re.compile(searchexpr, re.DOTALL).findall(searchstring)
					matches = re.compile(searchexpr, re.DOTALL).finditer(searchstring)

					#epcounter = 0
					#for title, season, episode, stills, bookmarkPosition in matches:
					for match in matches:
						title=match.group(1)
						season = match.group(2)
						episode = match.group(3)
						stills = match.group(4)
						bookmarkPosition = match.group(5)

						if not os.path.isdir(os.path.join(metapath, "titles", sys.argv[3], "Season " + season)):
							os.mkdir(os.path.join(metapath, "titles", sys.argv[3], "Season " + season))

						# write episode data
						ffilename = "S" + season.zfill(2) + "E" + episode.zfill(2)
						fh = open (os.path.join(metapath, "titles", sys.argv[3], "Season " + season, ffilename + ".json"), 'w')
						#print match.group()
						fh.write(match.group())
						
						# TODO: Get still image

						stillspath = ""
						stillswidth = 0

						stillsexpr = "{\"offset\":(.*?),\"sequence\":(.*?),\"type\":\"(.*?)\",\"url\":\"(.*?)\",\"height\":(.*?),\"width\":(.*?)}"

						stillsmatches = re.compile(stillsexpr, re.DOTALL).finditer(stills)

						for stillsmatch in stillsmatches:
							width = stillsmatch.group(6)
							try:
								if(int(width) > stillswidth):
									stillswidth = int(width)
									stillspath = stillsmatch.group(4)
							except:
								pass

						if stillspath != "":
							try:
								stillimage = netflixutils.makeGetRequest(stillspath, auth.cookiejar)
								fh = open (os.path.join(metapath, "titles", sys.argv[3], "Season " + season, ffilename + ".jpg"), 'wb')
								fh.write(stillimage)
								fh.close()
							except:
								pass



						#epcounter += 1

			thetitle = netflixutils.cleanurlstring(thetitle)
			#tilte = thetitle.decode('ascii', errors='ignore')




			fh = open(os.path.join(metapath, "titles", sys.argv[3],  "meta.json"), 'w')
			fh.write(content)
			fh.close()


			if not os.path.exists(coverartpath):
				coverartpath = iconpath

			if(thetitle != ""):
				#frig it so that encoding errors are effectively ignored
				try:
					xbmc.executebuiltin('Notification("Netflix", "{0} has been updated", 5000, {1})'.format(thetitle, coverartpath))
				except:
					xbmc.executebuiltin('Notification("Netflix", "Title updated", 5000, ' + coverartpath + ')')
			else:
				xbmc.executebuiltin('Notification("Netflix", "Title updated", 5000, ' + coverartpath + ')')



	def ensureFolder(self):
		metapath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix/meta')

		if not os.path.isdir(metapath):
			os.mkdir(metapath)

		if not os.path.isdir(os.path.join(metapath, "titles")):
			os.mkdir(os.path.join(metapath, "titles"))
Main()