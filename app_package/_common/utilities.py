from ws_models import sess, engine, text, Users
import logging
from logging.handlers import RotatingFileHandler
import os


def wrap_up_session():
    print("- accessed wrap_up_session -")
    try:
        # perform some database operations
        sess.commit()
        print("- perfomed: sess.commit() -")
    except:
        sess.rollback()  # Roll back the transaction on error
        print("- perfomed: sess.rollback() -")
        raise
    finally:
        sess.close()  # Ensure the session is closed in any case
        print("- perfomed: sess.close() -")


def custom_logger(logger_filename):
    """
    Creates and configures a logger with both file and stream handlers.

    :param path_to_logger: Path to the directory where the log file will be stored.
    :param logger_filename: Filename for the log file.
    :return: Configured logger object.
    """
    # Formatter setup
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

    # Logger setup
    logger = logging.getLogger(logger_filename)
    logger.setLevel(logging.DEBUG)

    # File handler setup
    path_to_logs = os.path.join(os.environ.get('WEB_ROOT'), 'logs')
    file_handler = RotatingFileHandler(os.path.join(path_to_logs, logger_filename), mode='a', maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Stream handler setup
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter_terminal)
    logger.addHandler(stream_handler)

    return logger

