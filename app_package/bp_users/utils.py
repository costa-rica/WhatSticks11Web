from flask import current_app, url_for
from flask_login import current_user
import json
from ws_models import sess, Users
from flask_mail import Message
from app_package import mail
import os
import shutil
import pandas as pd
from datetime import datetime
import csv
from app_package._common.utilities import wrap_up_session, custom_logger

logger_bp_users = custom_logger('bp_users.log')


#Kinetic Metrics, LLC
def userPermission(email):
    kmPermissions=['nickapeed@yahoo.com','test@test.com',
        'emily.reichard@kineticmetrics.com']
    if email in kmPermissions:
        return (True,'1,2,3,4,5,6,7,8')
    
    return (False,)

# def send_reset_email(user):
#     token = user.get_reset_token()
#     logger_main.info(f"current_app.config.get(MAIL_USERNAME): {current_app.config.get('MAIL_USERNAME')}")
#     msg = Message('Password Reset Request',
#                   sender=current_app.config.get('MAIL_USERNAME'),
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('bp_users.reset_token', token=token, _external=True)}

# If you did not make this request, ignore email and there will be no change.

# -Nick
# What Sticks
# '''

#     mail.send(msg)


# def send_confirm_email(email):
#     if os.environ.get('CONFIG_TYPE') == 'prod':
#         logger_main.info(f"-- sending email to {email} --")
#         msg = Message('Welcome to What Sticks',
#             sender=current_app.config.get('MAIL_USERNAME'),
#             recipients=[email])
#         msg.body = 'You have succesfully signed up.'
#         mail.send(msg)
#         logger_main.info(f"-- email sent --")
#     else :
#         logger_main.info(f"-- Non prod mode, no email sent --")


def create_shortname_list(user_files_list, user_id):
    # Define the prefixes to remove
    prefix_to_remove_1 = f"user_{user_id:04}_df_"
    prefix_to_remove_2 = f"user_{user_id:04}_df_daily_"
    suffix_to_remove = ".csv"
    
    # Create the new list with shortnames
    user_files_list_shortname = [
        filename.replace(prefix_to_remove_2, '').replace(prefix_to_remove_1, '').replace(suffix_to_remove, '')
        for filename in user_files_list
    ]
    
    return user_files_list_shortname

def api_url():
    match os.environ.get('WS_CONFIG_TYPE'):
        case 'dev':
            api_base_url = f"https://dev.api10.what-sticks.com"
        case 'prod':
            api_base_url = f"https://api10.what-sticks.com"
        case _:
            api_base_url = f"http://localhost:5001"
    
    return api_base_url
