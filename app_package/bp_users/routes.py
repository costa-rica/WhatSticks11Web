
from flask import Blueprint
from flask import render_template, url_for, redirect, flash, request, \
    abort, session, Response, current_app, send_from_directory, make_response, \
    send_file
import bcrypt
from flask_login import login_required, login_user, logout_user, current_user
import logging
from logging.handlers import RotatingFileHandler
import os
import json
from ws_models import sess, engine, text, Users

from app_package.bp_users.utils import send_reset_email, send_confirm_email, \
    create_shortname_list
import datetime
import requests
import zipfile

#Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

#initialize a logger
logger_bp_users = logging.getLogger(__name__)
logger_bp_users.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(os.environ.get('WEB_ROOT'),'logs','bp_users.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

#where the stream_handler will print
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

# logger_sched.handlers.clear() #<--- This was useful somewhere for duplicate logs
logger_bp_users.addHandler(file_handler)
logger_bp_users.addHandler(stream_handler)

salt = bcrypt.gensalt()

bp_users = Blueprint('bp_users', __name__)


@bp_users.route('/login', methods = ['GET', 'POST'])
def login():
    print('- in login')
    if current_user.is_authenticated:
        return redirect(url_for('bp_blog.blog_user_home'))
    
    logger_bp_users.info(f'- in login route')

    page_name = 'Login'
    if request.method == 'POST':
        # session.permanent = True
        formDict = request.form.to_dict()
        print(f"formDict: {formDict}")
        email = formDict.get('email')

        user = sess.query(Users).filter_by(email=email).first()

        # verify password using hash
        password = formDict.get('password')

        if user:
            if password:
                if bcrypt.checkpw(password.encode(), user.password):
                    login_user(user)
                    # flash('Logged in successfully', 'success')
                    # return redirect(url_for('bp_blog.blog_user_home'))
                    return redirect(url_for('bp_users.user_home'))
                else:
                    flash('Password or email incorrectly entered', 'warning')
            else:
                flash('Must enter password', 'warning')
        # elif formDict.get('btn_login_as_guest'):
        #     user = sess.query(Users).filter_by(id=2).first()
        #     login_user(user)

        #     return redirect(url_for('dash.dashboard', dash_dependent_var='steps'))
        else:
            flash('No user by that name', 'warning')


    return render_template('users/login.html', page_name = page_name)

@bp_users.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.user_home'))
    page_name = 'Register'
    if request.method == 'POST':
        formDict = request.form.to_dict()
        new_email = formDict.get('email')

        check_email = sess.query(Users).filter_by(email = new_email).all()

        logger_bp_users.info(f"check_email: {check_email}")

        if len(check_email)==1:
            flash(f'The email you entered already exists you can sign in or try another email.', 'warning')
            return redirect(url_for('bp_users.register'))

        hash_pw = bcrypt.hashpw(formDict.get('password').encode(), salt)
        new_user = Users(email = new_email, password = hash_pw, timezone = "Etc/GMT")
        sess.add(new_user)
        sess.commit()

        # Send email confirming succesfull registration
        try:
            send_confirm_email(new_email)
        except:
            flash(f'Problem with email: {new_email}', 'warning')
            return redirect(url_for('bp_users.login'))

        #log user in
        print('--- new_user ---')
        print(new_user)
        login_user(new_user)
        flash(f'Succesfully registered: {new_email}', 'info')
        return redirect(url_for('bp_main.home'))

    return render_template('users/register.html', page_name = page_name)

@bp_users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('bp_main.home'))

@bp_users.route('/reset_password', methods = ["GET", "POST"])
def reset_password():
    page_name = 'Request Password Change'
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))
    # form = RequestResetForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        formDict = request.form.to_dict()
        email = formDict.get('email')
        user = sess.query(Users).filter_by(email=email).first()
        if user:
        # send_reset_email(user)
            logger_bp_users.info('Email reaquested to reset: ', email)
            send_reset_email(user)
            flash('Email has been sent with instructions to reset your password','info')
            # return redirect(url_for('bp_users.login'))
        else:
            flash('Email has not been registered with What Sticks','warning')

        return redirect(url_for('bp_users.reset_password'))
    return render_template('users/reset_request.html', page_name = page_name)

@bp_users.route('/reset_password/<token>', methods = ["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.user_home'))
    user = Users.verify_reset_token(token)
    logger_bp_users.info('user::', user)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('bp_users.reset_password'))
    if request.method == 'POST':

        formDict = request.form.to_dict()
        if formDict.get('password_text') != '':
            hash_pw = bcrypt.hashpw(formDict.get('password_text').encode(), salt)
            user.password = hash_pw
            sess.commit()
            flash('Password successfully updated', 'info')
            return redirect(url_for('bp_users.login'))
        else:
            flash('Must enter non-empty password', 'warning')
            return redirect(url_for('bp_users.reset_token', token=token))

    return render_template('users/reset_request.html', page_name='Enter New Password')

@bp_users.route('/user_home', methods = ['GET', 'POST'])
@login_required
def user_home():
    logger_bp_users.info("- accessed user_home -")
    user_file_prefix = f"user_{current_user.id:04}_df"
    user_files_list = [ i for i in os.listdir(current_app.config.get('DAILY_CSV')) if user_file_prefix in i ]
    user_files_list_shortname = create_shortname_list(user_files_list, current_user.id)
    
    if request.method == 'POST':
        # Get the directory where the CSV files are stored
        csv_directory = current_app.config.get('DAILY_CSV')

        # Define the zip file name based on the current user's ID
        zip_file_name = f"user_{current_user.id:04}_files.zip"
        zip_file_path = os.path.join(csv_directory, zip_file_name)

        # Create a zip file in write mode
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            # Loop through each file in the directory
            for folder_name, subfolders, filenames in os.walk(csv_directory):
                for filename in filenames:
                    # Check if the current file is in the user's file list
                    if filename in user_files_list:
                        # Create the full path to the file
                        file_path = os.path.join(folder_name, filename)
                        # Add the file to the zip archive
                        zipf.write(file_path, os.path.relpath(file_path, csv_directory))
    
        # After zipping, send the file to the client
        # return send_file(zip_file_path, as_attachment=True, attachment_filename=zip_file_name)
        return send_file(zip_file_path, as_attachment=True)

    return render_template('users/user_home.html', user_files_list=user_files_list, len=len,
        user_files_list_shortname=user_files_list_shortname, zip=zip)

# User Files static data
@bp_users.route('/user_file/<filename>')
@login_required
def user_file(filename):
    return send_from_directory(current_app.config.get('DAILY_CSV'), filename)



# ########################
# # recaptcha
# ########################

# @bp_users.route("/sign-user-up", methods=['POST'])
# def sign_up_user():
#     # print(request.form)
#     secret_response = request.form['g-recaptcha-response']

#     verify_response = requests.post(url=f"{current_app.config.get('VERIFY_URL_CAPTCHA')}?secret={current_app.config.get('SECRET_KEY_CAPTCHA')}&response={secret_response}").json()
#     print(verify_response)
#     if verify_response['success'] == False or verify_response['score'] < 0.5:
#         abort(401)

#     formDict = request.form.to_dict()
#     print(formDict)
    
#     # get email, name and message

#     senders_name = formDict.get('name')
#     senders_email = formDict.get('email')
#     senders_message = formDict.get('message')

#     #send message to nick@dashanddata.com

#     # Send email confirming succesfully sent message to nick@dashanddata.com
#     try:
#         send_message_to_nick(senders_name, senders_email, senders_message)
#     except:
#         print('*** not successsuflly send_message_to_nick ***')
#     try:
#         send_confirm_email(senders_name, senders_email, senders_message)
#     except:
#         print('*** not successsuflly send_confirm_email')
#         flash(f'Problem with email: {new_email}', 'warning')
#         return redirect(url_for('bp_users.login'))



#     flash(f'Message has been sent to nick@dashanddata.com. A verification has been sent to your email as well.', 'success')
#     return redirect(url_for('bp_users.home'))


    # return redirect(url_for('home'))





