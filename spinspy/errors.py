## Create some error classes
## ------
class Error(Exception):
    """ Base class for exceptions in this module. """
    pass

class SillyHumanError(Error):
    """ Exception raised when the human does something silly.
        
        Attributes:
            msg -- explanation of the error"""

    def __init__(self, msg):
        self.msg = msg
        print(msg)
##------