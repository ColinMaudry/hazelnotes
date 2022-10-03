import typer
from pathlib import Path
from os import mkdir
import subprocess
from classes import *
import datetime
from slugify import slugify

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

    db.connect()

    # Add the note to the database
    new_note = Note.create(
        title=title,
        tags=tags,
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

    db.close()

    open_note_file(new_note.get_id())


@app.command()
def init():
    """
    Initializes a new note database and validate the options.
    """

    # Create the app config dir (typically ~/.config/hazelnotes)
    if not (APP_DIR.is_dir()):
        mkdir(APP_DIR)

    if not (Path(APP_DIR) / "hazelnotes.db").is_file():
        db.connect()
        db.create_tables([Note])
        db.close()
    else:
        print(str(APP_DIR) + "/hazelnotes.db already exists")

    if not MARKDOWN_DIR.is_dir():
        mkdir(MARKDOWN_DIR)
    else:
        print(str(APP_DIR) + "/notes directory already exists")


@app.command("open")
def open_note(note_id: str = typer.Argument(..., help="The id of the note to open.")):
    """
    Opens the note in the configured editor.
    """
    open_note_file(note_id)


def open_note_file(note_id: str):
    # Get the note from the database
    db.connect()
    note = Note.get_by_id(note_id)
    db.close()

    # Open it in the configured editor
    markdown_path = MARKDOWN_DIR / note.filename
    subprocess.run([EDITOR_COMMAND, markdown_path])


if __name__ == "__main__":
    app()
