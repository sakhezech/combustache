import os
import subprocess
from pathlib import Path

from combustache.__main__ import cli
from conftest import EXPECTED, TEMPLATE


def test_patial_list(clidir: Path):
    outpath = 'output_partial_list.txt'
    os.chdir(clidir)

    cli(
        [
            'template.txt',
            '-d',
            'data.json',
            '-p',
            'partials/partial_1.json',
            '-p',
            'partials/partial_2.json',
            '-p',
            'partial_3.json',
            '-o',
            outpath,
        ]
    )
    out = (clidir / outpath).read_text()
    assert out == EXPECTED


def test_partial_dir(clidir: Path):
    outpath = 'output_partial_dir.txt'
    os.chdir(clidir)

    cli(
        [
            'template.txt',
            '-d',
            'data.json',
            '--partial-dir',
            'partials/',
            '--partial-pattern',
            '**/*.json',
            '-p',
            'partial_3.json',
            '-o',
            outpath,
        ]
    )
    out = (clidir / outpath).read_text()
    assert out == EXPECTED


def test_template_string(clidir: Path):
    outpath = 'output_template_string.txt'
    os.chdir(clidir)

    cli(
        [
            '-s',
            TEMPLATE,
            '-d',
            'data.json',
            '-p',
            'partials/partial_1.json',
            '-p',
            'partials/partial_2.json',
            '-p',
            'partial_3.json',
            '-o',
            outpath,
        ]
    )
    out = (clidir / outpath).read_text()
    assert out == EXPECTED


def test_stdin_input(clidir: Path):
    outpath = 'output_stdin_input.txt'
    os.chdir(clidir)

    cat = subprocess.Popen(
        ['cat', 'data.json'],
        stdout=subprocess.PIPE,
    )
    com = subprocess.Popen(
        [
            'combustache',
            'template.txt',
            '--partial-dir',
            'partials/',
            '--partial-pattern',
            '**/*.json',
            '-p',
            'partial_3.json',
            '-o',
            outpath,
        ],
        stdin=cat.stdout,
        stdout=subprocess.PIPE,
    )
    com.wait()
    out = (clidir / outpath).read_text()
    assert out == EXPECTED


def test_stdout_output(clidir: Path):
    outpath = 'output_stdout_output.txt'
    os.chdir(clidir)

    com = subprocess.Popen(
        [
            'combustache',
            'template.txt',
            '-d',
            'data.json',
            '--partial-dir',
            'partials/',
            '--partial-pattern',
            '**/*.json',
            '-p',
            'partial_3.json',
        ],
        stdout=subprocess.PIPE,
    )
    if com.stdout is None:
        raise ValueError('no stdout subprocess?')

    out = com.stdout.read().decode()
    (clidir / outpath).write_text(out)
    assert out == EXPECTED
