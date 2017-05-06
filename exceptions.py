class GracefulExit(Exception):
    pass


def signal_handler(signum, frame):
    raise GracefulExit()
