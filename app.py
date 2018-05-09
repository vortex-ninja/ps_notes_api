from flask import Flask, jsonify

import models

app = Flask(__name__)

session = models.Session()


@app.route("/history/<int:note_id>/")
def note_history(note_id):

    note_history = session.query(models.Note).filter_by(id=note_id).all()

    return jsonify([note.serialize for note in note_history])
