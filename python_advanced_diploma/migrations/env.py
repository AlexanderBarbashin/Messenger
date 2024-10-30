"""Project migrations env file."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from python_advanced_diploma.src.config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)
from python_advanced_diploma.src.database import Base
from python_advanced_diploma.src.medias.medias_models import (  # noqa: F401
    TweetMedia,
)
from python_advanced_diploma.src.tweets.tweets_models import (  # noqa: F401
    Like,
    Tweet,
)
from python_advanced_diploma.src.users.users_models import (  # noqa: F401
    Follow,
    User,
)

config = context.config
section = config.config_ini_section
if DB_HOST:
    config.set_section_option(section, "DB_HOST", DB_HOST)
if DB_PORT:
    config.set_section_option(section, "DB_PORT", DB_PORT)
if DB_USER:
    config.set_section_option(section, "DB_USER", DB_USER)
if DB_PASSWORD:
    config.set_section_option(section, "DB_PASSWORD", DB_PASSWORD)
if DB_NAME:
    config.set_section_option(section, "DB_NAME", DB_NAME)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()