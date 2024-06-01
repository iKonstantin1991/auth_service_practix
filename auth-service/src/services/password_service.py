import hashlib


class PasswordService:
    def verify_password(self, salt: str, plain_password: str, hashed_password: str):
        return self.get_password_hash(salt, plain_password) == hashed_password

    def get_password_hash(self, salt: str, password: str):
        return hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()


password_service: PasswordService | None = None


async def get_password_service() -> PasswordService:
    return password_service
