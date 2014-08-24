import json
import datetime
from google.appengine.api import memcache
import webapp2
import jinja2
import os
from utils import time_sec, valid_user, valid_password, valid_verify, valid_email, make_pw_hash, match_pw, front_articles

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template) #parameter template is a file name
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))	

class Flush(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect('/')
class FrontPage(Handler):

    def render_front(self):
        self.render('front.html', blogs = front_articles(), 
                    time = time_sec(str(datetime.datetime.now() - memcache.get('start_time'))))
    def get(self):
        self.render_front()

class JsonFront(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; Charset=UTF-8'
        blogs = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC')
        j =[]
        for entry in blogs:
            entry_dict = {}
            entry_dict['subject'] = entry.subject
            entry_dict['content'] = entry.content
            entry_dict['created'] = str(entry.created)
            j.append(entry_dict)
        front_jsson = json.dumps(j) 
        self.write(front_jsson)
    
    
class NewPost(Handler):
    def get(self):
        self.render('newpost.html', subject='', content='', error='')
	
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if (subject and content):
            blog = Blog(subject = subject, content = content)
            blog.put()
            blog_id = blog.key().id()
            front_articles(True)
			
            self.redirect('/blog/%s' %str(blog_id))
        else:
            error = 'we need both a subject and some content!'
            self.render('newpost.html', subject = subject, error = error, content = content)

class BlogPost(Handler):
    def get(self, blog_id):
        subject = Blog.get_by_id(int(blog_id)).subject
        content = Blog.get_by_id(int(blog_id)).content
        self.render('blogpost.html', subject=subject, content=content, time = time_sec(str(datetime.datetime.now() - memcache.get('start_time'))))

class JsonBlogPost(Handler):
    def get(self, blog_id):
        self.response.headers['Content-Type'] = 'application/json; Charset=UTF-8'
        subject = Blog.get_by_id(int(blog_id)).subject
        content = Blog.get_by_id(int(blog_id)).content
        created = str(Blog.get_by_id(int(blog_id)).created)
        created = str(Blog.get_by_id(int(blog_id)).created)
        j = {}
        j['subject'] = subject
        j['content'] = content
        j['created'] = created
        entry_jsson = json.dumps(j)
        self.write(entry_jsson)


	

class Signup(Handler):

    def get(self):
        self.render('signup.html', username = '', password='', verify='', email='', error_username='', error_password='', error_verify='', error_email='')        
        
    def post(self):
        error_username = ''
        error_password = ''
        error_verify = ''
        error_email=''
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        
        if (valid_user(username) and valid_password(password) and valid_verify(verify,password)) and ((valid_email(email) or email=='')):
            user1 = db.GqlQuery('SELECT * FROM User WHERE username = :1', username)# see if username already exists
            user2 = db.GqlQuery('SELECT * FROM User WHERE email = :1', email)# see if email already exists
            if not (user1.get() and user2.get()):                     
                new_user = User(username = username, password = make_pw_hash(username, password), email = email)
                new_user.put()
                user_id = new_user.key().id()              
                self.response.headers.add_header('Set-Cookie', 'user_id = %s' %user_id)#set cookie
                self.redirect('/welcome')
            else:
                if user1.get():
			        error_username = 'Username already exists!'
                if user2.get():
                    error_email = 'Email already exists!'
                self.render('signup.html',username=username, password=password, verify=verify, email=email, error_username=error_username, error_password=error_password, error_verify=error_verify, error_email=error_email)					
                    
            
        else:
            if not valid_user(username):
			    error_username = "That's not a valid username!"
            if not valid_password(password):
                error_password = "That's not a valid password!"
            if not valid_verify(verify,password) or not(password and verify):
                error_verify = "Your passwords didn't match "
            if not (valid_email(email) or email == ''):
                error_email = "That's not a valid email!"
			
            self.render('signup.html', username=username, password=password, verify=verify, email=email, error_username=error_username, error_password=error_password, error_verify=error_verify, error_email=error_email)

        
class Login(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        error_login = ''
        username = self.request.get('username')
        password = self.request.get('password')
        user= db.GqlQuery('SELECT * FROM User WHERE username= :1', username)
        user_pw_hash = user.get().password
        user_id = user.get().key().id()
        if match_pw(username, password, user_pw_hash):
            self.response.headers.add_header('Set-Cookie', 'user_id = %s' % user_id)
            self.redirect('/welcome')
		            
class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie','user_id=; Path=/')
        self.redirect('/signup')
			
class Welcome(webapp2.RequestHandler):
    def get(self):
        user_id = self.request.cookies.get('user_id')
        if user_id:
            username =User.get_by_id(int(user_id)).username  		
            self.response.out.write('welcome, '+ username)
        else:
            self.redirect('/signup')		