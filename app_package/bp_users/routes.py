
from flask import Blueprint
from flask import render_template, url_for, redirect, flash, request, \
    abort, session, Response, current_app, send_from_directory, make_response, \
    send_file, jsonify, g
import bcrypt
from flask_login import login_required, login_user, logout_user, current_user
import os
import json
# from ws_models import sess, engine, text, Users
from ws_models import engine, DatabaseSession, text, Users
from app_package.bp_users.utils import  create_shortname_list, api_url, \
    send_reset_email
import datetime
import requests
import zipfile
from app_package._common.utilities import custom_logger, wrap_up_session
from ws_utilities import create_dashboard_table_object_json_file, \
    create_data_source_object_json_file


logger_bp_users = custom_logger('bp_users.log')
salt = bcrypt.gensalt()
bp_users = Blueprint('bp_users', __name__)


@bp_users.route('/login', methods = ['GET', 'POST'])
def login():
    logger_bp_users.info('- in login -')
    db_session = g.db_session
    if current_user.is_authenticated:
        return redirect(url_for('bp_users.user_home'))

    page_name = 'Login'
    
    if request.method == 'POST':
        # db_session = g.db_session
        formDict = request.form.to_dict()
        logger_bp_users.info(f"formDict: {formDict}")
        email = formDict.get('email')

        user = db_session.query(Users).filter_by(email=email).first()

        # verify password using hash
        password = formDict.get('password')

        if user:
            if password:
                if bcrypt.checkpw(password.encode(), user.password.encode()):
                    login_user(user)
                    
                    return redirect(url_for('bp_users.user_home'))
                else:
                    flash('Password or email incorrectly entered', 'warning')
            else:
                flash('Must enter password', 'warning')
        else:
            flash('No user by that name', 'warning')

    # wrap_up_session(logger_bp_users, db_session)
    return render_template('users/login.html', page_name = page_name)

@bp_users.route('/register', methods = ['GET', 'POST'])
def register():
    db_session = g.db_session
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.user_home'))
    page_name = 'Register'

    if request.method == 'POST':
        formDict = request.form.to_dict()
        new_email = formDict.get('email')

        check_email = db_session.query(Users).filter_by(email = new_email).all()

        logger_bp_users.info(f"check_email: {check_email}")

        if len(check_email)==1:
            flash(f'The email you entered already exists you can sign in or try another email.', 'warning')
            return redirect(url_for('bp_users.register'))

        hash_pw = bcrypt.hashpw(formDict.get('password').encode(), salt)
        new_user = Users(email = new_email, password = hash_pw, timezone = "Etc/GMT")
        db_session.add(new_user)
        # sess.commit()

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
    wrap_up_session(logger_bp_users, db_session)
    return render_template('users/register.html', page_name = page_name)

@bp_users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('bp_main.home'))

@bp_users.route('/request_reset_password', methods = ["GET", "POST"])
def request_reset_password():
    logger_bp_users.info(f'- in request_reset_password')
    db_session = g.db_session
    page_name = 'Request Password Change'
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))
    # form = RequestResetForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        formDict = request.form.to_dict()
        email = formDict.get('email')
        user = db_session.query(Users).filter_by(email=email).first()
        if user:
            send_reset_email(user)
            # # logger_bp_users.info('Email reaquested to reset: ', email)
            # # send_reset_email(user)
            # base_url = api_url()
            # # reset_pass_token_payload = {"email":email}
            # reset_pass_token_payload = {
            #     "email":"nrodrig1@gmail.com",
            #     "ws_api_password":current_app.config.get('WS_API_PASSWORD')
            #     }
            # response_reset_pass_token = requests.request(
            #     'GET',base_url + '/get_reset_password_token', json=reset_pass_token_payload)
            # response_reset_pass_token.status_code

            # flash('Email has been sent with instructions to reset your password','info')
            # # return redirect(url_for('bp_users.login'))
        else:
            flash('Email has not been registered with What Sticks','warning')

        # return redirect(url_for('bp_users.reset_password'))
        return redirect(url_for('bp_users.request_reset_password'))
    return render_template('users/reset_request.html', page_name = page_name)

@bp_users.route('/reset_password', methods = ["GET", "POST"])
def reset_password():
    logger_bp_users.info(f"- accessed: reset_password with token")
    db_session = g.db_session
    # if current_user.is_authenticated:
    #     return redirect(url_for('bp_main.user_home'))
    token = request.args.get('token')
    user = Users.verify_reset_token(token)
    logger_bp_users.info(f'user:: {user}')
    
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('bp_users.reset_password'))
    if request.method == 'POST':
        logger_bp_users.info(f'request.method == POST')

        formDict = request.form.to_dict()
        logger_bp_users.info(f'formDict : {formDict}')

        new_user_obj = db_session.get(Users,user.id)
        hash_pw = bcrypt.hashpw(formDict.get('password_text').encode(), salt)
        new_user_obj.password = hash_pw
        # wrap_up_session(db_session, logger_bp_users)
        try:
            # perform some database operations
            db_session.commit()
            logger_bp_users.info("- perfomed: sess.commit() -")
        except Exception as e:
            db_session.rollback()  # Roll back the transaction on error
            logger_bp_users.info("- perfomed: sess.rollback() -")
            logger_bp_users.info(f"{type(e).__name__}: {e}")
            raise
        finally:
            db_session.close()  # Ensure the session is closed in any case
            logger_bp_users.info("- perfomed: sess.close() -")



        # base_url = api_url()
    
        # reset_pass_payload = {"password_text":formDict.get('password_text')}
        # headers = {'Content-Type':'application/json','x-access-token':token}
        # response_reset_pass = requests.request('POST',base_url + '/reset_password',headers=headers, json=reset_pass_payload)
        # response_reset_pass.status_code

        # if response_reset_pass.status_code == 200:
        #     logger_bp_users.info(f'Refresh database here')
        #     # # NOTE: I think this i unnecessary with the new db_session, before and teardown_appcontext implementation
        #     # # Expire session so new data will take into effect when user logs in again
        #     # sess.expire_all()
        #     # sess.commit()
        #     logout_user()
        #     return redirect(url_for('bp_users.login'))
        return redirect(url_for('bp_users.login'))
        # logger_bp_users.info(f'response_reset_pass.status_code: {response_reset_pass.status_code}')
        # logger_bp_users.info(f"password_text: {formDict.get('password_text')}")


    return render_template('users/reset_request.html', token = token, page_name='Enter New Password')

@bp_users.route('/user_home', methods = ['GET', 'POST'])
@login_required
def user_home():
    logger_bp_users.info("- accessed user_home -")
    user_file_prefix = f"user_{current_user.id:04}_df"
    user_files_list = [ i for i in os.listdir(current_app.config.get('DAILY_CSV')) if user_file_prefix in i ]
    user_files_list_shortname = create_shortname_list(user_files_list, current_user.id)
    
    if request.method == 'POST':
        formDict = request.form.to_dict()
        logger_bp_users.info(f'formDict : {formDict}')

        if formDict.get("btn_download_files"):
            logger_bp_users.info(f'- Selected btn_download_files -')
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
            return send_file(zip_file_path, as_attachment=True)

        elif formDict.get("btn_recalculate_dashboard"):
            logger_bp_users.info(f'- Selected btn_recalculate_dashboard -')
            create_data_source_object_json_file(current_user.id)
            create_dashboard_table_object_json_file(current_user.id)
            if request.referrer:
                return redirect(request.referrer)

    return render_template('users/user_home.html', user_files_list=user_files_list, len=len,
        user_files_list_shortname=user_files_list_shortname, zip=zip)

# User Files static data
@bp_users.route('/user_file/<filename>')
@login_required
def user_file(filename):
    return send_from_directory(current_app.config.get('DAILY_CSV'), filename)


@bp_users.route('/nrodrig1_admin', methods=["GET"])
def nrodrig1_admin():
    db_session = g.db_session
    nrodrig1 = db_session.query(Users).filter_by(email="nrodrig1@gmail.com").first()
    if nrodrig1 != None:
        nrodrig1.admin_users_permission = True
        # sess.commit()
        flash("nrodrig1@gmail updated to admin", "success")
    return redirect(url_for('bp_main.home'))






