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

from app.models.contact import Contact
from app.models.authuser import AuthUser, PrivateContact
from app.models.BlogEntry import BlogEntry
from app.models.problems import problems
from app.models.review import review

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

@app.route('/lab04')
def lab04_bootstrap():
    return app.send_static_file('lab04_bootstrap.html')

@app.route('/lab10', methods=('GET', 'POST'))
@login_required
def lab10_phonebook():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        validated = True
        validated_dict = dict()
        valid_keys = ['firstname', 'lastname', 'phone']


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


        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            # if there is no id_: create contact
            if not id_:
                validated_dict['owner_id'] = current_user.id
                # entry = Contact(**validated_dict)
                entry = PrivateContact(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id_ already: update contact
            else:
                # contact = Contact.query.get(id_)
                contact = PrivateContact.query.get(id_)
                if contact.owner_id == current_user.id:
                    contact.update(**validated_dict)

            db.session.commit()

        return lab10_db_contacts()
    return render_template('lab12/lab10_phonebook.html')

@app.route("/lab10/contacts")
@login_required
def lab10_db_contacts():
    # db_contacts = Contact.query.all()
    db_contacts = PrivateContact.query.filter(
        PrivateContact.owner_id == current_user.id)
    contacts = list(map(lambda x: x.to_dict(), db_contacts))
    app.logger.debug("DB Contacts: " + str(contacts))

    return jsonify(contacts)

@app.route('/lab10/remove_contact', methods=('GET', 'POST'))
@login_required
def lab10_remove_contacts():
    app.logger.debug("LAB10 - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
        contact = PrivateContact.query.get(id_)
        if contact.owner_id == current_user.id:
            try:
                contact = Contact.query.get(id_)
                db.session.delete(contact)
                db.session.commit()
            except Exception as ex:
                app.logger.debug(ex)
                raise
    return lab10_db_contacts()

@app.route('/lab11', methods=('GET', 'POST'))
def lab11_microblog():
    posts = BlogEntry.query.all()
    return render_template('lab12/lab11_microblog.html', posts=posts)

@app.route('/microblog', methods=('GET', 'POST'))

def microblog():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        validated = True
        validated_dict = dict()
        valid_keys = ['name', 'message', 'email' , 'date', 'avatar_url']


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
            

        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            # if there is no id: create a new contact entry.
            if not id_:
                entry = BlogEntry(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                blogentry = BlogEntry.query.get(id_)
                if blogentry.email == current_user.email:
                    blogentry.update(**validated_dict)
            db.session.commit()
            return lab11_microblog_content()
        return redirect(url_for("lab11_microblog"))

@app.route("/lab11/microblogs")
def lab11_microblog_content():
    microblogs = []
    db_microblogs = BlogEntry.query.all()

    microblogs = list(map(lambda x: x.to_dict(), db_microblogs))
    app.logger.debug("DB microblogs: " + str(microblogs))

    return jsonify(microblogs)

@app.route('/lab11/remove_content', methods=('GET', 'POST'))
@login_required
def lab11_remove_content():
    app.logger.debug("LAB11 - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
        try:
            microblogs = BlogEntry.query.get(id_)
            if microblogs.email == current_user.email:
                db.session.delete(microblogs)
                db.session.commit()
        except Exception as ex:
            app.logger.debug(ex)
            raise
    return lab11_microblog_content()


@app.route('/lab12')
def lab12_index():
   return render_template('lab12/index.html')

@app.route('/lab12/profile', methods=('GET', 'POST'))
@login_required
def lab12_profile():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        password = result.get('password', '')
        validated = True
        validated_dict = {}
        valid_keys = ['email', 'name' , 'email_old']

        if password == '':
            flash('Please enter a password')
            return redirect(url_for('lab12_profile'))
            

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
                return redirect(url_for('lab12_profile'))
            

            # if this returns a user, then the email already exists in database
            user = AuthUser.query.filter_by(email=email_old).first()
            if email != email_old:
                if user:
                    # if a user is found, we want to redirect back to signup
                    # page so user can try again
                    flash('Email address already exists')
                    return redirect(url_for('lab12_profile'))

            # update User
            user = AuthUser.query.filter_by(email=email_old).first()
            app.logger.debug("preparing to add")
            avatar_url = gen_avatar_url(email, name)
            updatedict = {'email':email , 'name':name , 'avatar_url':avatar_url}
            user.update(**updatedict)
            
            # update Blog
            blogentry = BlogEntry.query.filter_by(email=email_old).all()
            for i in blogentry:
                updatedict_blog = {'name':name , 'message':i.message , 'email':email, 'date':i.date , 'avatar_url':avatar_url }
                i.update(**updatedict_blog)

            #commit
            db.session.commit()
        return redirect(url_for('lab12_profile'))
    return render_template('lab12/profile.html')

@app.route('/lab12/login', methods=('GET', 'POST'))
def lab12_login():
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
            return redirect(url_for('lab12_login'))

        # if the above check passes, then we know the user has the right
        # credentials
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('lab12_profile')
        return redirect(next_page)
    return render_template('lab12/login.html')

@app.route('/lab12/signup', methods=('GET', 'POST'))
def lab12_signup():
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
                return redirect(url_for('lab12_signup'))


            # create a new user with the form data. Hash the password so
            # the plaintext version isn't saved.
            app.logger.debug("preparing to add")
            avatar_url = gen_avatar_url(email, name)
            new_user = AuthUser(email=email, name=name,
                                password=generate_password_hash(
                                    password, method='sha256'),
                                avatar_url=avatar_url)
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()


        return redirect(url_for('lab12_login'))
    return render_template('lab12/signup.html')

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

@app.route('/lab12/logout')
@login_required
def lab12_logout():
    logout_user()
    return redirect(url_for('lab12_index'))

@app.route('/project/home')
def project_home():
   maps = review.query.all()
   return render_template('project_flask/index.html',maps=maps)

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
            avatar_url = gen_avatar_url(email, name)
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
                return redirect(url_for('lab12_profile'))
            
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    flash('No image selected for uploading')
                    return redirect(url_for('project_profile'))
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
                if user:
                    # if a user is found, we want to redirect back to signup
                    # page so user can try again
                    flash('Email address already exists')
                    return redirect(url_for('lab12_profile'))

            # update User
            user = AuthUser.query.filter_by(email=email_old).first()
            app.logger.debug("preparing to add")
            
            if 'file' not in request.files:
                avatar_url = gen_avatar_url(email, name)
            
            updatedict = {'email':email , 'name':name , 'avatar_url':avatar_url}
            user.update(**updatedict)
            
            # update Blog
            blogentry = BlogEntry.query.filter_by(email=email_old).all()
            for i in blogentry:
                updatedict_blog = {'name':name , 'message':i.message , 'email':email, 'date':i.date , 'avatar_url':avatar_url }
                i.update(**updatedict_blog)
            #commit
            db.session.commit()
            flash('Change Succeed')
        return redirect(url_for('project_profile'))
    return render_template('project_flask/profile.html', )

@app.route('/display/<filename>')
@login_required
def display_image(filename):
    if current_user.avatar_url[:5] == 'https':
        return redirect(url_for('static', filename='uploads/' + filename), code=301)
    else:
        return redirect(url_for('static', filename='uploads/' + filename), code=301)

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

@app.route('/project/review', methods=('GET', 'POST'))
def reviews():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        validated = True
        validated_dict = dict()
        valid_keys = ['message']


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


        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            # if there is no id: create a new contact entry
            if not id_:
                entry = review(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                contact = review.query.get(id_)
                contact.update(**validated_dict)


            db.session.commit()


        return review_content()

    return render_template('project_flask/review.html')

@app.route("/review/blog")
def review_content():
    microblogs = []
    db_microblogs = review.query.all()

    microblogs = list(map(lambda x: x.to_dict(), db_microblogs))
    app.logger.debug("DB microblogs: " + str(microblogs))

    return jsonify(microblogs)

    
@app.route('/project/problems')
def problem():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        validated = True
        validated_dict = dict()
        valid_keys = ['message']


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


        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            # if there is no id: create a new contact entry
            if not id_:
                entry = problems(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                contact = problems.query.get(id_)
                contact.update(**validated_dict)


            db.session.commit()


        return problems_content()
    
    return render_template('project_flask/problems.html')

@app.route("/problems/blog")
def problems_content():
    microblogs = []
    db_microblogs = problems.query.all()

    microblogs = list(map(lambda x: x.to_dict(), db_microblogs))
    app.logger.debug("DB microblogs: " + str(microblogs))

    return jsonify(microblogs)