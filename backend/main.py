from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse
import sqlite3
import datetime
import os


UPLOAD_FOLDER = "uploads"


app = FastAPI()


def get_db():
    db = sqlite3.connect("test.db")
    try:
        yield db
    finally:
        db.close()


def table_exists(db_cursor, table_name):
    db_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return db_cursor.fetchone() is not None


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
    start_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert new session
    db_cursor.execute(f"INSERT INTO session (start_time) VALUES ('{start_time_str}');")
    db.commit()
    session_id = db_cursor.lastrowid
    if session_id is None:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create session")

    # Success, return session id
    return {"session_id": session_id}


@app.post("/api/upload")
def upload_file(file: UploadFile, db = Depends(get_db)):
    # TODO: Get session id from request
    session_id = 1

    # Check if session exists in database

    # Check if file is a pdf
    filename = file.filename
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must end with .pdf")

    # Check file size wether file size is over 256 MB
    if file.size > 1024 * 1024 * 256:
        raise HTTPException(status_code=400, detail="File size must be less than 256 MB")

    # Store file
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.seek(0)
    with open(filepath, "wb") as os_file:
        os_file.write(file.file.read())

    # Verify if the file was written successfully
    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="Failed to write file to disk")

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
        raise HTTPException(status_code=500, detail="Failed to store file meta data in database")

    # Success,
    return {"filename": file.filename}
