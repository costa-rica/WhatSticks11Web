from flask import Blueprint
from flask import render_template, current_app, send_from_directory, g, \
    request
import os
from app_package._common.utilities import custom_logger, wrap_up_session
from ws_utilities import create_df_from_db_table_name
from ws_models import DatabaseSession

logger_bp_main = custom_logger('bp_main.log')
bp_main = Blueprint('bp_main', __name__)

# @bp_main.before_request
# def before_request():

#     # Assign a new session to a global `g` object, accessible during the whole request
#     g.db_session = DatabaseSession()


#     if request.referrer:
#         logger_bp_main.info(f"- request.referrer: {request.referrer} ")
    
#     logger_bp_main.info(f"- db_session ID: {id(g.db_session)} ")
    
#     if request.endpoint:
#         logger_bp_main.info(f"- request.endpoint: {request.endpoint} ")

# @bp_main.after_request
# def after_request(response):
#     logger_bp_main.info(f"---- after_request --- ")
#     if hasattr(g, 'db_session'):
#         wrap_up_session(logger_bp_main, g.db_session)
#     return response

@bp_main.route("/", methods=["GET","POST"])
def home():
    logger_bp_main.info(f"-- in home page route --")
    # df_users = create_df_from_db_table_name('users')
    # logger_bp_main.info(df_users)

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

@bp_main.route('/user_csv_documentation', methods = ['GET', 'POST'])
def user_csv_documentation():
    logger_bp_main.info(f"-- in user_csv_documentation route --")
    return render_template('main/user_csv_documentation.html')

@bp_main.route('/what_sticks_video/<filename>', methods = ['GET', 'POST'])
def what_sticks_video(filename):
    logger_bp_main.info(f"-- in what_sticks_video route --")

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
