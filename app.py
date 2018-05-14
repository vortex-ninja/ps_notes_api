from flask import Flask, jsonify, request, url_for
from sqlalchemy.sql.expression import func
from functools import wraps

from errors import ID_ERROR, NO_HISTORY_ERROR, NO_NOTES_ERROR, NO_NOTE_ERROR
from errors import CREATE_ERROR, UPDATE_ERROR

import models

app = Flask(__name__)

# To make responses more readable when using command line tools like CURL
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

session = models.Session()


ALL_METHODS = ['PUT', 'PATCH', 'HEAD', 'GET', 'POST', 'OPTIONS', 'DELETE']

# Helper functions and decorators


def method_check(allowed_methods):
    """Decorator that checks if method is allowed for an endpoint"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in allowed_methods:
                return f(*args, **kwargs)
            else:
                return jsonify(
                    {
                        "error": "method not allowed",
                        "status": 405,
                        "allowed methods": allowed_methods
                    })

        return decorated_function
    return decorator


def get_note_by_id(note_id):
    """Returns the latest version of a note for a given id"""
    subquery = session.query(
                  models.Note.id,
                  func.max(models.Note.version).
                  label('latest_version')).\
                  group_by(models.Note.id).\
                  filter(models.Note.id == note_id).\
                  subquery()

    note = session.query(
              models.Note).\
              filter(models.Note.id==subquery.c.id).\
              filter(models.Note.version==subquery.c.latest_version).\
              filter(models.Note.deleted==False).\
              one_or_none()

    return note


@app.route("/history", methods=ALL_METHODS)
@method_check(['GET'])
def note_history():

    data = request.args
    if models.Note.validate_id(data):
        note_history = session.query(models.Note).filter(models.Note.id==data['id']).all()
        if note_history:
            return jsonify([note.serialize for note in note_history])
        else:
            return jsonify(NO_HISTORY_ERROR)
    else:
        return jsonify(ID_ERROR), 400


@app.route('/', methods=ALL_METHODS)
@app.route("/notes", methods=ALL_METHODS)
@method_check(['GET'])
def get_notes():

    # This subquery returns latest versions for all 'id's

    subquery = session.query(models.Note.id,
                             func.max(models.Note.version).
                             label('latest_version')).\
                             group_by(models.Note.id).\
                             subquery()

    # This query joins subquery with 'notes' table to get
    # only latest versions of all notes that are not deleted

    results = session.query(models.Note).\
                        filter(models.Note.id==subquery.c.id).\
                        filter(models.Note.version==subquery.c.latest_version).\
                        filter(models.Note.deleted==False).\
                        order_by(models.Note.id).\
                        all()

    if results is None:
        return jsonify(NO_NOTES_ERROR)
    else:
        return jsonify([note.serialize for note in results])


@app.route("/note", methods=ALL_METHODS)
@method_check(['GET'])
def get_note():

    data = request.args

    if models.Note.validate_id(data):
        note = get_note_by_id(data['id'])
        if note is None:
            return jsonify(NO_NOTE_ERROR)
        else:
            return jsonify(note.serialize)
    else:
        return jsonify(ID_ERROR), 400


@app.route("/create", methods=ALL_METHODS)
@method_check(['POST'])
def add_note():

    data = request.get_json()

    if models.Note.validate_create(data):
        new_note = models.Note(title=data['title'], content=data['content'])
        session.add(new_note)
        session.commit()
        return jsonify(new_note.serialize), 201
    else:
        return jsonify(CREATE_ERROR), 400


@app.route("/update", methods=ALL_METHODS)
@method_check(['POST'])
def update_note():

    data = request.get_json()

    if models.Note.validate_update(data):

        note_to_update = get_note_by_id(data['id'])

        new_title = data['title'] if 'title' in data else note_to_update.title
        new_content = data['content'] if 'content' in data else note_to_update.content

        if note_to_update is None:
            return jsonify(NO_NOTE_ERROR)
        else:
            updated_note = models.Note(id=note_to_update.id,
                                       title=new_title,
                                       content=new_content,
                                       created=note_to_update.created,
                                       version=note_to_update.version + 1)
            session.add(updated_note)
            session.commit()

        return jsonify(updated_note.serialize)

    else:
        return jsonify(UPDATE_ERROR), 400


@app.route("/delete", methods=ALL_METHODS)
@method_check(['POST', 'DELETE'])
def delete_note():

    data = request.get_json()

    if models.Note.validate_id(data):

        note_to_delete = get_note_by_id(data['id'])

        if note_to_delete is None:
            return jsonify(NO_NOTE_ERROR)
        else:
            note_to_delete.deleted = True
            session.commit()

        return jsonify(note_to_delete.serialize)

    else:
        return jsonify(ID_ERROR), 400
