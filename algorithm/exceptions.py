class LocationNotFoundException(Exception):
    """Exception raised when a location is not found in the database."""
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg
