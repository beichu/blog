from google.appengine.ext import db

class Blog(db.Model): #google datastore entity
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required =True)
    created = db.DateTimeProperty(auto_now_add = True)
		


class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = False)
    registration_time = db.DateTimeProperty(auto_now_add = True)