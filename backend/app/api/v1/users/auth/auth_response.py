from fastapi.responses import JSONResponse

class AuthResponse(JSONResponse):
    def __init__(self, content: dict, tokens: dict, **kwargs):
        """
        Initializes the response with the given content and tokens.
        The tokens will be set as httpOnly cookies.
        """
        super().__init__(content=content, **kwargs)
        self.set_auth_cookies(tokens)

    def set_auth_cookies(self, tokens: dict):
        self.set_cookie(
            key="_at",
            value=tokens.access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60,
            path="/",
            domain="localhost"
        )
        self.set_cookie(
            key="_rt",
            value=tokens.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
            path="/",
            domain="localhost"
        )
        
        
class LogoutResponse(JSONResponse):
    def __init__(self, content: dict, **kwargs):
        super().__init__(content=content, **kwargs)
        self.clear_auth_cookies()

    def clear_auth_cookies(self):
        self.set_cookie(
            key="_at",
            value="",
            max_age=0,
            path="/",
            domain="localhost",
            httponly=True,
            secure=False
        )
        self.set_cookie(
            key="_rt",
            value="",
            max_age=0,
            path="/",
            domain="localhost",
            httponly=True,
            secure=False
        )