from pathlib import Path
from os import mkdir
from os import remove

from slugify import slugify

from helpers import *

typer_app = typer.Typer(help="A command line note manager. Nuts included."
                             "\n\n"
                             "Run `[command name] --help` to see how to use the commands.")
APP_NAME = "hazelnotes"


@typer_app.command()
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

    markdown_text = f"# {creation_date.date()} {title}\n\n"


    # Create the note

    note_url = create_web_note(markdown_text)

    if note_url != "":
        new_note.url = note_url

    else:
        markdown_filename = f"{str(new_note.get_id()):0>5}_{slugify(title)}.md"
        markdown_path = config["md_directory"] / markdown_filename

        file = open(markdown_path, "a")
        file.write(markdown_text)
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


@typer_app.command()
def init():
    """
    Initializes a new note database and validate the options.
    """

    # Create the app config dir (typically ~/.config/hazelnotes)
    if not (config["data_directory"].is_dir()):
        mkdir(config["data_directory"])

    if not (Path(config["data_directory"]) / "hazelnotes.db").is_file():
        connect_db(db)
        db.create_tables([Note, NoteTag])
        close_db(db)
    else:
        print(str(config["data_directory"]) + "/hazelnotes.db already exists")

    if not config["md_directory"].is_dir():
        mkdir(config["md_directory"])
    else:
        print(str(config["md_directory"]) + "directory already exists")


@typer_app.command("open")
def open_note(note_id: str = typer.Argument(help="The id of the note to open.", default="")):
    """
    Opens the note in the configured editor.
    """

    import webbrowser
    import requests

    if note_id == "":
        list_notes("Last notes")
        raise typer.Exit()

    try:
        assert int(note_id) > 0
    except ValueError:
        print("The note id must be an integer.")
        raise typer.Exit(1)

    # Get the note from the database
    try:
        connect_db(db)
        note = Note.get_by_id(note_id)
    except (IndexError, DoesNotExist):
        print(f"This note id doesn't exist: {note_id}")
        raise typer.Exit(1)

    try:
        # Test internet connection
        requests.head(config["hedgedoc_url"], timeout=1)

        # Open note in the browser
        webbrowser.open(note.url + "/both", new=2, autoraise=True)
    except requests.ConnectionError:
        # No internet, open the file in the local editor
        print("No internet connection")
        open_note_file(note)

    close_db(db)


@typer_app.command("list")
def list_notes_command(t: str = typer.Option(default="", help="Comma-separated list of tags to filter notes.")):
    """
    Displays a list of the last created notes.
    """

    if len(t) > 0:
        tags: list = t.split(",")
        connect_db(db)
        notes: ModelSelect = Note.select(Note.title,
                                         Note.creation_date,
                                         Note.filename,
                                         NoteTag.note_id,
                                         NoteTag.tag_text).distinct().join(NoteTag).where(NoteTag.tag_text.in_(tags))

        check_result_length(notes, f"No note has the following tags: {' and '.join(tags)}")

        notes_list: list[dict] = to_aggregated_list(notes, 'creation_date', ascending=False)

        close_db(db)

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


@typer_app.command()
def delete(note_id: str = typer.Argument(..., help="The id of the note to delete.")):
    connect_db(db)
    note: Note = Note.get_by_id(note_id)

    markdown_path = config["md_directory"] / note.filename
    if markdown_path.is_file():
        remove(markdown_path)
    else:
        print(str(markdown_path) + " doesn't exist. No file was removed.")
    note.delete_instance()
    close_db(db)


if __name__ == "__main__":
    typer_app()
