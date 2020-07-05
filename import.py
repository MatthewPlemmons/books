import csv
import os

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, MetaData, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import func


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_db_tables():
    """Create database tables for books, authors, users, and reviews."""

    metadata = MetaData()
    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('username', String, nullable=False),
        Column('password', String, nullable=False),
        )

    authors = Table('authors', metadata,
        Column('auth_id', Integer, primary_key=True),
        Column('name', String),
        )

    books = Table('books', metadata,
        Column('book_id', Integer, primary_key=True),
        Column('isbn', String),
        Column('title', String),
        Column('year', Integer),
        Column('author0', Integer, ForeignKey('authors.auth_id')),
        Column('author1', Integer, ForeignKey('authors.auth_id')),
        )

    reviews = Table('reviews', metadata,
        Column('id', Integer, primary_key=True),
        Column('rating', Integer),
        Column('review_text', Text),
        Column('book_id', Integer, ForeignKey('books.book_id')),
        Column('user_id', Integer, ForeignKey('users.id')),
        Column('time', DateTime(timezone=True), server_default=func.now()),
        )

    metadata.create_all(engine)

def add_authors():
    """
    Pull author names from the `books.csv` file to insert into
    the `authors` database table.
    """

    authors = []
    with open("books.csv") as f:
        # Skip header
        next(f)
        reader = csv.reader(f)
        for isbn, title, author, years in reader:
            author1 = ""
            if "," in author:
                author, author1 = author.split(", ")
                if author1 not in authors:
                    authors.append(author1)
            if author not in authors:
                authors.append(author)

    for author in authors:
         db.execute("INSERT INTO authors (name) VALUES (:name)",
                     {"name": author})
    db.commit()

def main():
    """
    Create database tables and then populate them with data from
    the `books.csv` file.
    """

    create_db_tables()
    add_authors()

    with open("books.csv") as f:
        next(f)
        reader = csv.reader(f)
        for isbn, title, author, year in reader:
            if "," in author:
                author0, author1 = author.split(", ")
            else:
                author0, author1 = author, ""

            # Need to send author0 and author1 to the `authors` table and retrieve
            # the correct author ids, then those integer ids get inserted into the `books` table.
            auth_id0 = db.execute("SELECT auth_id FROM authors WHERE name = :name", {"name": author0}).fetchone()
            if len(author1) > 0:
                auth_id1 = db.execute("SELECT auth_id FROM authors WHERE name = :name", {"name": author1}).fetchone()
                db.execute("INSERT INTO books (isbn, title, year, author0, author1) VALUES (:isbn, :title, :year, :author0, :author1)",
                    {"isbn": isbn, "title": title, "year": year, "author0": auth_id0[0], "author1": auth_id1[0]})
            else:
                db.execute("INSERT INTO books (isbn, title, year, author0) VALUES (:isbn, :title, :year, :author0)",
                    {"isbn": isbn, "title": title, "year": year, "author0": auth_id0[0]})

            #print(auth_id0[0])
            print(title)
        db.commit()

if __name__ == "__main__":
    main()