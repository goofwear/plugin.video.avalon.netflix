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
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

    # make the request, but don't do anything with it, we're only interested in the cookies!!!
    response = opener.open("https://signup.netflix.com/login", str('email='+urllib.quote_plus(username) + "&password=" + urllib.quote_plus(password) + "&authURL=" + urllib.quote_plus(getAuth())).encode('utf-8')).read()


