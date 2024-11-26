from sqlalchemy import create_engine

# database configuration
engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/mias')


def get_db_connection():
    return engine.connect()
