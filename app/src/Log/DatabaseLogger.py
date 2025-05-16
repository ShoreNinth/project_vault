import time

def transaction_logger():
    try:
        with open(file='./log/db.txt', mode='a', encoding='utf-8') as db_log:
            data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    except FileNotFoundError:
        print('file not found')


# def login_activity():
#     with open(file='log.txt',mode='a', encoding='utf-8') as f:
#         f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
# def register_activity():
#     with open(file='log.txt',mode='a', encoding='utf-8') as f:
#         f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
