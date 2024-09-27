"""Project config file. Use to config FastAPI app."""
import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

APP_PORT = os.environ.get('APP_PORT')

DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('POSTGRES_PORT')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DB_NAME = os.environ.get('POSTGRES_NAME')

DB_HOST_TEST = os.environ.get('POSTGRES_HOST_TEST')
DB_PORT_TEST = os.environ.get('POSTGRES_PORT_TEST')
DB_USER_TEST = os.environ.get('POSTGRES_USER_TEST')
DB_PASSWORD_TEST = os.environ.get('POSTGRES_PASSWORD_TEST')
DB_NAME_TEST = os.environ.get('POSTGRES_NAME_TEST')

logger.add(
    'logs.log',
    rotation='1 week',
    compression='zip',
    level='INFO',
    format='{time} {level} {message}',
    backtrace=True,
    diagnose=True,
)
