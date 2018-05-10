from flask import Flask, jsonify, request
from sqlalchemy.sql.expression import func

import models

app = Flask(__name__)

session = models.Session()


# Helper functions

def get_note_by_id(note_id):
    subquery = session.query(models.Note.id,
                             func.max(models.Note.version).\
                             label('latest_version')).\
                             group_by(models.Note.id).\
                             filter(models.Note.id==note_id).\
                             subquery()

    note = session.query(models.Note).\
                         filter(models.Note.id==subquery.c.id).\
                         filter(models.Note.version==subquery.c.latest_version).\
                         filter(models.Note.deleted==False).\
                         one_or_none()

    return note



@app.route("/history/<int:note_id>")
def note_history(note_id):

    note_history = session.query(models.Note).filter_by(id=note_id).all()

    return jsonify([note.serialize for note in note_history])


@app.route('/')
@app.route("/notes")
def get_notes():
    subquery = session.query(models.Note.id,
                             func.max(models.Note.version).
                             label('latest_version')).\
                             group_by(models.Note.id).\
                             subquery()

    results = session.query(models.Note).\
                        filter(models.Note.id==subquery.c.id).\
                        filter(models.Note.version==subquery.c.latest_version).\
                        filter(models.Note.deleted==False).\
                        order_by(models.Note.id).\
                        all()

    return jsonify([note.serialize for note in results])


@app.route("/note/<int:note_id>")
def get_note(note_id):

    note = get_note_by_id(note_id)

    if note is None:
        return jsonify({'error': "Note doesn't exist"})
    else:
        return jsonify(note.serialize)


@app.route("/create", methods=['POST'])
def add_note():

    # TODO: add data validation

    data = request.get_json()

    new_note = models.Note(title=data['title'], content=data['content'])
    session.add(new_note)
    session.commit()

    return jsonify(data)


@app.route("/update", methods=['POST'])
def update_note():

    # TODO: add data validation

    data = request.get_json()

    note_to_update = get_note_by_id(data['id'])

    if note_to_update is None:
        return jsonify({'error': "Note doesn't exist."})
    else:
        updated_note = models.Note(id=note_to_update.id,
                                   title=data['title'],
                                   content=data['content'],
                                   created=note_to_update.created,
                                   version=note_to_update.version + 1)
        session.add(updated_note)
        session.commit()

    return jsonify(updated_note.serialize)


@app.route("/delete", methods=['POST'])
def delete_note():

    # TODO: add data validation

    data = request.get_json()

    note_to_delete = get_note_by_id(data['id'])

    if note_to_delete is None:
        return jsonify({'error': "Note doesn't exist."})
    else:
        note_to_delete.deleted = True
        session.commit()

    return jsonify(note_to_delete.serialize)