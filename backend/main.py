from fastapi import FastAPI, Depends, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse
import sqlite3
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager
import time
from threading import Thread, Event
import uvicorn
from utils import table_exists, UPLOAD_FOLDER, DB_FILE


app = FastAPI()
app_stop_event = Event()


def get_db():
    db = sqlite3.connect(DB_FILE)
    try:
        yield db
    finally:
        db.close()


class BackgroundTasks(Thread):
    def __init__(self):
        super().__init__(daemon=True)


    def run(self,*args,**kwargs):
        # Main loop
        while not app_stop_event.is_set():
            # Sleep
            time.sleep(60)

            # Get db and cursor
            db = sqlite3.connect(DB_FILE)
            db_cursor = db.cursor()

            # Check session timeout
            db_cursor.execute("SELECT id, start_time FROM session;")
            for session_id, start_time_str in db_cursor.fetchall():
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() - start_time > timedelta(minutes=15):
                    db_cursor.execute(f"DELETE FROM session WHERE id = {session_id};")
            db.commit()

            # Delete files without valid session
            db_cursor.execute(
""" SELECT file.id, file.name
        FROM file LEFT JOIN session ON file.session_id = session.id
        WHERE file.session_id IS NULL OR session.id IS NULL;""")
            for file_id, filename in db_cursor.fetchall():
                # Delete file on disk
                filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                # Delete file reference from database
                db_cursor.execute(f"DELETE FROM file WHERE id = {file_id};")
            db.commit()

            # Delete all files that are not reference in database
            db_cursor.execute("SELECT id, name FROM file;")
            filenames = [f"{file_id}_{filename}" for file_id, filename in db_cursor.fetchall()]
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename not in filenames:
                    os.remove(filename)

            # Close db
            db.close()


@app.get("/")
def root():
    # Return default html page
    return HTMLResponse(content=f"""
<html>
    <head></head>
    <body>
        <h1>This is an API not a website</h1>
        <p>Hello there!</p>
    </body>
</html>
""")


@app.post("/api/session")
def create_session(db = Depends(get_db)):
    # Check wether session table exists
    db_cursor = db.cursor()
    if not table_exists(db_cursor, "session"):
        db_cursor.execute("CREATE TABLE session (id INTEGER PRIMARY KEY, start_time TEXT);")
        db.commit()
    
    # Parse current time as str
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert new session
    db_cursor.execute(f"INSERT INTO session (start_time) VALUES ('{start_time_str}');")
    db.commit()
    session_id = db_cursor.lastrowid
    if session_id is None:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="Failed to create session")

    # Success, return session id
    db.close()
    return {"session_id": session_id}


@app.post("/api/upload")
def upload_file(file: UploadFile, db = Depends(get_db)):
    # TODO: Get session id from request
    session_id = 1

    # Check if session exists in database

    # Check if file is a pdf
    filename = file.filename
    if not filename.endswith(".pdf"):
        db.close()
        raise HTTPException(status_code=400, detail="File must end with .pdf")

    # Check file size wether file size is over 256 MB
    if file.size > 1024 * 1024 * 256:
        db.close()
        raise HTTPException(status_code=400, detail="File size must be less than 256 MB")

    # Check if file table exists
    db_cursor = db.cursor()
    if not table_exists(db_cursor, "file"):
        db_cursor.execute("CREATE TABLE file (id INTEGER PRIMARY KEY, session_id INTEGER, name TEXT);")
        db.commit()

    # Store file meta data references in database
    db_cursor.execute(f"INSERT INTO file (session_id, name) VALUES ({session_id}, '{filename}');")
    db.commit()
    file_id = db_cursor.lastrowid
    if file_id is None:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail="Failed to store file meta data in database")

    # Store file
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}")
    with open(filepath, "wb") as os_file:
        os_file.write(file.file.read())

    # Verify if the file was written successfully
    if not os.path.exists(filepath):
        db.close()
        raise HTTPException(status_code=500, detail="Failed to write file to disk")

    # Success,
    db.close()
    return {"filename": file.filename}


if __name__ == "__main__":
    bg_task = BackgroundTasks()
    bg_task.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    app_stop_event.set()
