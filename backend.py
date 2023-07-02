# importing the dependencies
from flask import Flask, render_template, send_file, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import pymysql
import json
import os
import ast

# loading the environment variables 
load_dotenv('.env')
USERNAME = os.environ['USER_NAME']
PASSWORD = os.environ['PASSWORD']
FULLNAME = os.environ['FULLNAME']

pymysql.install_as_MySQLdb()

# calling the configuration file
with open('config.json', 'r') as file:
    params = json.load(file)['params']
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = params['uri']

# creating the database models
app.secret_key = os.environ['SECRET_KEY']
db = SQLAlchemy(app)

class Skill(db.Model):
    name = db.Column(db.String, primary_key=True)
    priority = db.Column(db.Integer)

class Education(db.Model):
    courseid = db.Column(db.Integer, primary_key=True)
    coursetitle = db.Column(db.String)
    commence = db.Column(db.String)
    completion = db.Column(db.String)
    institute = db.Column(db.String)
    markstype = db.Column(db.String)
    marks = db.Column(db.Float)
    info = db.Column(db.String)

class Project(db.Model):
    title = db.Column(db.String)
    priority = db.Column(db.Integer)
    overview = db.Column(db.String)
    features = db.Column(db.String)
    stub = db.Column(db.String, primary_key=True)
    ghlink = db.Column(db.String)
    imgpath = db.Column(db.String)

class Dissertation(db.Model):
    title = db.Column(db.String)
    stub = db.Column(db.String, primary_key=True)
    supervisor = db.Column(db.String)
    duringcourse = db.Column(db.String)
    institute = db.Column(db.String)
    imgpath = db.Column(db.String)
    ghlink = db.Column(db.String)
    overview = db.Column(db.String)

@app.route('/')
def index():
    '''functionality of the index page'''
    skills = Skill.query.order_by(Skill.priority).all()
    courses = Education.query.order_by(Education.courseid.desc()).all()
    projects = Project.query.order_by(Project.priority).all()
    dissertations = Dissertation.query.all()
    for course in courses:
        course.info = ast.literal_eval(course.info)
    return render_template('index.html', 
                           params=params, 
                           skills=skills,
                           courses=courses,
                           projects=projects,
                           dissertations=dissertations)

@app.route('/project/<string:stub>')
def project(stub):
    '''functionality of the project page, it shows details of the selected project'''
    project = Project.query.filter(Project.stub == stub).first()
    project.overview = ast.literal_eval(project.overview)
    project.features = ast.literal_eval(project.features)
    return render_template('project.html',
                    params=params,
                    project=project)

@app.route('/dissertation/<string:stub>')
def diss(stub):
    '''functionality of the dissertation page, it shows details of the selected dissertaion'''
    dissertation = Dissertation.query.filter(Dissertation.stub == stub).first()
    dissertation.overview = ast.literal_eval(dissertation.overview)
    return render_template('dissertation.html',
                    params=params,
                    dissertation=dissertation)

@app.route('/download')
def download_resume():
    '''functionality to download the resume'''
    file_url = 'static/resume.pdf'
    return send_file(file_url, as_attachment=True)

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    '''functionality to log in the admin to get in the admin panel, if logged in, directly enter into the admin page'''
    if 'user' in session and session['user'] == USERNAME:
        return redirect('/adminpanel')
    else:
        if request.method == 'POST':
            uname = request.form.get('username')
            password = request.form.get('password')
            if uname == USERNAME and password == PASSWORD:
                session['user'] = uname
                return redirect('/adminpanel')
            else:
                return render_template('login.html', params=params, showalert=True)
        return render_template('login.html', params=params, showalert=False)
    
@app.route('/adminpanel', methods=['GET', 'POST'])
def adminpanel():
    '''admin panel functionality, if not logged in redirect to admin login page'''
    if 'user' in session and session['user'] == USERNAME:
        skills = Skill.query.order_by(Skill.priority).all()
        projects = Project.query.order_by(Project.priority).all()
        dissertations = Dissertation.query.all()
        courses = Education.query.all()
        if request.method == 'POST':
            dpinput = request.files.get('dpinput')
            resumeinput = request.files.get('resumeinput')

            if dpinput.filename != '':
                dpinput.save('./static/images/Dp.jpg')

            if resumeinput.filename != '':
                resumeinput.save('./static/resume.pdf')

            return redirect('/adminpanel')

        return render_template('adminpanel.html', 
                               params=params, 
                               user=FULLNAME,
                               skills=skills,
                               projects=projects,
                               courses=courses,
                               dissertations=dissertations)
    else:
        return redirect('/adminlogin')

@app.route('/adminpanel/editproject/<string:stub>', methods=['GET', 'POST'])
def edit_project(stub):
    '''edit and delete project detail and images'''
    if 'user' in session and session['user'] == USERNAME:
        project = Project.query.filter(Project.stub==stub).first()
        project.overview = '\n\n'.join(ast.literal_eval(project.overview))
        project.features = '\n\n'.join(ast.literal_eval(project.features))

        if request.method == "POST":
            title = request.form.get('title')
            priority = request.form.get('priority')
            stub = request.form.get('stub')
            imgpath = request.form.get('imgpath')
            ghlink = request.form.get('ghlink')
            overview = request.form.get('overview')
            features = request.form.get('features')
            imginput = request.files.get('imginput')

            if imginput.filename != '':
                imginput.save(os.path.join(params["upload_folder_loc"], secure_filename(imgpath)))

            overview = str(overview.split('\r\n\r\n'))
            features = str(features.split('\r\n\r\n'))

            project.title = title
            project.priority = priority
            project.stub = stub
            project.imgpath = imgpath
            project.ghlink = ghlink
            project.overview = overview
            project.features = features

            db.session.merge(project)
            db.session.commit()

            return redirect('/adminpanel')
        return render_template('editoraddproject.html', 
                               params=params,
                               action='Edit',
                               stub=stub,
                               user=FULLNAME,
                               project=project)
    else:
        return redirect('/adminlogin')

@app.route('/adminpanel/addproject', methods=["GET", "POST"])
def add_project():
    '''add a new project functionality'''
    if 'user' in session and session['user'] == USERNAME:
        if request.method == 'POST':
            title = request.form.get('title')
            priority = request.form.get('priority')
            stub = request.form.get('stub')
            imgpath = request.form.get('imgpath')
            ghlink = request.form.get('ghlink')
            overview = request.form.get('overview')
            features = request.form.get('features')
            imginput = request.files.get('imginput')

            if imginput.filename != '':
                imginput.save(os.path.join(params["upload_folder_loc"], secure_filename(imgpath)))

            overview = str(overview.split('\r\n\r\n'))
            features = str(features.split('\r\n\r\n'))

            proj_insert = Project(title=title,
                                  priority=priority, 
                                  overview=overview,
                                  features=features,
                                  stub=stub,
                                  ghlink=ghlink,
                                  imgpath=imgpath)
            
            db.session.add(proj_insert)
            db.session.commit()
            return redirect('/adminpanel')

        return render_template('editoraddproject.html', 
                           params=params,
                           action='Add',
                           user=FULLNAME)
    else:
        return redirect('/adminlogin') 

@app.route('/deleteproject/<string:stub>')
def delete_project(stub):
    '''delete the project and related images'''
    if 'user' in session and session['user'] == USERNAME:
        del_proj = Project.query.filter(Project.stub == stub).first()

        img_path = os.path.join(params["upload_folder_loc"], del_proj.imgpath)
        
        if img_path != params['upload_folder_loc'] and os.path.exists(img_path):
            os.remove(img_path)

        db.session.delete(del_proj)
        db.session.commit()

        return redirect('/adminpanel')
    else:
        return redirect('/adminlogin')

@app.route('/adminpanel/editdissertation/<string:stub>', methods=['GET', 'POST'])
def edit_diss(stub):
    '''edit and delete dissertation detail and images'''
    if 'user' in session and session['user'] == USERNAME:
        dissertation = Dissertation.query.filter(Dissertation.stub==stub).first()
        dissertation.overview = '\n\n'.join(ast.literal_eval(dissertation.overview))

        if request.method == "POST":
            title = request.form.get('title')
            stub = request.form.get('stub')
            supervisor = request.form.get('supervisor')
            duringcourse = request.form.get('during_course')
            institute = request.form.get('institute')
            imgpath = request.form.get('imgpath')
            imginput = request.files.get('imginput')
            ghlink = request.form.get('ghlink')
            overview = request.form.get('overview')

            overview = str(overview.split('\r\n\r\n'))

            if imginput.filename != '':
                imginput.save(os.path.join(params["upload_folder_loc"], secure_filename(imgpath)))


            dissertation.title = title
            dissertation.stub = stub
            dissertation.supervisor = supervisor
            dissertation.duringcourse = duringcourse
            dissertation.institute = institute
            dissertation.imgpath = imgpath
            dissertation.ghlink = ghlink
            dissertation.overview = overview

            db.session.merge(dissertation)
            db.session.commit()

            return redirect('/adminpanel')
        return render_template('editoradddiss.html', 
                               params=params,
                               action='Edit',
                               stub=stub,
                               user=FULLNAME,
                               diss=dissertation)
    else:
        return redirect('/adminlogin')
    
@app.route('/adminpanel/adddissertation', methods=["GET", "POST"])
def add_diss():
    '''add a new dissertation functionality'''
    if 'user' in session and session['user'] == USERNAME:
        if request.method == 'POST':
            title = request.form.get('title')
            stub = request.form.get('stub')
            supervisor = request.form.get('supervisor')
            during_course = request.form.get('during_course')
            institute = request.form.get('institute')
            imgpath = request.form.get('imgpath')
            imginput = request.files.get('imginput')
            ghlink = request.form.get('ghlink')
            overview = request.form.get('overview')

            overview = str(overview.split('\r\n\r\n'))

            if imginput.filename != '':
                imginput.save(os.path.join(params["upload_folder_loc"], secure_filename(imgpath)))

            diss_insert = Dissertation(title=title, 
                                  supervisor=supervisor,
                                  duringcourse=during_course,
                                  institute=institute,
                                  imgpath=imgpath,
                                  ghlink=ghlink,
                                  overview=overview,
                                  stub=stub)
            
            db.session.add(diss_insert)
            db.session.commit()
            return redirect('/adminpanel')

        return render_template('editoradddiss.html', 
                           params=params,
                           action='Add',
                           user=FULLNAME)
    else:
        return redirect('/adminlogin') 

@app.route('/deletedissertation/<string:stub>')
def delete_diss(stub):
    '''delete the dissertation and related images'''
    if 'user' in session and session['user'] == USERNAME:
        del_diss = Dissertation.query.filter(Dissertation.stub == stub).first()

        img_path = os.path.join(params["upload_folder_loc"], del_diss.imgpath)

        if img_path != params['upload_folder_loc'] and os.path.exists(img_path):
            os.remove(img_path)

        db.session.delete(del_diss)
        db.session.commit()

        return redirect('/adminpanel')
    else:
        return redirect('/adminlogin')

@app.route('/adminpanel/editcourse/<string:coursename>', methods=['GET', 'POST'])
def edit_course(coursename):
    '''edit and delete course detail'''
    if 'user' in session and session['user'] == USERNAME:
        course = Education.query.filter(Education.coursetitle==coursename).first()
        course.info = '\n\n'.join(ast.literal_eval(course.info))

        if request.method == "POST":
            courseid = request.form.get('courseid')
            coursetitle = request.form.get('coursetitle')
            commence = request.form.get('commence')
            completion = request.form.get('completion')
            institute = request.form.get('institute')
            markstype = request.form.get('markstype')
            marks = request.form.get('marks')
            info = request.form.get('info')

            if info is not None:
                info = str(info.split('\r\n\r\n'))
            else:
                info = str([])

            course.courseid = courseid
            course.coursetitle = coursetitle
            course.commence = commence
            course.completion = completion
            course.institute = institute
            course.markstype = markstype
            course.marks = marks
            course.info = info

            db.session.merge(course)
            db.session.commit()

            return redirect('/adminpanel')
        return render_template('editoraddcourse.html', 
                               params=params,
                               action='Edit',
                               coursename=coursename,
                               user=FULLNAME,
                               course=course)
    else:
        return redirect('/adminlogin')

@app.route('/adminpanel/addcourse', methods=["GET", "POST"])
def add_course():
    '''add a new course functionality'''
    if 'user' in session and session['user'] == USERNAME:
        if request.method == 'POST':
            courseid = request.form.get('courseid')
            coursetitle = request.form.get('coursetitle')
            commence = request.form.get('commence')
            completion = request.form.get('completion')
            institute = request.form.get('institute')
            markstype = request.form.get('markstype')
            marks = request.form.get('marks')
            info = request.form.get('info')

            if info is not None:
                info = str(info.split('\r\n\r\n'))
            else:
                info = str([])

            course_insert = Education(courseid=courseid,
                                      coursetitle=coursetitle,
                                      commence=commence,
                                      completion=completion,
                                      institute=institute,
                                      markstype=markstype,
                                      marks=marks,
                                      info=info)
            
            db.session.add(course_insert)
            db.session.commit()
            return redirect('/adminpanel')

        return render_template('editoraddcourse.html', 
                           params=params,
                           action='Add',
                           user=FULLNAME)
    else:
        return redirect('/adminlogin') 

@app.route('/deletecourse/<string:coursename>')
def delete_course(coursename):
    '''delete the course'''
    if 'user' in session and session['user'] == USERNAME:
        del_course = Education.query.filter(Education.coursetitle == coursename).first()

        db.session.delete(del_course)
        db.session.commit()

        return redirect('/adminpanel')
    else:
        return redirect('/adminlogin')
    
@app.route('/adminpanel/addskill', methods=['GET', 'POST'])
def add_skill():
    '''add a new skill functionality'''
    if 'user' in session and session['user'] == USERNAME:
        if request.method == 'POST':
            name = request.form.get('name')
            priority = request.form.get('priority')

            skill_insert = Skill(name=name,
                                 priority=priority)
            
            db.session.add(skill_insert)
            db.session.commit()
            return redirect('/adminpanel')
        
        return render_template('editoraddskill.html',
                               params=params,
                               user=FULLNAME)
    else:
        return redirect('/adminlogin')

@app.route('/deleteskill/<string:skillname>')
def delete_skill(skillname):
    '''delete the skill'''
    if 'user' in session and session['user'] == USERNAME:
        del_skill = Skill.query.filter(Skill.name == skillname).first()

        db.session.delete(del_skill)
        db.session.commit()

        return redirect('/adminpanel')
    else:
        return redirect('/adminlogin')

@app.route('/logout')
def logout():
    '''logout from the admin panel'''
    session.pop('user')
    return redirect('/adminlogin')
    
if __name__ == '__main__':
    app.run(debug=True)