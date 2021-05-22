import uuid


class AuthKey:
    key = None

    @staticmethod
    def generate_key():
        if not AuthKey.key:
            AuthKey.key = str(uuid.uuid1())
        return AuthKey.key

    @staticmethod
    def get_key():
        return AuthKey.key
