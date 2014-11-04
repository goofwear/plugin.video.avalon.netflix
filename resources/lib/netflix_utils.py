######################################################################
# netflic_utils.py                                                   #
######################################################################
# Author:   Iamdixon (avalonprojects.net)                            #
# Date:     2014-10-28                                               #
######################################################################
# helper functions to handle/meter Netflix requests - a text file is #
# used to maintain a persistent call stack between scripts. Each     #
# line in the text file is a timestamp (float) as we don't need any  #
# other information - this allows us to guage entries within a given #
# timeframe.                                                         #
#                                                                    #
# maintains compatibility with current versions of XBMC/Kodi.        #
######################################################################


### TODO - I think I might be getting file collisions with multiple processes attempting to write to the call stack???

import os
import time
import urllib2
import xbmc




### make url request wrapper - uses a text file to meter requests so that we don't get blocked by Netflix for scraping.
def makeGetRequest(url, cookies):

	# map the folder that the request meter is held in
	# TODO: is there a way to automatically discover the user data folder rather than hard coding the plugin id?
	callstackpath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix')
	# get path to the actual metering file
	callstack = os.path.join(callstackpath, "callstack")

	# do we need to check the call stack?
	doit = False
	if os.path.exists(callstack):
		doit = False
	else:
		doit = True

	lines = [];

	# create a loop to continually check the call stack until there are less than 60 entries - then we can make a new request.


	while not doit:
		try:
			fh = open(callstack, 'r')
			lines = fh.read().split('\n')
			fh.close()

			# 60 = upto 60 requests per minute - need to do some testing to see how far we can push this out!!!
			if(len(lines) <= 50):
				doit=True
			else:
				print 'too many requests in stack (' + str(len(lines)) + ')'


			# read the lines
			for line in lines:
				#print 'line: ' + line
				#print 'time: ' + str(time.time())
				try:
					# check if the timestamp of the row is older than a minute
					if float(line) + 60 <  time.time():
						lines.remove(line) # remove old lines
						
					# update the metering file

				except:
					pass

			fh = open(callstack, 'w')
			fh.write('\n'.join('\n'.join(lines).split()))
			#fh.write('\n'.join(lines))
			#fh.writelines(lines)
			fh.close()
		except Exception, Argumnent:
			print "Netflix: FileLock encountered - trying again"
			pass

	return _doRequest(url, cookies, lines, callstack)


def _doRequest(url, cookies, lines, callstack):
	try:
		# add a timestamp to the metering file
		lines += (str(time.time()),)
		fh = open(callstack, 'w')
		fh.write('\n'.join('\n'.join(lines).split()))
		#fh.writelines(lines)
		fh.close()

		# make the request and return the response!!!
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
		return opener.open(url).read()
	except Exception, Argument:
		print "Netflix FileLock encountered - trying again"
		return makeGetRequest(url, cookies)