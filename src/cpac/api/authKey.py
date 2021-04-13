import uuid


class AuthKey:
    key = None

    @staticmethod
    def generateKey():
        if not AuthKey.key:
            AuthKey.key = uuid.uuid1()
        return AuthKey.key

    @staticmethod
    def getKey():
        return AuthKey.key
