"""Project main file. Used to run FastAPI app."""

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from python_advanced_diploma.src.config import APP_PORT, DEV
from python_advanced_diploma.src.exception_handlers import (
    add_attribute_error_exception_handler,
    add_integrity_error_exception_handler,
    add_no_result_found_exception_handler,
    override_validation_exception_handler,
)
from python_advanced_diploma.src.medias.medias_router import (
    router as medias_router,
)
from python_advanced_diploma.src.tweets.tweets_router import (
    router as tweets_router,
)
from python_advanced_diploma.src.users.users_router import (
    router as users_router,
)

app = FastAPI(title="My Twitter")

app.include_router(medias_router)
app.include_router(tweets_router)
app.include_router(users_router)

add_no_result_found_exception_handler(app)
add_attribute_error_exception_handler(app)
add_integrity_error_exception_handler(app)
override_validation_exception_handler(app)

if DEV:
    app.mount("/images", StaticFiles(directory="../../images"))
    app.mount(
        "",
        StaticFiles(directory="../static", html=True),
    )

DEFAULT_PORT = 8000
app_port = int(APP_PORT) if APP_PORT else DEFAULT_PORT

if __name__ == "__main__" and DEV:
    uvicorn.run("main:app", host="127.0.0.1", port=app_port)
