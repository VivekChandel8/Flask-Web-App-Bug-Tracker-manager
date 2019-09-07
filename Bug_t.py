from flask import Flask, render_template, request, flash, session, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from conf_admin import username, password
import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

#It is a table for storing data of bugs
class Bugs(db.Model):
   id = db.Column('bug_id', db.Integer, primary_key = True)
   assign = db.Column(db.String(50))
   Status = db.Column(db.String(50))
   Severity = db.Column(db.String(50))
   Title = db.Column(db.String(100))
   Writedescription = db.Column(db.String(2000))
   project = db.Column(db.String(100))
   timenow = db.Column(db.String(100))
   postedby = db.Column(db.String(100))
   path = db.Column(db.String(100))
   def __init__(self, assign, Status, Severity,Title,Writedescription,project,timenow,postedby,path):
       self.assign = assign
       self.Status = Status
       self.Severity = Severity
       self. Title = Title
       self.Writedescription = Writedescription
       self.project = project
       self.timenow = timenow
       self.postedby = postedby
       self.path = path

#It is a table for storing data of users
class Addu(db.Model):
   uid = db.Column('user_id', db.Integer, primary_key = True)
   uname = db.Column(db.String(50))
   Email = db.Column(db.String(120))
   Passwrd = db.Column(db.String(23))
   status = db.Column(db.String(40))

   def __init__(self, uname, Email,Passwrd, status="enabled"):
       self.uname = uname
       self.Email = Email
       self.Passwrd = Passwrd
       self.status = status


#adding bug to database
@app.route('/addbug', methods=['POST'])
def addbug(size=6, chars=string.ascii_uppercase + string.digits):
    somerstring = ''.join(random.choice(chars) for _ in range(size))
    now = str(datetime.datetime.now())
    pname = request.form['project'] + somerstring
    # target = '\\BUG_TRACKER_T\\Bug Data\\'+pname
    cwd = os.path.dirname(os.path.realpath(__file__))#current working directory
    target = os.path.join( cwd, 'Bug Data', pname)
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)

    saddress = []
    for f in request.files.getlist('file[]'):
        filename = secure_filename(f.filename)
        app.config['UPLOAD_FOLDER'] = target
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        saddress.append('Bug data/'+ pname +'/'+ f.filename.replace(' ','_')+';')
    Address = ''.join(saddress)
    if request.method == 'POST':
        if not request.form['Status'] or not request.form['Assignto'] or not request.form['Severity'] or not request.form['Title']  or not request.form['Writedescription'] or not request.form['project'] or not now:
            flash('Please enter all the fields', 'error')
        else:
           Save = Bugs(request.form['Assignto'],request.form['Status'],
                               request.form['Severity'], request.form['Title'], request.form['Writedescription'],request.form['project'],now,request.form['postedby'],Address)
           flash('Bug saved, Fill the form again if you want to enter a new bug')
           db.session.add(Save)
           db.session.commit()
    if 'admin' in session:
        return redirect('/postasadmin')
    else:
        return redirect('/postasuser')

#adminloginpage
@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')

#function to authonicate admin
@app.route('/authonticate', methods=['POST'])
def logincheck():
    user = request.form['uname']
    pwrd = request.form['pass']
    session['admin']=user
    if username==user and pwrd==password:
     return redirect("/adminpanel")
    else:
        flash("Invalid username or password.. Please enter a valid user name and password")
        return redirect("/adminlogin")

#function for loggin out admin
@app.route('/logout', methods=['POST'])
def logout():
    del(session['admin'])
    flash('You were logged out, Thank you admin !!!')
    return redirect("/adminlogin")

# decorater for admin required pages
def login_required_admin(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if 'admin' in session:
            return test(*args,**kwargs)
        else:
            flash('You need to login first')
            return redirect("/adminlogin")
    return wrap

#decorater for user required pages
def login_required_user(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if 'user' in session:
            return test(*args,**kwargs)
        else:
            flash('You need to login first')
            return redirect("/userlogin")
    return wrap

#viewing bug as admin
@app.route('/bugpage')
@login_required_admin
def BugpageA():
    data = Bugs.query.all()
    sortedbugsa=[]
    print(session['admin'])
    for i in reversed(data):
        sortedbugsa.append(i)
    return render_template('index admin.html',data=sortedbugsa)

#adding user by admin
@app.route('/adduser')
@login_required_admin
def adduserpage():
    return render_template('adduser.html')

#adminpanelpage
@app.route('/adminpanel')
@login_required_admin
def adminpanel():
    return render_template('Admin.html')

#Bug viewing page for user
@app.route('/Bugs')
@login_required_user
def Bugpage():
    assigned = session['user']
    data = Bugs.query.filter_by(assign = assigned).all()
    sortedbugs =[]
    for i in reversed(data):
        sortedbugs.append(i)
    return render_template('index.html',data=data)


#posting bug as admin
@app.route('/postasadmin')
@login_required_admin
def bugtrackerA():
    ar = Addu.query.all()
    return  render_template('Bug_tracker_admin.html',data=ar)

#posting bug as user
@app.route('/postasuser')
@login_required_user
def bugtracker():
    ar = Addu.query.all()
    return  render_template('Bug_tracker.html',data=ar)

#adding user to database
@app.route('/addinguser', methods=['POST'])
def addinguser():
    if request.method == 'POST':
      addnew = Addu(request.form['uname'], request.form['email'], request.form['psw'],)
      db.session.add(addnew)
      db.session.commit()
      flash('User added successfully, fill form again to add new one')
    return redirect("/adduser")

#user login page
@app.route('/userlogin')
def userlogin():
    return render_template('userlogin.html')

#function for authonicate user
@app.route('/usercheck', methods=['POST'])
def usercheck():
    uname = request.form['uname']
    passrd = request.form['pass']
    check = Addu.query.filter_by(uname=uname, Passwrd=passrd, status="enabled").all()
    session['user'] = uname

    if(len(check) == 0):
        flash('Your are entering wrong user name or password or Your account has been disabled')
        return redirect('/userlogin')
    else:
        return redirect('/Bugs')

#deleting user as admin page
@app.route('/removeuser')
@login_required_admin
def removeuser():
    userdata = Addu.query.all()
    sorteduser = []
    for i in reversed(userdata):
        sorteduser.append(i)
    return render_template("userdata.html",data=sorteduser)

#function for deleting user
@app.route('/deleteuser', methods=['POST'])
def deluser():
    if request.method == 'POST':
     duser = request.form['hiddendata']
     Addu.query.filter_by(uid=duser).delete()
     db.session.commit()
     return redirect('/removeuser')

#setting permission page for admin
@app.route('/permission')
@login_required_admin
def permission():
    permission = Addu.query.all()
    sortedpermission = []
    for i in reversed(permission):
        sortedpermission.append(i)
    return render_template("permission.html",data=sortedpermission)

#function for setting permissions
@app.route('/changepermission', methods=['POST'])
def changepermission():
    if request.method == 'POST':
        match = request.form['hiddendata']
        ed = request.form['getdata']
        Addu.query.filter_by(uid=match).update(dict(status=ed))
        db.session.commit()
        return redirect('/permission')


#function for userlogout
@app.route('/logoutuser', methods=['POST'])
def logoutU():
    del(session['user'])
    flash('You were logged out, Thank you user !!!')
    return redirect("/userlogin")

#view bug
@app.route('/viewbugdes', methods=['POST'])
@login_required_admin
def viewbugdes():
    if request.method == 'POST':
        dmatch = request.form['check']
        rat =Bugs.query.filter_by(id=dmatch)
        for u in rat:
            earl = u.path
            ragnar = earl.split(';')
            lagretha = []
            fname = []
            for k in ragnar:
                lagretha.append(k)
                fname.append(k)
            lagretha = filter(None, lagretha)
            fname = filter(None, fname)

            for i in fname:

              filed = []
              j = i.split('/')
              filed.append(j[2])

    return render_template("viewbug.html", duck=rat, data= zip(lagretha,filed))


@app.route('/viewbugdesu', methods=['POST'])
@login_required_user
def viewbugdesu():
    if request.method == 'POST':
        dmatch = request.form['check']
        rat =Bugs.query.filter_by(id=dmatch)
        for u in rat:
            earl = u.path
            ragnar = earl.split(';')
            lagretha = []
            fname=[]
            for k in ragnar:
                lagretha.append(k)
                fname.append(k)
            lagretha = filter(None, lagretha)
            fname = filter(None, fname)
            filed = []

            for i in fname:

              j = i.split('/')
              filed.append(j[2])
    return render_template("viewbugsuser.html", duck=rat, data= zip(lagretha,filed))

@app.route('/returnfile', methods=['POST'])
def returnfile():
    cad = request.form['choco']
    return send_file(cad,as_attachment=True)

@app.route('/')
def home():
    return render_template("Home.html")


if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)