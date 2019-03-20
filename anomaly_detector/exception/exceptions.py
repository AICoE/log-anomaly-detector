




class factStoreEnvVarNotSetException(Exception):
    def __init__(self, msg="fact store url env var not set"):
        self.message = msg