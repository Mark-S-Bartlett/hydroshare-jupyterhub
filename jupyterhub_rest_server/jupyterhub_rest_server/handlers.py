import tornado.web
import os
import socket
import logging
import tornado.auth
import shutil
import ipgetter
from . import utilities

from tornado.log import enable_pretty_logging
enable_pretty_logging()

class RequestHandler(tornado.web.RequestHandler):
    def __init_(self):
        super(RequestHandler, self)

    def get_or_error(self, argname, strip=True):
        """
        This function gets a REST input argument or returns an error message if the argument is not found
        Arguments:
        argname -- the name of the argument to get
        strip -- indicates if the whitespace will be stripped from the argument
        """
        arg = self.get_argument(argname, default=None, strip=strip)
        if arg is None:
            self.write('<b>Encountered Error: </b> Could not find parameter "%s". <br> ' % argname)
            return 0
        return arg

class JupyterHandler(RequestHandler, tornado.auth.OAuth2Mixin):
    def get(self):
        resourcetype = self.get_or_error('resourcetype')
        resourceid = self.get_or_error('resourceid')
        husername = self.get_or_error('husername')

        # make all usernames lowercase
        username = husername.lower()
        resourcetype = resourcetype.lower()
	
        # build userspace
        utilities.build_userspace(username)
        utilities.set_hydroshare_args(husername, resourceid, resourcetype)
 
        # generate the redirect url
        baseurl = os.environ['JUPYTER_HUB_IP']
        port = os.environ['JUPYTER_PORT']
        
        # build the redirect url 
        url = "http://%s:%s/user/%s/tree/notebooks/Welcome.ipynb" % (baseurl,port, username)

        # save the next url to ensure that the redirect will work
        p = os.path.join(os.environ['HYDROSHARE_REDIRECT_COOKIE_PATH'], '.redirect_%s' % username)        
        with open(p, 'w') as f:
            f.write(url)

        # redirect to the desired page
        self.redirect(url, status=303)
