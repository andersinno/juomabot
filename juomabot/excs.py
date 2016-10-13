class Problem(Exception):
    """
    User-visible exception
    """

    def __init__(self, message, code=None, icon=':exclamation:'):
        """
        :param message: The error message
        :type message: str
        :param code: An internal error code, for ease of testing
        :type code: str|None
        :param icon: The slack emoji to prepend to the message
        :type icon: str
        """
        super(Problem, self).__init__(message)
        self.code = code
        self.icon = icon

    def as_slack(self):
        return "%s %s" % (
            self.icon,
            str(self),
        )
