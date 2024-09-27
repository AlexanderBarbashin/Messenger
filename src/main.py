"""Project main file. Used to run FastAPI app."""
import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from config import APP_PORT
from medias.router import router as medias_router
from tweets.router import router as tweets_router
from users.router import router as users_router

app = FastAPI(title='My Twitter')

app.include_router(medias_router)
app.include_router(tweets_router)
app.include_router(users_router)

app.mount('/static', StaticFiles(directory='static'))
app.mount('', StaticFiles(directory='static', html=True))

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=int(APP_PORT))
