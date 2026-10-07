"""CLI tests for ``python -m package_sorter``."""

import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

import package_sorter.__main__ as entrypoint
from package_sorter.cli import main


@pytest.mark.parametrize(
    ("argv", "stack"),
    [
        pytest.param(
            ["--width", "10", "--height", "10", "--length", "10", "--mass", "5"],
            "STANDARD",
            id="standard",
        ),
        pytest.param(
            ["--width", "150", "--height", "1", "--length", "1", "--mass", "1"],
            "SPECIAL",
            id="special",
        ),
        pytest.param(
            ["--width", "100", "--height", "100", "--length", "100", "--mass", "20"],
            "REJECTED",
            id="rejected",
        ),
    ],
)
def test_prints_stack(
    argv: list[str],
    stack: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(argv) == 0
    assert capsys.readouterr().out == f"{stack}\n"


@pytest.mark.parametrize(
    ("argv", "detail"),
    [
        pytest.param(
            ["--width", "0", "--height", "10", "--length", "10", "--mass", "5"],
            "width must be greater than zero",
            id="zero-width",
        ),
        pytest.param(
            ["--width", "10", "--height", "-2", "--length", "10", "--mass", "5"],
            "height must be greater than zero",
            id="negative-height",
        ),
        pytest.param(
            ["--width", "nan", "--height", "10", "--length", "10", "--mass", "5"],
            "width must be a finite number",
            id="nan-width",
        ),
        pytest.param(
            ["--width", "10", "--height", "10", "--length", "inf", "--mass", "5"],
            "length must be a finite number",
            id="infinite-length",
        ),
    ],
)
def test_rejects_invalid_measurements(
    argv: list[str],
    detail: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(argv) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ")
    assert detail in captured.err


def test_missing_argument_exits_with_usage() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--width", "10"])
    assert exc_info.value.code == 2


def test_non_numeric_argument_exits_with_usage() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(
            ["--width", "ten", "--height", "10", "--length", "10", "--mass", "5"],
        )
    assert exc_info.value.code == 2


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == "package_sorter 1.0.0"


def test_help_lists_measurements(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    help_text = capsys.readouterr().out
    assert "--width" in help_text
    assert "--height" in help_text
    assert "--length" in help_text
    assert "--mass" in help_text


def test_main_module_can_be_imported() -> None:
    assert entrypoint.main is main


def test_module_entrypoint(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delitem(sys.modules, "package_sorter.__main__", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "package_sorter",
            "--width",
            "10",
            "--height",
            "10",
            "--length",
            "10",
            "--mass",
            "20",
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("package_sorter", run_name="__main__")
    assert exc_info.value.code == 0
    assert capsys.readouterr().out == "SPECIAL\n"


def test_module_entrypoint_subprocess() -> None:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "package_sorter",
            "--width",
            "10",
            "--height",
            "10",
            "--length",
            "10",
            "--mass",
            "5",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
    )
    assert completed.returncode == 0
    assert completed.stdout == "STANDARD\n"
