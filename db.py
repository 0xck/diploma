# DB main settings
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# choosing DB engine
db_engine = create_engine('sqlite:///db.sqlite')
# making DB session and binding one with engine
db_session = scoped_session(sessionmaker(bind=db_engine))
# define DB type
DB = declarative_base()
# possibility to make queries to DB
DB.query = db_session.query_property()
