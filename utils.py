import random
import re
import hashlib
import string
import datetime
from google.appengine.api import memcache
from google.appengine.ext import db

#convert "00:00:00" time format into seconds
def time_sec(time_str):
    time_list = time_str.split(':')
    return int(time_list[0])*3600 + int(time_list[1])*60 + float(time_list[2])
    
#check if a username only contains valid characters
def valid_user(username):
    username_re = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
    return username_re.match(username)
    
#check if a password or email only contains valid characters, and if verify matches email
def valid_password(password):
    password_re = re.compile(r'^.{3,20}')
    return password_re.match(password)
def valid_verify(verify, password):
    return verify == password
def valid_email(email):
    email_re = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return email_re.match(email)

#make a string that contains 5 letters 
def make_salt():
    salt = ''
    for i in range(0, 5):
        salt = salt + random.choice(string.ascii_letters)
    return salt

#make a hash of the password, and attach a radom 5 letter string to it  
def make_pw_hash(username, password):
    salt = make_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return '%s|%s' %(h, salt)

def match_pw(username, password, h):
    salt = h[h.find('|') + 1 : ]
    test_hash = hashlib.sha256(username + password + salt).hexdigest() + '|' + salt
    return test_hash == h

def front_articles(update = False):
    key = 'front'
    
    blogs = memcache.get(key)
    if blogs is None or update:
        blogs = list(db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC'))
        memcache.set(key, blogs)    
        memcache.set('start_time', datetime.datetime.now())    
    return blogs