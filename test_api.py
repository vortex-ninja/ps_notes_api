import requests
import models
from datetime import datetime
from errors import NO_NOTE_ERROR, ID_ERROR


session = models.Session()
URL = 'http://127.0.0.1:5000/'

# A helper function to clean 'notes' table in database


def flush_db(session):
    notes = session.query(models.Note).all()
    for note in notes:
        session.delete(note)

    session.commit()


class TestCreate:
    """Class aggregating methods to test creating notes functionality"""

    create_url = URL + 'create/'

    def setup_method(self):
        flush_db(session)

    def test_succesfull_create(self):

        r = requests.post(TestCreate.create_url, json={
                          'title': 'test_note1',
                          'content': 'test_content1'
                          })

        query = session.query(models.Note)

        assert r.status_code == 201
        assert query.count() == 1
        assert query[0].title == 'test_note1'
        assert query[0].content == 'test_content1'

    def test_create_invalid_data(self):

        # Missing parameter 'content'
        r = requests.post(TestCreate.create_url, json={
                          'title': 'test_note2'
                          })

        query = session.query(models.Note).all()

        assert r.status_code == 400
        assert len(query) == 0

        # Additional parameter 'id'
        r = requests.post(TestCreate.create_url, json={
                          'title': 'test_note2',
                          'content': 'test_content2',
                          'id': 1
                          })

        query = session.query(models.Note)

        assert r.status_code == 400
        assert query.count() == 0


class TestUpdate:
    """Class aggregating methods to test updating notes functionality"""

    update_url = URL + 'update/'

    def setup_method(self):
        flush_db(session)

        # Add a note with a creation date in a past to check
        # if properties Note.created and Note.modified
        # are filled in correctly

        test_date = datetime(2018, 5, 14)

        note1 = models.Note(title='test_note1',
                            content='test_content1',
                            created=test_date,
                            modified=test_date)

        session.add(note1)
        session.commit()
        TestUpdate.note_id = note1.id

    def test_succesful_update(self):

        r = requests.post(TestUpdate.update_url, json={
                          'id': TestUpdate.note_id,
                          'title': 'updated_test_note1',
                          'content': 'updated_test_content1'
                          })

        query = session.query(models.Note).filter(
                                models.Note.id==TestUpdate.note_id)

        assert r.status_code == 200
        assert query.count() == 2

        note1_1 = query.all()[0]
        note1_2 = query.all()[1]

        assert note1_1.id == note1_2.id
        assert note1_1.version == 1
        assert note1_2.version == 2

        assert note1_1.created == note1_2.created
        assert note1_1.modified < note1_2.modified

    def test_update_with_missing_data(self):

        # Missing 'title' or 'content' argument
        r = requests.post(TestUpdate.update_url, json={
                          'id': TestUpdate.note_id
                          })

        query = session.query(models.Note).filter(
                                models.Note.id==TestUpdate.note_id)

        assert r.status_code == 400
        assert query.count() == 1

    def test_update_with_invalid_data(self):

        # 'created' is not a valid parameter
        # program fills that property automatically

        r = requests.post(TestUpdate.update_url, json={
                          'id': TestUpdate.note_id,
                          'title': 'updated_test_note1',
                          'created': '2008 12 1'
                          })

        query = session.query(models.Note).filter(
                                models.Note.id==TestUpdate.note_id)

        assert r.status_code == 400
        assert query.count() == 1


class TestDelete:
    """Class aggregating methods to test deleting notes functionality"""
    delete_url = URL + 'delete/'

    def setup_method(self):
        flush_db(session)

        note1 = models.Note(title='test_note1', content='test_content1')

        session.add(note1)
        session.commit()
        TestDelete.note_id = note1.id

    def test_delete(self):

        r = requests.post(TestDelete.delete_url, json={
                          'id': TestDelete.note_id
                          })

        note = session.query(models.Note).one_or_none()

        assert r.status_code == 200
        assert note.deleted

    def test_delete_with_invalid_data(self):

        # /delete endpoint accepts only one parameter: 'id'

        r = requests.post(TestDelete.delete_url, json={
                          'id': TestDelete.note_id,
                          'title': 'test_note1'
                          })

        note = session.query(models.Note).one_or_none()

        assert r.status_code == 400
        assert note.deleted == False


class TestViews:
    """Class aggregating methods to test retrieving notes functionality"""

    def setup_method(self):

        # Adds two notes both with two versions
        # One marked as deleted

        flush_db(session)
        note1_1 = models.Note(title='test_note1', content='test_content1')
        note2_1 = models.Note(title='test_note2', content='test_content2')
        session.add_all([note1_1, note2_1])
        session.commit()

        note1_2 = models.Note(id=note1_1.id,
                              version=2,
                              title='updated_test_note1',
                              content='updated_test_content1',
                              deleted=True)

        note2_2 = models.Note(id=note2_1.id,
                              version=2,
                              title='updated_test_note2',
                              content='updated_test_content2')

        session.add_all([note1_2, note2_2])
        session.commit()

        TestViews.note1_id = note1_1.id
        TestViews.note2_id = note2_1.id

    def test_history(self):

        r = requests.get(URL + 'history/', params={'id': TestViews.note1_id})

        notes = r.json()

        assert len(notes) == 2
        assert notes[0]['created'] == notes[1]['created']
        assert notes[0]['version'] == 1
        assert notes[1]['version'] == 2
        assert r.status_code == 200

    def test_history_with_invalid_data(self):

        r = requests.get(URL + 'history/', params={'pk': TestViews.note1_id})

        data = r.json()

        assert r.status_code == 400
        assert data == ID_ERROR

    def test_get_all_notes(self):

        r = requests.get(URL + 'notes/')

        notes = r.json()

        # It should not  return the deleted note

        assert len(notes) == 1
        assert notes[0]['id'] == TestViews.note2_id

    def test_get_note_with_versions(self):

        # It should return the latest version of a note

        r = requests.get(URL + 'note/', params={'id': TestViews.note2_id})

        note = r.json()

        assert r.status_code == 200
        assert note['version'] == 2
        assert note['id'] == TestViews.note2_id

    def test_get_deleted_note(self):

        r = requests.get(URL + 'note/', params={'id': TestViews.note1_id})

        note = r.json()

        assert r.status_code == 200
        assert note == NO_NOTE_ERROR
