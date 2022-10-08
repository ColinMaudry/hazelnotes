import datetime
import subprocess
from rich.console import Console
from rich.table import Table
import pandas as pd
import typer

from classes import *


def open_note_file(note_id: str):
    # Get the note from the database
    try:
        assert int(note_id) > 0
    except ValueError:
        print("The note id must be an integer.")
        raise typer.Exit(1)

    try:
        connect_db(db)
        note = Note.get_by_id(note_id)

        # Open it in the configured editor
        markdown_path = config["md_directory"] / note.filename
        subprocess.run([config["local_editor_command"], markdown_path])
    except (IndexError, DoesNotExist):
        print(f"This note id doesn't exist: {note_id}")
        raise typer.Exit(1)


def list_notes(table_title: str = None, notes: list = None):
    if not notes:
        connect_db(db)
        notes_query = Note.select(Note.title,
                                  Note.creation_date,
                                  Note.filename,
                                  NoteTag.note_id,
                                  NoteTag.tag_text).distinct().join(NoteTag).order_by(Note.creation_date.desc())

        notes = to_aggregated_list(notes_query, 'creation_date', ascending=False)

        close_db(db)

    console = Console()

    if len(notes) == 0:
        print("There are not notes to display.")
        raise typer.Exit()

    table = Table("id", "title", "creation date", "tags", title=table_title, title_justify='left')
    print(notes)
    for note in notes:
        table.add_row(str(note['note_id']),
                      note['title'],
                      print_datetime(note['creation_date']),
                      " | ".join(note['tag_text'])
                      )

    print("")
    console.print(table)


def print_datetime(dt: datetime.datetime):
    return dt.strftime('%Y-%m-%d %H:%M')


def connect_db(database):
    if database.is_closed():
        database.connect()


def close_db(database):
    if not database.is_closed():
        database.close()


def to_aggregated_list(notes_query, sort_by, ascending=False):
    notes_list = [row for row in notes_query.dicts()]
    df: pd.DataFrame = pd.DataFrame(notes_list)
    df = df.drop_duplicates()
    df = df.groupby(by=['note_id', 'title', 'creation_date', 'filename'], as_index=False).agg(list)
    df.sort_values(by=sort_by, ascending=ascending)
    notes_list: list = df.to_dict(orient='records')
    return notes_list

