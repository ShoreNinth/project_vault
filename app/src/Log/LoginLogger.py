import time


def login_logger():
    try:
        with open('./log/login', 'rw') as db_log:
            data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    except FileNotFoundError:
        print('file not found')
