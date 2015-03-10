import os
import time
import urllib2
import xbmc
import xbmcvfs
import time

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

	if((now - maxage) > (age)):
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

	return s


# Make an HTTP GET request using the provided cookies, checking the callstack, to ensure we don't get throttled
def makeGetRequest(url, cookies, callstackpath, maxcalls):


	callstack = callstackpath

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
			else:
				print 'Netflix: Too many requests in stack (' + str(len(lines)) + ')'
				doit=False


			# read the lines
			for line in lines:
				try:
					# check if the timestamp of the row is older than a minute
					if float(line) + 60 <  time.time():
						lines.remove(line) # remove old lines

					# update the metering file

				except:
					pass

			fh = open(callstack, 'w')
			fh.write('\n'.join('\n'.join(lines).split()))
			fh.close()



		except Exception, Argumnent:
			print "Netflix: FileLock encountered - trying again"
			pass

		time.sleep(1)

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


		time.sleep(1)

	return _doPostRequest(url, cookies, callstackpath, lines, data)



def _doGetRequest(url, cookies, callstackpath, lines):
	try:
		# add a timestamp to the metering file
		lines += (str(time.time()),)
		fh = open(callstackpath, 'w')
		fh.write('\n'.join('\n'.join(lines).split()))
		#fh.writelines(lines)
		fh.close()
	except:
		time.sleep(1)
		_doGetRequest(url, cookies, callstackpath, lines)

	# make the request and return the response!!!
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
	opener.addheaders = [("Accept-Language", "en-US,en;q=0.5"),  ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"), ("Connection", "keep-alive")]
	return opener.open(url).read()


def _doPostRequest(url, cookies, callstackpath, lines, data):
	lines += (str(time.time()),)
	fh = open(callstackpath, 'w')
	fh.write('\n'.join('\n'.join(lines).split()))
	fh.close()

	# make the request and return the response!!!
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
	return opener.open(url, data).read()
