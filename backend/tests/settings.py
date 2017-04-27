from aidex.settings import BASE_DIR

DEBUG = False
TESTING = True
DB_USER = "aidex"
DB_NAME = "aidex-test"
DB_PASSWORD = "aidex"
DB_HOST = "localhost"
DB_PORT = 5432
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

ALEMBIC_CONFIG = "{}/alembic.ini".format(BASE_DIR)
ALEMBIC_MIGRATIONS = "{}/migrations".format(BASE_DIR)
