from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os


engine = create_engine(os.environ["DATABASE_URL"], echo=False)
Base = declarative_base()


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, primary_key=True, default=1)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(DateTime(timezone=True), server_default=func.now())
    deleted = Column(Boolean, default=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'version': self.version,
            'title': self.title,
            'content': self.content,
            'created': self.created.strftime('%Y/%m/%d %H:%M:%S'),
            'modified': self.modified.strftime('%Y/%m/%d %H:%M:%S'),
            'deleted': self.deleted,
        }

    def __str__(self):
        return 'Note (id={}, version={}, deleted={})'.format(self.id,
                                                             self.version,
                                                             self.deleted)

    @staticmethod
    def validate_id(data):
        if len(data) == 1 and 'id' in data.keys():
            return True
        return False

    @staticmethod
    def validate_create(data):
        to_compare = set(['title', 'content'])
        if data.keys() == to_compare:
            return True
        return False

    @staticmethod
    def validate_update(data):
        to_compare = set(['id', 'title', 'content'])
        data_set = set(data.keys())

        if data_set <= to_compare and 'id' in data_set and len(data_set) > 1:
            return True
        return False

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
