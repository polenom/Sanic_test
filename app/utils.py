import hashlib



def getPass( password: str, salt: str) -> str | None:
    if password:
        return hashlib.sha512((salt+password).encode()).hexdigest()



