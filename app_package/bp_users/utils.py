import os
from app_package._common.utilities import custom_logger
from flask_mail import Message
from app_package import mail
from flask import current_app, url_for

logger_bp_users = custom_logger('bp_users.log')


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

def send_reset_email(user):
    token = user.get_reset_token()
    logger_bp_users.info(f"current_app.config.get(MAIL_USERNAME): {current_app.config.get('MAIL_USERNAME')}")
    msg = Message('Password Reset Request',
                  sender=current_app.config.get('MAIL_USERNAME'),
                  recipients=[user.email])

    long_f_string = (
        "To reset your password, visit the following link:" +
        f"\n {url_for('bp_users.reset_password', token=token, _external=True)} " +
        "\n\n" +
        "If you did not make this request, simply ignore this email and no changes will be made."
    )
    msg.body =long_f_string

    mail.send(msg)
