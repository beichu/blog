import jinja2
import webapp2
import datetime
from utils import time_sec, valid_user, valid_password, valid_verify, valid_email, make_pw_hash, match_pw, front_articles
from handlers import FrontPage, NewPost, Flush, BlogPost, Signup, Welcome, Login, Logout, JsonBlogPost, JsonFront
from db import Blog, User




		

    
app = webapp2.WSGIApplication([('/', FrontPage),('/newpost', NewPost), 
                               ('/flush', Flush),('/blog/([0-9]+)', BlogPost),
                               ('/blog/([0-9]+).json', JsonBlogPost),('/.json', JsonFront),
                               ('/signup', Signup), ('/welcome', Welcome),
                               ('/login', Login),('/logout', Logout)], debug = True)
