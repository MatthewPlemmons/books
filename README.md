### Book Review
A web app for writing book reviews.

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

#### Usage
Register a new account, then log in to access the search page.  Type in a book title, author, or ISBN and click the Search button to retrieve a list of books matching the search query. 
