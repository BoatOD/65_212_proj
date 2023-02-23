from flask import (jsonify, render_template,
                   request, url_for, flash, redirect)

from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse
import json
from sqlalchemy.sql import text
from flask_login import login_user
from app import app
from app import db
from app import login_manager
from app.models.contact import Contact
from app.models.authuser import AuthUser
from app.models.BlogEntry import BlogEntry


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our
    # user table, use it in the query for the user
    return AuthUser.query.get(int(user_id))


@app.route('/')
def home():
    return "Flask says 'Hello world!'"

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
            # if there is no id: create a new contact entry
            if not id_:
                entry = Contact(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                contact = Contact.query.get(id_)
                contact.update(**validated_dict)


            db.session.commit()


        return lab10_db_contacts()
    return app.send_static_file('lab10_phonebook.html')

@app.route("/lab10/contacts")
def lab10_db_contacts():
    contacts = []
    db_contacts = Contact.query.all()


    contacts = list(map(lambda x: x.to_dict(), db_contacts))
    app.logger.debug("DB Contacts: " + str(contacts))


    return jsonify(contacts)

@app.route('/lab10/remove_contact', methods=('GET', 'POST'))
def lab10_remove_contacts():
    app.logger.debug("LAB10 - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
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
    return render_template('lab11_microblog.html', posts=posts)

@app.route('/microblog', methods=('GET', 'POST'))
def microblog():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
        id_ = result.get('id', '')
        validated = True
        validated_dict = dict()
        valid_keys = ['name', 'message', 'email' , 'date']


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
                entry = BlogEntry(**validated_dict)
                app.logger.debug(str(entry))
                db.session.add(entry)
            # if there is an id already: update the contact entry
            else:
                blogentry = BlogEntry.query.get(id_)
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
def lab11_remove_content():
    app.logger.debug("LAB11 - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
        try:
            microblogs = BlogEntry.query.get(id_)
            db.session.delete(microblogs)
            db.session.commit()
        except Exception as ex:
            app.logger.debug(ex)
            raise
    return lab11_microblog_content()


@app.route('/lab12')
def lab12_index():
   return 'Lab12'

@app.route('/lab12/profile')
def lab12_profile():
   return 'Profile'

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

@app.route('/lab12/signup')
def lab12_signup():
   return render_template('lab12/signup.html')

@ app.route('/lab12/logout')
def lab12_logout():
   return 'Logout'