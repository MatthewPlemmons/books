### Book Review
A web app for writing book reviews.  View demo [here](https://book-project-002.herokuapp.com/).

#### Installation
Download the requirements.

```
$ pip3 install -r requirements.txt
```

Create a free Heroku PostgreSQL database.  Then set up the environment variables `FLASK_APP` and `DATABASE_URL`.  `FLASK_APP` should be assigned the application.py file, and `DATABASE_URL` should be assigned the URI of the Heroku database.  To get the database URI, find the Database Credentials section in the database's settings and then click `View Credentials...`

```
$ export FLASK_APP=application.py
$ export DATABASE_URL=<Database URI>
```

Create an account on https://www.goodreads.com/ and get an API key.

```
$ export GOODREADS_KEY=<Goodreads API Key>
```

Run the `import.py` script, which will set up the tables on the new PostgreSQL database and then populate them with data from the `books.csv` file.  This can take a couple minutes depending on how many books are in the csv.  The script will print the book titles as it inserts them into the database.

Once that is complete, the app should be ready to run.
```
$ flask run
```
Flask will then report what URL the application is being served on in the terminal.

#### Usage
Navigate to the URL given by Flask.  Register a new account, then log in to access the search page.  Type in a book title, author, or ISBN, and click the Search button to retrieve a list of books matching the search query.

#### API
An API is provided that serves JSON formatted data on each book in the database.  To retrieve data from the API add `/api/ISBN` to the end of the URL Flask is serving the app from, where `ISBN` is the book's actual ISBN.  For example, say and we want to retrieve data about a book whose ISBN is 0380795272, and the app is running on `http://127.0.0.1:5000`, we can use the `curl` command in the terminal:
```
$ curl 127.0.0.1:5000/api/0380795272
```
The API should reply with JSON like the following:
```
{"title": "Krondor: The Betrayal", "author": "Raymond E. Feist", "year": 1998, "isbn": "0380795272", "review_count": 13821, "average_score": 3.85}
```

