class UserError(Exception):
    def __init__(self, message, status_code=404):
        self.message = message
        self.status_code = status_code
