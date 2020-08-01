from database import Base
from sqlalchemy import create_engine
from sqlalchemy import Column, MetaData, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

class Author(Base):
    __tablename__ = 'authors'

    auth_id = Column(String(60), nullable=False, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Author(auth_id='%s', name='%s')>" % (self.auth_id, self.name)

class Book(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True)
    isbn = Column(String, unique=True)
    title = Column(String)
    year = Column(Integer)
    author0 = Column(String(60), ForeignKey('authors.auth_id'))
    author1 = Column(String(60), ForeignKey('authors.auth_id'))

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    review_text = Column(Text)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    time = Column(DateTime(timezone=True), server_default=func.now())