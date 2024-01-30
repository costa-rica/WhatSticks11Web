from flask import Blueprint
from flask import render_template, current_app, send_from_directory
import os
import logging
from logging.handlers import RotatingFileHandler


bp_main = Blueprint('bp_main', __name__)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_bp_main = logging.getLogger(__name__)
logger_bp_main.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(os.environ.get('WEB_ROOT'),'logs','main_routes.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

logger_bp_main.addHandler(file_handler)
logger_bp_main.addHandler(stream_handler)


@bp_main.route("/", methods=["GET","POST"])
def home():
    logger_bp_main.info(f"-- in home page route --")

    return render_template('main/home.html')

@bp_main.route("/download_ios", methods=["GET","POST"])
def download_ios():
    logger_bp_main.info(f"-- in download_ios route --")

    return render_template('main/download_ios.html')


@bp_main.route("/about", methods=["GET","POST"])
def about():
    logger_bp_main.info(f"-- in about page route --")
    return render_template('main/about.html')



@bp_main.route('/privacy', methods = ['GET', 'POST'])
def privacy():
    logger_bp_main.info(f"-- in privacy page route --")
    return render_template('main/privacy.html')


# Website Files static data
@bp_main.route('/website_images/<filename>')
def website_images(filename):
    print("-- entered website_images -")
    print(f"Path to image file: {current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES')}")
    print(f"image filename: {filename}")
    return send_from_directory(current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES'), filename)

@bp_main.route('/website_images_favicon/<filename>')
def website_images_favicon(filename):
    print("-- entered website_images -")
    print(f"Path to image file: {os.path.join(current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES'),'Favicon')}")
    print(f"image filename: {filename}")
    return send_from_directory(os.path.join(current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES'),"Favicon"), filename)


@bp_main.route('/favicon_ico')
def favicon_ico():
    print("--- ** Favicon() ** ----")
    return send_from_directory(current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES'),
                               'Favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')
