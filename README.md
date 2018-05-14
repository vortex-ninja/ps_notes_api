# ps_notes_api

### OVERVIEW
Basic REST API that manages notes created with Flask.

### NOTE
At the moment web service doesn't use in memory database as specified in requirements.

### DATABASE SETUP

- install PostgreSQL:
- using `psql` connect to the PostgreSQL server and create two databases with

`CREATE DATABASE <dbname>;`

`CREATE DATABASE <test_dbname>;`

Application uses environment variable `DATABASE_URL` to connect to the database.
Format of the `DATABASE_URL` is

`postgresql+psycopg2://<user>:<password>@localhost/<dbname>`

Please set the `DATABASE_URL` environment variable to this value. If you're going to use pipenv to run the app,
which I recommend, put the `DATABASE_URL` in `.env` file and pipenv will load it automatically

### HOW TO RUN

- clone this repo with `git clone`
- add the `DATABASE_URL` to `.env` file
- run app with `pipenv run flask run` (this will create virtual environment and download all dependencies)

### HOW TO TEST

- change `DATABASE_URL` in `.env` file to point to test database
- run tests with `pipenv run pytest`

### ENDPOINTS
1. `/`, `/notes`
 - returns a list of notes,
 - accessible by GET request,
2. `/note?<id>`
 - returns latest version of a note for a given `id`
 - accessible by GET request
 - accepts id as a query parameter
3. `/history`
 - returns all versions of a note for given id,
 - accessible by GET request,
 - accepts id as query parameter,
4. `/create`
 - adds a note to the database,
 - accessible by POST request,
 - it requires title and content (both fields are required) in POST data
5. `/update`
 - creates a new version of a note, id stays the same, version number increases
 - accessible by POST request
 - it requires id and either title or content
6. `/delete`
 - deletes a note, technically it marks a note as deleted so /note and /notes won't return it
 - accessible by POST and DELETE requests
 - id is mandatory and should be sent in the body of the request
 
### EXAMPLE USING CURL

Examples assume Flask development server runs on default 127.0.0.1:5000

##### CREATING A NOTE
`curl -X POST -H "Content-Type: application/json" -d '{"title":"note","content":"note_content"}' http://127.0.0.1:5000/create`

This will create a note, save it in a database and return it as a response when succesfull.

##### UPDATING A NOTE

`curl -X POST -H "Content-Type: application/json" -d '{"id":"1", "title": "updated_note", "content": "updated_content"}' http://127.0.0.1:5000/update`

##### DELETING A NOTE
`curl -X POST -H "Content-Type: application/json" -d '{"id":"1"}' http://127.0.0.1:5000/delete`

or

`curl -X DELETE -H "Content-Type: application/json" -d '{"id":"1"}' http://127.0.0.1:5000/delete`
##### GETTING ALL NOTES
`curl -X GET http://127.0.0.1:5000/notes`
##### GETTING A NOTE
`curl -X GET http://127.0.0.1:5000/note?id=1`

This will return a note with id 1.

##### GETTING HISTORY OF A NOTE
`curl -X GET http://127.0.0.1:5000/history?id=1`

This will return history (all versions) of a note with id 1.
