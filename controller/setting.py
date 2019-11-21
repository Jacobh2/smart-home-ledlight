from os import getenv


class Setting(object):
    def __init__(self):

        self.AUTH_DOMAIN = getenv("AUTH_DOMAIN")
        self.API_AUDIENCE = getenv("API_AUDIENCE")
        self.ALGORITHMS = ["RS256"]

        self.TEMPLATE_FOLDER = "public/html"
        self.STATIC_FOLDER = "public"
        self.STATIC_URL_PATH = ""

        self.HTTP_ADDRESS = "0.0.0.0"
        self.HTTP_PORT = 8080

        self.THIS_ROOM = getenv("THIS_ROOM", "hallway")

        self.PIN_RED = getenv("PIN_RED", 24)
        self.PIN_GREEN = getenv("PIN_GREEN", 22)
        self.PIN_BLUE = getenv("PIN_BLUE", 17)
