from pathlib import Path
from typing import Any

import pytest
import yaml
from combustache import render


def lambda_constructor(
    loader: yaml.Loader | yaml.FullLoader | yaml.UnsafeLoader, node: yaml.Node
) -> Any:
    value = loader.construct_mapping(node)  # type: ignore
    return eval(value['python'])


yaml.add_constructor('!code', lambda_constructor)


def pytest_collect_file(parent, file_path: Path):
    if file_path.suffix == '.yml':
        if not file_path.name.startswith('~') or file_path.stem == '~lambdas':
            return SpecFile.from_parent(parent, path=file_path)


class SpecFile(pytest.File):
    def collect(self):
        with self.path.open() as f:
            r = yaml.load(f, yaml.Loader)
        for test in r['tests']:
            yield SpecItem.from_parent(self, name=test['name'], test=test)


class SpecItem(pytest.Item):
    def __init__(self, *, test: dict, **kwargs):
        super().__init__(**kwargs)
        self.test = test

    def runtest(self) -> None:
        template = self.test['template']
        expected = self.test['expected']
        data = self.test['data']
        partials = self.test.get('partials', None)
        result = render(template, data, partials)
        if result != expected:
            raise TestException(
                self, template, expected, data, partials, result
            )

    def repr_failure(self, excinfo: pytest.ExceptionInfo, style=None):
        if isinstance(excinfo.value, TestException):
            _, template, expected, data, partials, result = excinfo.value.args
            expected: str
            string = (
                f'Data: {data}\n'
                f'Partials: {partials}\n'
                f'Template: |{unescape(template)}|\n'
                f'Expected: |{unescape(expected)}|\n'
                f'Result: |{unescape(result)}|'
            )
            return string
        return super().repr_failure(excinfo)

    def reportinfo(self):
        return (
            self.path,
            None,
            f'{self.parent.path.stem.removeprefix("~").capitalize()}::{self.name}',  # type: ignore
        )


class TestException(Exception):
    pass


def unescape(string: str) -> str:
    return string.encode('unicode-escape').decode()
