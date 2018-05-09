from flask import Flask, jsonify, request
from sqlalchemy.sql.expression import func

import models

app = Flask(__name__)

session = models.Session()


@app.route("/history/<int:note_id>/")
def note_history(note_id):

    note_history = session.query(models.Note).filter_by(id=note_id).all()

    return jsonify([note.serialize for note in note_history])


@app.route('/')
@app.route("/notes/")
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


@app.route("/note/<int:note_id>/")
def get_note(note_id):
    subquery = session.query(models.Note.id,
                             func.max(models.Note.version).\
                             label('latest_version')).\
                             group_by(models.Note.id).\
                             filter(models.Note.id==note_id).\
                             subquery()

    result = session.query(models.Note).\
                           filter(models.Note.id==subquery.c.id).\
                           filter(models.Note.version==subquery.c.latest_version).\
                           filter(models.Note.deleted==False).\
                           one_or_none()

    if result is None:
        return jsonify({'error': "Note doesn't exist"})
    else:
        return jsonify(result.serialize)


@app.route("/create/", methods=['POST'])
def add_note():

    # TODO: add data validation

    data = request.get_json()

    new_note = models.Note(title=data['title'], content=data['content'])
    session.add(new_note)
    session.commit()

    return jsonify(data)
