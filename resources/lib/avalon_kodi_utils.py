import os
import time
import urllib2
import xbmc
import xbmcvfs

def translation(addon, id):
	return addon.getLocalizedString(id).encode('utf-8')

def paramStringToDict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for pair in paramPairs:
			paramSplits = pair.split('=')
			if len(paramSplits) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def fileIsOlderThan(filepath, maxage):
	age = xbmcvfs.Stat(filepath).st_mtime()
	now = time.time()

	oneday = 24 * 60 * 60

	if((now - age) > (maxage)):
		return True
	else:
		return False

def cleanstring(inputstring):
	s=inputstring


	htmlCodes = (
		("'", '&#39;'),
		('"', '&quot;'),
		('>', '&gt;'),
		('<', '&lt;'),
		('&', '&amp;'),
		('"', '\\"'), 

	)

	for code in htmlCodes:
		s = s.replace(code[1], code[0])

	y = s
	y.encode('utf-8')
	q = y.encode('ascii')
	q.decode('ascii')
	s = q.decode('unicode_escape') 

	#s = eval("u'%s'" % s).encode('utf-8')




	return s


# Make an HTTP GET request using the provided cookies, checking the callstack, to ensure we don't get throttled
def makeGetRequest(url, cookies, callstackpath, maxcalls):

#	doit = False
#
#	lines = []
#
#	while not doit:
#		try:
#			if not os.path.exists(callstackpath):
#				pass
#			else:
#				fh = open(callstackpath, 'r')
#				lines = fh.read().split('\n')
#				fh.close()
#
#				for line in lines:
#					try:
#						if float(line) + 60 < time.time():
#							lines.remove(line)
#					except:
#						pass
#
#			try:
#				fh = open(callstackpath, 'w')
#				fh.write('\n'.join('\n'.join(lines).split()))
#				fh.close()
#			except:
#				makeGetRequest(url, cookies, callstackpath, maxcalls)
#
#			
#			if len(lines) <= maxcalls:
#				print str(len(lines)) + ":" + str(maxcalls)
#				doit = True
#			else:
#				print "Netflix: Too many requests in stack (" + str(len(lines)) + ")"
#				doit = False
#
#
#		except:
#			# assume the exception is associated with locking of the callstack
#			print "Netflix: FileLock encountered - retry"
#			doit = False
#			makeGetRequest(url, cookies, callstackpath, maxcalls)

	# map the folder that the request meter is held in
	# TODO: is there a way to automatically discover the user data folder rather than hard coding the plugin id?
	#callstackpath = xbmc.translatePath('special://profile/addon_data/plugin.video.avalon.netflix')
	# get path to the actual metering file
	#callstack = os.path.join(callstackpath, "callstack")

	callstack = callstackpath
	# do we need to check the call stack?
	print callstackpath
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
			if len(lines) <= int(maxcalls):
				doit=True
				print str(len(lines)) + "<=" + str(maxcalls) + " is " + str(len(lines) <= maxcalls)
			else:
				print 'too many requests in stack (' + str(len(lines)) + ')'
				doit=False


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

	return _doGetRequest(url, cookies, callstackpath, lines)

# Make an HTTP GET request using the provided cookies, checking the callstack, to ensure we don't get throttled
def makePostRequest(url, cookies, callstackpath, maxcalls, data):

	doit = False

	lines = []

	while not doit:
		try:
			if not os.path.exists(callstackpath):
				pass
			else:
				fh = open(callstackpath, 'r')
				lines = fh.read().split('\n')
				fh.close()

				for line in lines:
					try:
						if float(line) + 60 < time.time():
							lines.remove(line)
					except:
						pass

			fh = open(callstackpath, 'w')
			fh.write('\n'.join('\n'.join(lines).split()))
			fh.close()


			if len(lines) < int(maxcalls):
				doit = True
			else:
				print "Netflix: Too many requests in stack (" + str(len(lines)) + ")"


		except:
			# assume the exception is associated with locking of the callstack
			print "Netflix: FileLock encountered - retry"
			doit = false

	return _doPostRequest(url, cookies, callstackpath, lines, data)



def _doGetRequest(url, cookies, callstackpath, lines):
	#try:
	# add a timestamp to the metering file
	lines += (str(time.time()),)
	fh = open(callstackpath, 'w')
	fh.write('\n'.join('\n'.join(lines).split()))
	#fh.writelines(lines)
	fh.close()

	# make the request and return the response!!!
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
	return opener.open(url).read()
	#except Exception, Argument:
		#print "Netflix FileLock encountered - trying again "
		#return makeGetRequest(url, cookies, callstackpath, lines)

def _doPostRequest(url, cookies, callstackpath, lines, data):
	lines += (str(time.time()),)
	fh = open(callstackpath, 'w')
	fh.write('\n'.join('\n'.join(lines).split()))
	#fh.writelines(lines)
	fh.close()

	# make the request and return the response!!!
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
	return opener.open(url, data).read()
