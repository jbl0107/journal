class UserAlreadyExists(Exception):
    '''El usuario ya existe'''

    def __init__(self, username):
        self.username = username
        self.message = f"El usuario '{username}' ya existe"
        super().__init__(self.message)