import csv
import os

from database import init_db, db
from models import Author, Book, Review
from uuid import uuid4


def add_authors_and_books():
    """
    Pull data from `books.csv` to insert into the `authors`
    and `books` database tables.
    """

    # Keep track of authors to avoid duplicate inserts
    author_names = {}
    authors = []
    books = []

    with open("books.csv") as f:

        next(f) # Skip csv header
        reader = csv.reader(f)

        for isbn, title, author, year in reader:
            author1 = ""
            author1_id = None

            if "," in author:
                author, author1 = author.split(", ")

                if author1 not in author_names:
                    author1_id = str(uuid4())
                    author_names[author1] = author1_id
                    authors.append(Author(auth_id=author1_id, name=author1))

            if author not in author_names:
                author0_id = str(uuid4())
                author_names[author] = author0_id
                authors.append(Author(auth_id=author0_id, name=author))

            books.append(Book(
                            isbn=isbn, 
                            title=title, 
                            year=year, 
                            author0=author0_id, 
                            author1=author1_id))

    db.add_all(authors)
    db.commit()
    db.add_all(books)
    db.commit()

def main():
    """
    Create database tables and then populate them with data from
    the `books.csv` file.
    """

    init_db()
    add_authors_and_books()


if __name__ == "__main__":
    main()
    print('Database tables successfully created')

