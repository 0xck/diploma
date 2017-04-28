# start server
from app import app
# for correct stop
import signal
from sys import exit
from exceptions import GracefulExit, signal_handler

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except (KeyboardInterrupt, GracefulExit):
        print('STOPSIG')
        exit()
