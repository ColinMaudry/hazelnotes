import datetime
import subprocess
from rich.console import Console
from rich.table import Table
import pandas as pd
import typer
from peewee import ModelSelect, DoesNotExist

from hazelnotes_cli.classes import *


def open_note_locally(note: Note):
    if note.filename:
        # Open it in the configured editor
        markdown_path = conf["md_directory"] / note.filename
        subprocess.run([conf["local_editor_command"], markdown_path])
    else:
        print("This note doesn't have a local copy.")
        typer.Exit(1)


def list_notes(table_title: str = None, notes: list = None):
    if not notes:
        connect_db(db)
        notes_query: ModelSelect = Note.select(Note.title,
                                               Note.creation_date,
                                               Note.filename,
                                               NoteTag.note_id,
                                               NoteTag.tag_text).distinct().join(NoteTag).order_by(
            Note.creation_date.desc())

        check_result_length(notes_query, f"No note in the database.")

        notes = to_aggregated_list(notes_query, 'creation_date', ascending=False)

        close_db(db)

    console = Console()

    table = Table("id", "title", "creation date", "tags", title=table_title, title_justify='left')
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


def check_result_length(notes_list: ModelSelect, message):
    if len(notes_list) == 0:
        print(message)
        raise typer.Exit()


def to_aggregated_list(notes_query, sort_by, ascending=False):
    notes_list = [row for row in notes_query.dicts()]
    df: pd.DataFrame = pd.DataFrame(notes_list)
    df = df.drop_duplicates()
    df = df.groupby(by=['note_id', 'title', 'creation_date', 'filename'], as_index=False).agg(list)
    df.sort_values(by=sort_by, ascending=ascending)
    notes_list: list = df.to_dict(orient='records')
    return notes_list


def open_note(note: Note):
    # ConnectionError is also in peewee
    from requests import head, ConnectionError as requestsConnectionError
    import webbrowser
    import multiprocessing
    from time import sleep

    try:
        # Test internet connection
        print("test internet")
        head(conf["hedgedoc_url"], timeout=1)

        # Open note in the browser if not testing
        if os.environ["RUN_ENV"] != "test":
            x = lambda: webbrowser.open(note.url + "?both", new=0)
            proc = multiprocessing.Process(target=x, args=())
            proc.start()
            sleep(1)
            # Terminate the process
            proc.terminate()

    except requestsConnectionError:
        # No internet, open the file in the local editor
        print("No internet connection, attempt to open the file locally")
        open_note_locally(note)


def create_web_note(text: str) -> str:
    """
    Create a note in HedgeDoc using user input.
    :param text: The markdown text to be added in the new note.
    :return: The url of the created HedgeDoc note.
    """

    import requests

    try:
        r = requests.post(conf["hedgedoc_url"] + "/new",
                          headers={"Content-Type": "text/markdown"},
                          data=text,
                          )
    except requests.ConnectionError:
        return ""

    return r.request.url
