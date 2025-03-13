import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi_csrf_protect import CsrfProtect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .api.v1.router import api_router
from .core.config import (
    get_settings,
    get_csrf_settings
)
from .core.exceptions import (
    custom_exception_handler, CustomException,
    validation_exception_handler
)
from .middlewares.security_headers import SecurityHeadersMiddleware

# from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

settings = get_settings()
csrf_settings = get_csrf_settings()
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True) 


def create_app() -> FastAPI:
    """Initialize FastAPI application."""
    app = FastAPI()
    configure_logging()
    configure_cors(app)
    configure_middlewares(app)
    configure_rate_limiter(app)
    configure_csrf(app)
    configure_routes(app)
    configure_exception_handlers(app)
    return app


def configure_logging():
    """Configure logging settings."""
    log_file = LOGS_DIR / "app.log"
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging is configured.")


def configure_csrf(app: FastAPI):
    """Configure CSRF protection using FastAPI-CSRF-Protect."""
    @CsrfProtect.load_config
    def get_csrf_config():
        return csrf_settings

    # csrf = CsrfProtect(app)
    # app.state.csrf_protect = csrf
    logging.info("CSRF Protection is configured.")


def configure_cors(app: FastAPI):
    """Configure CORS settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
def configure_middlewares(app: FastAPI):
    """Configure additional security middlewares."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    # app.add_middleware(HTTPSRedirectMiddleware)
    
    
def configure_rate_limiter(app: FastAPI):
    """Configure API rate limiting."""
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        return JSONResponse(status_code=429, content={"message": "Rate limit exceeded"})


def configure_routes(app: FastAPI):
    """Include API routes."""
    app.include_router(api_router, prefix="/api/v1")


def configure_exception_handlers(app: FastAPI):
    """Configure exception handlers."""
    app.add_exception_handler(
        CustomException,
        custom_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )

app = create_app()