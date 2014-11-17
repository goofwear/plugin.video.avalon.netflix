######################################################################
# netflix_interop_auth.py                                            #
######################################################################
# Author:   Iamdixon (avalonprojects.net)                            #
# Date:     2014-10-28                                               #
######################################################################
# helper functions to make Netflix login requests and retrieve       #
# cookies for use in subsequent requestsself.                        #
#                                                                    #
# maintains compatibility with current versions of XBMC/Kodi.        #
######################################################################

import cookielib
import re
import urllib
import urllib2

# global cookiejar to handle persistance for authentication
cookiejar = cookielib.MozillaCookieJar()

### make a GET request to the login page and determine the form value of the hidden "authURL" input element
def getAuth():

    # build an opener using the global cookiejar
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    response = opener.open("https://signup.netflix.com/login").read()
    
    # find matches - should return <input type="hidden" name="authURL" value="[the_value]" /> instances
    match = re.compile('input.*?authURL.*?value="(.*?)"', re.DOTALL).findall(str(response))

    auth = "";

    # use the last instance found (there should only be one anyway...)
    for found in match:
        auth = found

    # return the found token!!
    return auth


### make a POST request to the login page passing along username (email), password and "authURL"
def login(username, password):

    # build an opener using the global cookiejar
    #http_headers = [("User-Agent","Mozilla/4.0 (compatible; MSIE 5.5;Windows NT)")]

    #proxy_support = urllib2.ProxyHandler({})
    #opener = urllib2.build_opener(proxy_support)
    #urllib2.install_opener(opener)


    postdata = { 'email': username, 'password': password, 'authURL' : getAuth() }
    data = urllib.urlencode(postdata)

    #opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler(debuglevel=1), urllib2.HTTPCookieProcessor(cookiejar))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    #opener.addheaders = http_headers

    print urllib.urlencode(postdata)

    # make the request, but don't do anything with it, we're only interested in the cookies!!!
    #response = opener.open("https://signup.netflix.com/login", str('email='+urllib.quote_plus(username) + "&password=" + urllib.quote_plus(password) + "&authURL=" + urllib.quote_plus(getAuth())).encode('utf-8')).read()
    try:
        response = opener.open("https://www.netflix.com/Login?locale=en-GB", data)
    except:
        pass


#dualstack.wwwservice--frontend-san-428817943.eu-west-1.elb.amazonaws.com