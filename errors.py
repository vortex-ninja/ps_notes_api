ID_ERROR = {
                "error": "bad request, this endpoint accepts exactly one parameter: 'id'",
                "status": 400
            }
NO_HISTORY_ERROR = {
                        "error": "no history for this id",
                        "status": 200
                    }
NO_NOTES_ERROR = {
                    "error": "there are no notes in database",
                    "status": 200
                }
NO_NOTE_ERROR = {
                    "error": "note doesn't exist",
                    "status": 200
                }
CREATE_ERROR = {
                    "error": "bad request, this endpoint accepts exactly two parameters: 'title' and 'content'",
                    "status": 400
                }
UPDATE_ERROR = {
                    "error": "bad request, this endpoint accepts exactly 2 or 3 parameters: 'id' (required), 'title', 'content'",
                    "status": 400
                }

