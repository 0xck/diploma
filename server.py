# start server
from app import app
from config import app_listen, app_port
# for correct stop
import signal
from sys import exit
from exceptions import GracefulExit, signal_handler

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        app.run(host=app_listen, port=app_port, debug=True)
    except (KeyboardInterrupt, GracefulExit):
        print('STOPSIG')
        '''
        here something for DB done
        '''
        exit()
