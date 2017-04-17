import os
import webapp2
import jinja2
import time
import hmac
import re
import random
import string
import hashlib

#gp utils

template_dir = os.path.join(os.path.dirname(__file__), 'templates')             #jinja-html templates directory
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),  
    autoescape = True)

class Handler(webapp2.RequestHandler):
    """
    """

    def write(self, *argva, **argvb):
        self.response.out.write(*argva, **argvb)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **argvb):
        self.write(self.render_str(template, **argvb))



"""
Security utils
"""

SECRET = "koRTOfxD4rfPtyQWSalf0823lkjnm"  #key for hmac

def make_salt():
    """Makes salt randomly generated from letters.

    Returns:
        Salt: A five letter string
    """
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, password, salt):
    """Makes password & username hash with salt.
    Args:
        name: User name.
        password: User password.
        salt: A salt.

    Returns:
        A tuple: hash (hexadecimal digits), salt.
    """
    result_hash = hashlib.sha256(name + password + salt).hexdigest()
    return '%s|%s' % (result_hash, salt)

def valid_pw(name, password, h):
    """Validates username and password against hash.
    Args:
        name: User name.
        password: User password.
        h: A tuple hash, salt.

    Returns:
        True if name & password matches hash.
    """
    new_hash = make_pw_hash(name,password,h.split('|')[1])
    if new_hash == h:
        return True

def hmac_str(s):
	return hmac.new(SECRET,s).hexdigest()

def make_hmac_str(s):
	return "%s|%s" % (s,hmac_str(s))

def check_hmac_str(s):
	orig = s.split('|')[0]
	if s == make_hmac_str(orig):
		return orig
