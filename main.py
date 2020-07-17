from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from _datetime import datetime
import json
from flask_mail import Mail
import os
import math

with open("config.json", 'r') as c:
    params=json.load(c)["parameter"]
app=Flask(__name__)
app.secret_key = 'hrithik secret key'
app.config['UPLOAD_FOLDER']=params['uploader']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',   #To Send Email To Our Email Id We use smtp server
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['user_id'],
    MAIL_PASSWORD=params['user_pass']
)

mail=Mail(app)
if(params['local_server']):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)
#class File(db.Model):
 #   data=db.column(db.LargeBinary)
class Contact(db.Model):
    '''
    sno,name,phone_num,msg,data,email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)   #nullable=flase means it is compulsary to fill this field
    phone_num = db.Column(db.String(12), unique=False, nullable=False)
    msg = db.Column(db.String(120), unique=False, nullable=False)  #if nullable=true then we can leave this field empty
    date = db.Column(db.String(12), unique=False, nullable=True)   #In db it automatically take current time
    email = db.Column(db.String(20), unique=False, nullable=False)
class Posts(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80), nullable=False)
    slug=db.Column(db.String(21),nullable=False)
    content=db.Column(db.String(200), nullable=False)
    date=db.Column(db.String(12),nullable=True)
    img_file = db.Column(db.String(12), nullable=False)
@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    last = math.floor(len(posts)/int(params['no_of_post']))
    #[0:params['no_of_post']]
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts=posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    if(page==1):
        prev = "#"
        next = "/?page=" + str(page+1)
    elif(page==last):
        prev="/?page=" + str(page-1)
        next="#"
    else:
        prev="/?page=" + str(page-1)
        next="/?page=" + str(page+1)
    return render_template('index.html',p=params,posts=posts,prev=prev,next=next)
@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html', p=params)
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user']==params['a_user']):
        postss = Posts.query.all()
        return render_template('dashboard.html',p=params,posts=postss)
    if request.method=='POST':
        username=request.form['email']
        userpassword=request.form.get('password')
        if(username==params['a_user'] and userpassword==params['a_pass']):
            #set session for user
            session['user']=username
            postss = Posts.query.all()
            return render_template('dashboard.html', p=params, posts=postss)
    return render_template('login.html', p=params)
@app.route('/contact',methods=['GET','POST'])    #By GET we can fetch(or request) image or url from server
def contact():
    if (request.method=='POST'):                   #POST is used to add entry in database
        '''Add Entry To Database'''
        name=request.form.get('name')
        phone=request.form.get('phone')
        message=request.form.get('message')
        email=request.form.get('email')
        entry = Contact(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('The Contact Info By' + name,  #Subject of  email
                          sender=email,                   #senders email id
                          recipients=[params['user_id']], #List of email ids to send email
                          body=message + '\n' +phone+"\n Email-Id="+email)     #content of the mail
    return render_template('contact.html', p=params)
@app.route('/post/<string:post_slug>',methods=['GET'])
def posts(post_slug):
    pp=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',p=params,p_fetch=pp)
@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']==params['a_user']):
        if request.method=='POST':
            box_title=request.form.get('title')
            box_slug= request.form.get('slug')
            box_content = request.form.get('content')
            box_img = request.form.get('img_file')
            if sno=='0':
                post=Posts(title=box_title,slug=box_slug,content=box_content,date=datetime.now(),img_file=box_img)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=box_slug
                post.content=box_content
                post.img_file=box_img
                post.date=datetime.now()
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',p=params,post=post)
@app.route("/logout")
def logout():
    session.pop('user')
    return  redirect("/dashboard")
@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['a_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return  redirect("/dashboard")
@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if('user' in session and session['user']==params['a_user']):
        if(request.method=='POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded Successfully"

app.run(debug=True)