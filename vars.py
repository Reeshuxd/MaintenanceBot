from os import getenv

class Var:
    try:
        TOKEN = getenv("TOKEN")
        OWNER_ID = int(getenv("OWNER_ID"))
        MONGODB_URL = getenv("MONGODB_URL")
    except ValueError:
        print("Important Vars missing!")