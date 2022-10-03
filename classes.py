from peewee import *
from main import APP_DIR

db = SqliteDatabase(APP_DIR / "hazelnotes.db")


class Note(Model):
    title = CharField(max_length=200)
    creation_date = DateTimeField()
    tags = CharField(max_length=200)
    filename = CharField(max_length=200, default="")

    def __str__(self):
        return f"{self.title} ({self.creation_date})"

    class Meta:
        database = db
