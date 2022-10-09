from typer.testing import CliRunner
from pathlib import Path
from hazelnotes.app import conf, typer_app
import os

runner = CliRunner()
test_db: Path = conf["data_directory"] / "hazelnotes_test.db"

if test_db.is_file():
    os.remove(conf["data_directory"] / "hazelnotes_test.db")
os.environ["RUN_ENV"] = "test"


def test_app():
    result = runner.invoke(typer_app, ['init'])
    assert result.exit_code == 0


def test_create_note():
    result = runner.invoke(typer_app, ['create', 'test note'])
    assert result.exit_code == 0


def test_list_created_note():
    result = runner.invoke(typer_app, ['list'], input="99999\n")
    assert result.exit_code == 1
    assert "test note" in result.stdout
    assert "This note id doesn't exist" in result.stdout







