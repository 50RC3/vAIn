# SQL/NoSQL database management

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class SQLDatabaseManager:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()
    
    def get_session(self):
        return self.Session()

    def execute_query(self, query):
        with self.get_session() as session:
            return session.execute(query)

    def commit_transaction(self, session):
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
