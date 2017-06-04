# especial exception for making deal with signals
class GracefulExit(Exception):
    # just making own exception class
    pass


def signal_handler(signum, frame):
    # raises exception
    raise GracefulExit()
