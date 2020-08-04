import os
import requests
import json

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, err
from database import db


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up Goodreads API Key
key = os.getenv("GOODREADS_KEY")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        query = request.form.get("search")

        if not query:
            flash("Enter a book title, author, or ISBN to search for.")
            return render_template("search.html")

        if query[0].isalpha():
            query = query.title() # Capitalize each word in a string

        books = db.execute("SELECT *, authors.name FROM books INNER JOIN \
                            authors ON books.author0=authors.auth_id WHERE \
                            books.title LIKE :a OR \
                            authors.name LIKE :a OR \
                            books.isbn LIKE :a",
                            {"a": "%"+query+"%"}).fetchall()

        return render_template("search.html", books=books)
    return render_template("search.html")


@app.route("/books/<int:book_id>", methods=["GET", "POST"])
@login_required
def book(book_id):
    """Lists details about a single book."""

    user_review_exists = False
    user_id = session['user_id']
    review_id = 0

    if request.method == "GET":
        user_id = session['user_id']
        b = db.execute("SELECT *, authors.name FROM books INNER JOIN \
                        authors ON books.author0=authors.auth_id WHERE \
                        books.book_id=:id", {"id": book_id}).fetchone()
        #if book is None:
            # Display error message
        reviews = db.execute("SELECT *, users.username FROM \
                            reviews INNER JOIN users ON \
                            reviews.user_id=users.id WHERE book_id=:book_id",
                            {"book_id": book_id}).fetchall()

        # Use ISBN to retrieve book's json data from the Goodreads API
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                            params={"key": key, "isbns": b.isbn})
        res = res.json()
        avg_rating = res["books"][0]["average_rating"]
        work_ratings_count = res["books"][0]["work_ratings_count"]

        book = dict(b)
        book.update({"review_avg": avg_rating,
                    "work_ratings_count": work_ratings_count})

        # Check if user has already reviewed this book
        for review in reviews:
            if review.user_id == user_id:
                user_review_exists = True
                break
        
        return render_template("books.html", 
                                book=book, 
                                reviews=reviews, 
                                user_id=user_id, 
                                user_review_exists=user_review_exists)
    
    if request.method == "POST":
        user_review_exists = False
        user_id = session['user_id']

        star_rating = request.form.get("rate")
        review_text = request.form.get("reviewText")

        book = db.execute("SELECT *, authors.name FROM books INNER JOIN \
                            authors ON books.author0=authors.auth_id WHERE \
                            books.book_id=:id", {"id": book_id}).fetchone()
        reviews = db.execute("SELECT *, users.username FROM reviews INNER JOIN \
                            users ON reviews.user_id=users.id WHERE \
                            book_id=:book_id", {"book_id": book_id}).fetchall()

        for review in reviews:
            if review.user_id == user_id:
                review_id = review[0]
                user_review_exists = True
                break

        if user_review_exists:
            db.execute("UPDATE reviews SET \
                    rating=:rating, review_text=:review_text WHERE id=:id",
                    {"rating": star_rating,
                    "review_text": review_text,
                    "id": review_id})
        else:
            db.execute("INSERT INTO \
                    reviews (rating, review_text, book_id, user_id) VALUES \
                    (:rating, :review_text, :book_id, :user_id)",
                    {"rating": star_rating, "review_text": review_text,
                    "book_id": book_id, "user_id": user_id})
        db.commit()

        # Retrieve the reviews again to provide the new, or updated, review to the web page.
        reviews = db.execute("SELECT *, users.username FROM reviews INNER JOIN \
                            users ON reviews.user_id=users.id WHERE \
                            book_id=:book_id", {"book_id": book_id}).fetchall()
        return render_template("books.html", book=book, reviews=reviews, 
                                user_id=user_id, user_review_exists=True)

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):

    try:
        book = db.execute("SELECT *, authors.name FROM books INNER JOIN \
                            authors ON books.author0=authors.auth_id WHERE \
                            books.isbn=:isbn", {"isbn": isbn}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                            params={"key": key, "isbns": book.isbn})
    except:
        return "404: isbn not found"
    
    res = res.json()
    avg_rating = float(res["books"][0]["average_rating"])
    work_ratings_count = res["books"][0]["work_ratings_count"]

    b = {"title": book.title,
        "author": book.name,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": work_ratings_count,
        "average_score": avg_rating
        }

    book = json.dumps(b)
    return book

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Must provide username.")
            return render_template("login.html")

        password = request.form.get("password")
        if not password:
            flash("Must provide password.")
            return render_template("login.html")

        usr = db.execute("SELECT * FROM users WHERE username = :username", 
                            {"username": username}).fetchone()

        if usr is None or not check_password_hash(usr.password, password):
            flash("Invalid username and/or password.")
            return render_template("login.html")

        session["user_id"] = usr.id
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        usr = db.execute("SELECT * FROM users WHERE username = :username", 
                            {"username": username}).fetchone()

        # If db.execute returns a value to `usr` then the username is taken
        if usr is not None:
            flash("Name already in use.")
            return render_template("register.html")
 
        password = request.form.get("password")
        if not password or len(password) < 5:
            flash("Password must contain at least 5 characters.")
            return render_template("register.html")

        passhash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, password) VALUES \
            (:username, :password)",
            {"username": username, "password": passhash})
            
        db.commit()
        return redirect("/")
    
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user id
    session.clear()
    return redirect("/")
