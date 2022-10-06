import typer
from pathlib import Path
from os import mkdir
from os import remove
import subprocess
from classes import *
import datetime
from slugify import slugify
from rich.console import Console
from rich.table import Table
import pandas as pd

app = typer.Typer(help="A command line note manager. Nuts included."
                       "\n\n"
                       "Run `[command name] --help` to see how to use the commands.")
APP_NAME = "hazelnotes"
APP_DIR: Path = Path(typer.get_app_dir(APP_NAME))
MARKDOWN_DIR: Path = APP_DIR / "notes"
EDITOR_COMMAND = "/opt/sublime_text/sublime_text"


@app.command()
def create(
        title: str = typer.Argument(..., help="The title of the note (is added as # at the top of the markdown file)."),
        tags: str = typer.Argument(default="", show_default=True,
                                   help="Comma-separated list of tags that will help you find the note later.")
):
    """
    Creates a new markdown file for a note, adds the note to the database and opens the markdown file in the editor.
    """

    creation_date: datetime.datetime = datetime.datetime.now()

    connect_db(db)

    # Add the note to the database
    new_note = Note.create(
        title=title,
        creation_date=creation_date,
    )

    # Create the note file
    markdown_title = f"# {creation_date.date()} {title}\n\n"
    markdown_filename = f"{str(new_note.get_id()):0>5}_{slugify(title)}.md"
    markdown_path = MARKDOWN_DIR / markdown_filename

    file = open(markdown_path, "a")
    file.write(markdown_title)
    file.close()

    # Update note's filename
    new_note.filename = markdown_filename
    new_note.save()

    note_id = new_note.get_id()

    # Create tags
    for tag in tags.split(","):
        NoteTag.create(
            note_id=note_id,
            tag_text=tag.strip()
        )

    close_db(db)

    open_note_file(note_id)


@app.command()
def init():
    """
    Initializes a new note database and validate the options.
    """

    # Create the app config dir (typically ~/.config/hazelnotes)
    if not (APP_DIR.is_dir()):
        mkdir(APP_DIR)

    if not (Path(APP_DIR) / "hazelnotes.db").is_file():
        connect_db(db)
        db.create_tables([Note, NoteTag])
        close_db(db)
    else:
        print(str(APP_DIR) + "/hazelnotes.db already exists")

    if not MARKDOWN_DIR.is_dir():
        mkdir(MARKDOWN_DIR)
    else:
        print(str(MARKDOWN_DIR) + "directory already exists")


@app.command("open")
def open_note(note_id: str = typer.Argument(help="The id of the note to open.", default="")):
    """
    Opens the note in the configured editor.
    """

    if note_id == "":
        note_id = typer.prompt("Which [id] do you want to edit?")

    open_note_file(note_id)


@app.command("list")
def list_notes_command(t: str = typer.Option(default="", help="Comma-separated list of tags to filter notes.")):
    """
    Displays a list of the last created notes.
    """

    if len(t) > 0:
        tags: list = t.split(",")
        connect_db(db)
        notes: Model = Note.select(Note.title,
                                   Note.creation_date,
                                   Note.filename,
                                   NoteTag.note_id,
                                   NoteTag.tag_text).distinct().join(NoteTag).where(NoteTag.tag_text.in_(tags))
        notes_list: list[dict] = to_aggregated_list(notes, 'creation_date', ascending=False)

        close_db(db)
        if len(notes_list) == 0:
            print(f"No note has the following tags: {' and '.join(tags)}")
            raise typer.Exit()

        new_list = []
        for note in notes_list:
            if all([tag in note['tag_text'] for tag in tags]):
                new_list.append(note)

        notes_list = new_list

        # for i, note in notes.enumerate():

        list_notes(f"Last notes with the following tags: {' and '.join(tags)}", notes_list)
    else:
        list_notes("Last notes")

    note_id = typer.prompt("Which [id] do you want to edit?")
    open_note_file(note_id)


@app.command()
def delete(note_id: str = typer.Argument(..., help="The id of the note to delete.")):
    connect_db(db)
    note: Note = Note.get_by_id(note_id)

    markdown_path = MARKDOWN_DIR / note.filename
    if markdown_path.is_file():
        remove(markdown_path)
    else:
        print(str(markdown_path) + " doesn't exist. No file was removed.")
    note.delete_instance()
    close_db(db)


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
        markdown_path = MARKDOWN_DIR / note.filename
        subprocess.run([EDITOR_COMMAND, markdown_path])
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


if __name__ == "__main__":
    app()
