from flask import Blueprint
from flask import render_template, current_app, send_from_directory
import os
import logging
from logging.handlers import RotatingFileHandler
# from ws_models import session_scope
# from flask_login import login_required, login_user, logout_user, current_user


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

# @bp_main.context_processor
# def inject_user():
#     logger_bp_main.info(f"-- ***** in inject_user route --")
#     try:
#         if current_user.is_authenticated:
#             logger_bp_main.info(f"--  if current_user.is_authenticated --")
#             user_id = current_user.id
            
#             try:
#                 yield session
#                 session.commit()
#             except Exception as e:
#                 session.rollback()
#                 raise
#             finally:
#                 session.close()
#             session = Session()
#             user = session.get(Users,user_id)
#             logger_bp_main.info(f"--  user: {user} --")
#             login(user)
#     except:
#         logger_bp_main.info(f"--  if @bp_main.context_processor current_user is None --")

# @bp_main.before_request
# def before_request():
#     logger_bp_main.info(f"-- ***** in before_request route --")
#     try:
#         if current_user.is_authenticated:
#             logger_bp_main.info(f"--  if current_user.is_authenticated --")
#             user_id = current_user.id
            
#             try:
#                 yield session
#                 session.commit()
#             except Exception as e:
#                 session.rollback()
#                 raise
#             finally:
#                 session.close()
#             session = Session()
#             user = session.get(Users,user_id)
#             logger_bp_main.info(f"--  user: {user} --")
#             login(user)
#     except:
#         logger_bp_main.info(f"--  if @bp_main.before_request current_user is None --")

@bp_main.route("/", methods=["GET","POST"])
def home():
    logger_bp_main.info(f"-- in home page route --")
    # logger_bp_main.info(f"--  current_user: {current_user} --")
    return render_template('main/home.html')

@bp_main.route("/download_ios", methods=["GET","POST"])
def download_ios():
    logger_bp_main.info(f"-- in download_ios route --")
    # download_test_flight_link = "https://testflight.apple.com/join/ZXNq4c8s"
    # try:
    with open(os.path.join(current_app.config.get('WEBSITE_FILES'),'TestFlightUrl.txt'), 'r') as file:
        download_test_flight_link = file.read().strip()  # .strip() removes any leading/trailing whitespace
    
    # except:
    #     download_test_flight_link="https://testflight.apple.com/join/LHzvgt5g"

    return render_template('main/download_ios.html', download_test_flight_link=download_test_flight_link)

@bp_main.route("/about", methods=["GET","POST"])
def about():
    logger_bp_main.info(f"-- in about page route --")

    test_flight_link = ""

    try:
        with open(os.path.join(current_app.config.get('WEBSITE_FILES'),'TestFlightUrl.txt'), 'r') as file:
            test_flight_link = file.read().strip()  # .strip() removes any leading/trailing whitespace
    except FileNotFoundError:
        logger_bp_main.info(f"- no TestFlight Link found")

    return render_template('main/about.html', test_flight_link=test_flight_link)

@bp_main.route('/privacy', methods = ['GET', 'POST'])
def privacy():
    logger_bp_main.info(f"-- in privacy page route --")
    return render_template('main/privacy.html')

@bp_main.route('/what_sticks_video/<filename>', methods = ['GET', 'POST'])
def what_sticks_video(filename):
    logger_bp_main.info(f"-- in privacy page route --")

    if filename == "SleepTime20240130_shortDrawings.mp4":
        filename = "SleepTime_v03.mp4"

    return render_template('main/video_page.html', filename=filename)

# Website Files static data
@bp_main.route('/website_images/<filename>')
def website_images(filename):
    print("-- entered website_images -")
    print(f"Path to image file: {current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES')}")
    print(f"image filename: {filename}")
    return send_from_directory(current_app.config.get('DIR_WEBSITE_UTILITY_IMAGES'), filename)

# Website Videos static data
@bp_main.route('/website_videos/<filename>')
def website_videos(filename):
    print("-- entered website_videos -")
    print(f"Path to image file: {current_app.config.get('DIR_WEBSITE_VIDEOS')}")
    print(f"image filename: {filename}")
    return send_from_directory(current_app.config.get('DIR_WEBSITE_VIDEOS'), filename)

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

@bp_main.route('/robots.txt')
def robots_txt():
    # return send_from_directory(app.static_folder, 'robots.txt')
    return send_from_directory(current_app.config.get('WEBSITE_FILES'), 'robots.txt')
