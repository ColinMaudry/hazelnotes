from peewee import Model, CharField, SqliteDatabase, DateTimeField, ForeignKeyField
from app_config import config

db: SqliteDatabase = SqliteDatabase(config["data_directory"] / "hazelnotes.db",
                                    pragmas={'foreign_keys': 1})


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
