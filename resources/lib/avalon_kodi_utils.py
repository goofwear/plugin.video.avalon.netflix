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

			try:
				fh = open(callstackpath, 'w')
				fh.write('\n'.join('\n'.join(lines).split()))
				fh.close()
			except:
				makeGetRequest(url, cookies, callstackpath, maxcalls)

			if len(lines) < maxcalls:
				doit = True
			else:
				print "Netflix: Too many requests in stack (" + str(len(lines)) + ")"


		except:
			# assume the exception is associated with locking of the callstack
			print "Netflix: FileLock encountered - retry"

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

			if len(lines) < maxcalls:
				doit = True
			else:
				print "Netflix: Too many requests in stack (" + str(len(lines)) + ")"


		except:
			# assume the exception is associated with locking of the callstack
			print "Netflix: FileLock encountered - retry"

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
