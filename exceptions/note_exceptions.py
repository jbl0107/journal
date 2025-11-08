class UserNotFound(Exception):
    '''El usuario asociado a una Note no existe'''

    def __init__(self, user_id:int):
        self.user_id = user_id
        self.message = f'El usuario con id {user_id} no existe'
        super().__init__(self.message)