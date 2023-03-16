import os
import secrets
import string
from flask import (jsonify, render_template, request, url_for, flash, redirect)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from sqlalchemy.sql import text
from flask_login import login_user, login_required, logout_user, current_user
import urllib.request

import json

from app import app
from app import db
from app import login_manager

from app.models.authuser import AuthUser
from app.models.problems import problems
from app.models.review import Review

from app import oauth

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our
    # user table, use it in the query for the user
    return AuthUser.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/crash')
def crash():
    return 1/0

@app.route('/db')
def db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return '<h1>db works.</h1>'
    except Exception as e:
        return '<h1>db is broken.</h1>' + str(e)

def gen_avatar_url(email, name):
    bgcolor = generate_password_hash(email, method='sha256')[-6:]
    color = hex(int('0xffffff', 0) -
                int('0x'+bgcolor, 0)).replace('0x', '')
    lname = ''
    temp = name.split()
    fname = temp[0][0]
    if len(temp) > 1:
        lname = temp[1][0]


    avatar_url = "https://ui-avatars.com/api/?name=" + \
        fname + "+" + lname + "&background=" + \
        bgcolor + "&color=" + color
    return avatar_url

@app.route('/project/home')
def project_home():
   return render_template('project_flask/home.html')

@app.route('/project/login', methods=('GET', 'POST'))
def project_login():
    if request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        user = AuthUser.query.filter_by(email=email).first()
 
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the
        # hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('project_home'))

        # if the above check passes, then we know the user has the right
        # credentials
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('project_home')
        return redirect(next_page)
    return render_template('project_flask/home.html')

@app.route('/project/logout')
@login_required
def project_logout():
    logout_user()
    return redirect(url_for('project_home'))

@app.route('/project/signup', methods=('GET', 'POST'))
def project_signup():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
 
        validated = True
        validated_dict = {}
        valid_keys = ['email', 'name', 'password']


        # validate the input
        for key in result:
            app.logger.debug(str(key)+": " + str(result[key]))
            # screen of unrelated inputs
            if key not in valid_keys:
                continue


            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value
            # code to validate and add user to database goes here
        app.logger.debug("validation done")
        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            email = validated_dict['email']
            name = validated_dict['name']
            password = validated_dict['password']
            # if this returns a user, then the email already exists in database
            user = AuthUser.query.filter_by(email=email).first()


            if user:
                # if a user is found, we want to redirect back to signup
                # page so user can try again
                flash('Email address already exists')
                return redirect(url_for('project_home'))


            # create a new user with the form data. Hash the password so
            # the plaintext version isn't saved.
            app.logger.debug("preparing to add")
            avatar_url = 'user.png'
            new_user = AuthUser(email=email, name=name,
                                password=generate_password_hash(
                                    password, method='sha256'),
                                avatar_url=avatar_url)
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()


        return redirect(url_for('project_home'))
    return render_template('project_flask/home.html')

@app.route('/project/profile', methods=('GET', 'POST'))
@login_required
def project_profile():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        password = result.get('password', '')
        avatar_url = ''
        picname = '0'
        validated = True
        validated_dict = {}
        valid_keys = ['email', 'name' , 'email_old']

        if password == '':
            flash('Please enter a password')
            return redirect(url_for('project_profile'))
            

        # validate the input
        for key in result:
            app.logger.debug(str(key)+": " + str(result[key]))
            # screen of unrelated inputs
            if key not in valid_keys:
                continue


            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value
            # code to validate and add user to database goes here
        app.logger.debug("validation done")
        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            email_old = validated_dict['email_old']
            email = validated_dict['email']
            name = validated_dict['name']
            
            user = AuthUser.query.filter_by(email=email_old).first()
            if not check_password_hash(user.password, password):
                flash('Password incorrect')
                return redirect(url_for('project_profile'))
            
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    avatar_url = user.avatar_url
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    avatar_url = file.filename
                if file and not allowed_file(file.filename):
                    flash('Allowed image types are - png, jpg, jpeg, gif')
                    return redirect(url_for('project_profile'))
                

            # if this returns a user, then the email already exists in database
            user = AuthUser.query.filter_by(email=email_old).first()
            if email != user.email:
                user = AuthUser.query.filter_by(email=email).first()
                if user:
                    # if a user is found, we want to redirect back to signup
                    # page so user can try again
                    flash('Email address already exists')
                    return redirect(url_for('project_profile'))

            # update User
            user = AuthUser.query.filter_by(email=email_old).first()
            app.logger.debug("preparing to add")
            
            if 'file' not in request.files:
                avatar_url = user.avatar_url
            
            updatedict = {'email':email , 'name':name , 'avatar_url':avatar_url}
            user.update(**updatedict)
            
            # update Blog
            review = Review.query.filter_by(email=email_old).all()
            for i in review:
                updatedict_blog = {'name':name , 'message':i.message , 'email':email, 'date':i.date , 'avatar_url':avatar_url }
                i.update(**updatedict_blog)

            problem = problems.query.filter_by(email=email_old).all()
            for i in problem:
                updatedict_blog = {'name':name , 'message':i.message , 'email':email, 'date':i.date , 'avatar_url':avatar_url }
                i.update(**updatedict_blog)
            #commit
            db.session.commit()
            flash('Change Succeed')
        return redirect(url_for('project_profile'))
    return render_template('project_flask/profile.html', )

@app.route('/display/<filename>')
def display_image(filename):
    app.logger.debug(filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/project/review', methods=('GET', 'POST'))
def projectreviews():
    posts = Review.query.all()
    return render_template('project_flask/review.html', posts=posts)

@app.route('/review', methods=('GET', 'POST'))
@login_required
def reviews():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        picname = '0'
        validated = True
        validated_dict = dict()
        valid_keys = ['name', 'message', 'email', 'date', 'avatar_url', 'lat', 'lng']


        # validate the input
        for key in result:
            app.logger.debug(key, result[key])
            # screen of unrelated inputs
            if key not in valid_keys:
                continue


            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value

        if 'file' in request.files:
            app.logger.debug('work')
            file = request.files['file']
            if file.filename == '':
                flash('No image selected for uploading')
                return redirect(url_for('reviews'))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                validated_dict['picname'] = file.filename
            if file and not allowed_file(file.filename):
                flash('Allowed image types are - png, jpg, jpeg, gif')
                return redirect(url_for('reviews'))
        else:
            validated_dict['picname'] = '1'
            picname = '1'

        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            # if there is no id: create a new contact entry.
            if not id_:
                entry = Review(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                review = Review.query.get(id_)
                if review.email == current_user.email:
                    if picname == '1':
                        app.logger.debug('work')
                        validated_dict['picname'] = review.picname
                    review.update(**validated_dict)
            db.session.commit()
        return review_content()
    return redirect(url_for("projectreviews"))

@app.route("/review/blog")
def review_content():
    microblogs = []
    db_microblogs = Review.query.all()

    microblogs = list(map(lambda x: x.to_dict(), db_microblogs))
    app.logger.debug("DB microblogs: " + str(microblogs))

    return jsonify(microblogs)

@app.route('/project/remove-review', methods=('GET', 'POST'))
@login_required
def project_remove_review():
    app.logger.debug("REVIEW - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
        try:
            review = Review.query.get(id_)
            if review.email == current_user.email:
                db.session.delete(review)
                db.session.commit()
        except Exception as ex:
            app.logger.debug(ex)
            raise
    return review_content()
    
@app.route('/project/problems', methods=('GET', 'POST'))
def projectproblems():
    posts = problems.query.all()
    return render_template('project_flask/problems.html', posts=posts)

@app.route('/Notify', methods=('GET', 'POST'))
def Notify():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        picname = '0'
        validated = True
        validated_dict = dict()
        valid_keys = ['name', 'message', 'email', 'date', 'avatar_url', 'lat', 'lng']


        # validate the input
        for key in result:
            app.logger.debug(key, result[key])
            # screen of unrelated inputs
            if key not in valid_keys:
                continue


            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value

        if 'file' in request.files:
            app.logger.debug('work')
            file = request.files['file']
            if file.filename == '':
                flash('No image selected for uploading')
                return redirect(url_for('Notify'))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                validated_dict['picname'] = file.filename
            if file and not allowed_file(file.filename):
                flash('Allowed image types are - png, jpg, jpeg, gif')
                return redirect(url_for('Notify'))
        else:
            validated_dict['picname'] = '1'
            picname = '1'

        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            # if there is no id: create a new contact entry.
            if not id_:
                entry = problems(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                problem = problems.query.get(id_)
                if problem.email == current_user.email:
                    if picname == '1':
                        app.logger.debug('work')
                        validated_dict['picname'] = problem.picname
                    problem.update(**validated_dict)
            db.session.commit()
        return problems_content()
    return redirect(url_for("projectproblems"))

@app.route("/problems/blog")
def problems_content():
    microblogs = []
    db_microblogs = problems.query.all()

    microblogs = list(map(lambda x: x.to_dict(), db_microblogs))
    app.logger.debug("DB microblogs: " + str(microblogs))

    return jsonify(microblogs)

@app.route('/project/remove-problems', methods=('GET', 'POST'))
@login_required
def project_remove_problems():
    app.logger.debug("PROBLEMS - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
        try:
            review = problems.query.get(id_)
            if review.email == current_user.email:
                db.session.delete(review)
                db.session.commit()
        except Exception as ex:
            app.logger.debug(ex)
            raise
    return problems_content()

@app.route('/google')
def google():


    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


   # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    app.logger.debug(str(token))


    userinfo = token['userinfo']
    app.logger.debug(" Google User " + str(userinfo))
    email = userinfo['email']
    user = AuthUser.query.filter_by(email=email).first()


    if not user:
        name = userinfo['given_name'] + " " + userinfo['family_name']
        random_pass_len = 8
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(random_pass_len))
        picture = userinfo['picture']
        new_user = AuthUser(email=email, name=name,
                           password=generate_password_hash(
                               password, method='sha256'),
                           avatar_url=picture)
        db.session.add(new_user)
        db.session.commit()
        user = AuthUser.query.filter_by(email=email).first()
    login_user(user)
    return redirect('/project/home') 


if __name__ == "__main__":  #and the final closing function
    app.run(debug=True)