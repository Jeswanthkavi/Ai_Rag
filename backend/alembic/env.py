from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

from app.config import settings
from app.database import Base

# Import all SQLAlchemy models so Alembic can detect them
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.message import Message


# ---------------------------------------------------------
# Alembic configuration
# ---------------------------------------------------------

config = context.config


# ---------------------------------------------------------
# Build MySQL database URL
# ---------------------------------------------------------

database_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.mysql_user,
    password=settings.mysql_password,
    host=settings.mysql_host,
    port=settings.mysql_port,
    database=settings.mysql_database,
)


config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(
        hide_password=False
    ),
)


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


# ---------------------------------------------------------
# SQLAlchemy metadata
#
# Alembic compares this metadata with the actual
# MySQL database when using --autogenerate.
# ---------------------------------------------------------

target_metadata = Base.metadata


# ---------------------------------------------------------
# Offline migrations
#
# This generates SQL without directly connecting
# to the database.
# ---------------------------------------------------------

def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# Online migrations
#
# This connects directly to MySQL and applies
# migrations.
# ---------------------------------------------------------

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# Run correct migration mode
# ---------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()