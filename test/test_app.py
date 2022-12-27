from typer.testing import CliRunner
from pathlib import Path
import os
from shutil import rmtree

from hazelnotes_cli.app_config import get_config
from hazelnotes_cli.app import typer_app

runner = CliRunner()

def test_init_db():
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

def test_remove_test_folder():
    data_dir: Path = get_config("test")["data_directory"]
    rmtree(data_dir)
    assert not data_dir.is_dir()








