import re
import urllib
import urllib2

import avalon_kodi_utils as utils


### make a GET request to the login page and determine the form value of the hidden "authURL" input element
def getAuth(cookies, callstackpath, maxcalls):

	# use utils to make the GET request
	response = utils.makeGetRequest("http://www.netflix.com/login", cookies, callstackpath, maxcalls)

	# find matches - should return <input type="hidden" name="authURL" value="[the_value]" /> instances
	match = re.compile('input.*?authURL.*?value="(.*?)"', re.DOTALL).findall(str(response))

	# use the last instance found (there should only be one anyway...)
	auth = ""
	for found in match:
		auth = found

	# return the found token
	return auth


def checkLogin(cookies, callstackpath, maxcalls):
	try:
		response = utils.makeGetRequest("https://www.netflix.com/Login", cookies, callstackpath, maxcalls)
		if 'id="page-LOGIN"' in response:
			return False
		else:
			return True
	except:
		return False


def login(username, password, cookies, callstackpath, maxcalls):

	# only login if the cookies aren't valid
	if not checkLogin(cookies, callstackpath, maxcalls):
		postdata = {'email': username, 'password': password, 'authURL': getAuth(cookies, callstackpath, maxcalls), 'RememberMe': 'on' }
		data = urllib.urlencode(postdata)
		#opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler(debuglevel=1), urllib2.HTTPCookieProcessor(cookiejar))
		#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
		#opener.addheaders = http_headers

		print urllib.urlencode(postdata)

		# make the request, but don't do anything with it, we're only interested in the cookies!!!
		#response = opener.open("https://signup.netflix.com/login", str('email='+urllib.quote_plus(username) + "&password=" + urllib.quote_plus(password) + "&authURL=" + urllib.quote_plus(getAuth())).encode('utf-8')).read()
		try:
			response = utils.makePostRequest("https://www.netflix.com/Login?locale=en-GB", cookies, callstackpath, maxcalls, data)
		except:
			pass


		return checkLogin(cookies, callstackpath, maxcalls)
	else:
		return checkLogin(cookies, callstackpath, maxcalls)
