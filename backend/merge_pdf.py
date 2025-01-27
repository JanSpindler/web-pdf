import sqlite3
from utils import table_exists, UPLOAD_FOLDER, RESULT_FOLDER
from pypdf import PdfReader, PdfWriter
import os


# pdf_order is a list of tuples containing the file_id and page number
def merge_pdf(db: sqlite3.Connection, pdf_order: list[tuple[int, int]], session_id: int) -> None:
    # Get db cursor
    db_cursor = db.cursor()

    # Check if file table exists
    if not table_exists(db_cursor, "file"):
        db.close()
        raise Exception("File table does not exist")
    
    # Check if file with file_id exists and get file names
    file_name_dict = {}
    for file_id, _ in pdf_order:
        # Check if file exists
        db_cursor.execute(f"SELECT name, session_id FROM file WHERE id = {file_id};")
        result = db_cursor.fetchone()
        if result is None:
            db.close()
            raise Exception(f"File with id {file_id} does not exist")
        
        # Check if file belongs to session
        if int(result[1]) != session_id:
            db.close()
            raise Exception(f"File with id {file_id} does not belong to session with id {session_id}")

        # Reconstruct file name
        file_name_dict[file_id] = f"{file_id}_{result[0]}"

    # Read pdf pages
    original_pages_dict = {}
    for file_id, file_name in file_name_dict.items():
        pdf_reader = PdfReader(f"{UPLOAD_FOLDER}/{file_name}")
        original_pages_dict[file_id] = pdf_reader.pages

    # Create results directory if not exists
    if not os.path.exists(RESULT_FOLDER):
        os.mkdir(RESULT_FOLDER)

    # Merge pdf pages
    pdf_writer = PdfWriter()
    for file_id, page_number in pdf_order:
        # Check if page number is valid for selected pdf
        if page_number < 0 or page_number >= len(original_pages_dict[file_id]):
            db.close()
            raise Exception(f"Page number {page_number} is invalid for file with id {file_id}")
        
        # Add page to result
        pdf_writer.add_page(original_pages_dict[file_id][page_number])

    # Check if result table exists in db
    if not table_exists(db_cursor, "result"):
        db_cursor.execute("CREATE TABLE result (id INTEGER PRIMARY KEY, session_id INTEGER);")
        db.commit()

    # Add result to db
    db_cursor.execute(f"INSERT INTO result (session_id) VALUES ({session_id});")
    result_id = db_cursor.lastrowid
    if result_id is None:
        db.rollback()
        db.close()
        raise Exception("Failed to store result in database")

    # Write result to file
    result_file_path = f"{RESULT_FOLDER}/{result_id}.pdf"
    pdf_writer.write(result_file_path)
