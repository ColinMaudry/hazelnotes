from peewee import Model, CharField, SqliteDatabase, DateTimeField, ForeignKeyField
import os
from pathlib import Path

from hazelnotes_cli.app_config import get_config

conf = get_config()

try:
    if os.environ["RUN_ENV"] and os.environ["RUN_ENV"] == "test":
        db_file: Path = conf["data_directory"] / "hazelnotes_test.db"
        db: SqliteDatabase = SqliteDatabase(db_file, pragmas={'foreign_keys': 1})
    else:
        db_file: Path = conf["data_directory"] / "hazelnotes.db"
        db: SqliteDatabase = SqliteDatabase(db_file, pragmas={'foreign_keys': 1})

except KeyError:
    os.environ["RUN_ENV"] = "default"
    db_file: Path = conf["data_directory"] / "hazelnotes.db"
    db: SqliteDatabase = SqliteDatabase(db_file, pragmas={'foreign_keys': 1})


class Note(Model):
    title = CharField(max_length=200)
    creation_date = DateTimeField()
    filename = CharField(max_length=200, default="")
    url = CharField(max_length=200, default="")

    def __str__(self):
        return f"[{self.id}] {self.title} ({self.creation_date})"

    class Meta:
        database = db


class NoteTag(Model):
    note_id = ForeignKeyField(Note, backref='tags')
    tag_text = CharField(max_length=200)

    class Meta:
        database = db
