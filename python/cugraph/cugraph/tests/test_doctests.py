import doctest
import inspect
import os

import numpy as np
import pytest

import cugraph


def _name_in_all(parent, name, member):
    return name in getattr(parent, "__all__", [])


def _is_public_name(parent, name, member):
    return not name.startswith("_")


def _find_docstrings_in_obj(finder, obj, criteria=None):
    for docstring in finder.find(obj):
        if docstring.examples:
            yield docstring
    for name, member in inspect.getmembers(obj):
        # Filter out non-matching objects with criteria
        if criteria is not None and not criteria(obj, name, member):
            continue
        # Recurse over the public API of modules (objects defined in __all__)
        if inspect.ismodule(member):
            yield from _find_docstrings_in_obj(
                finder, member, criteria=_name_in_all
            )
        # Recurse over the public API of classes (attributes not prefixed with
        # an underscore)
        if inspect.isclass(member):
            yield from _find_docstrings_in_obj(
                finder, member, criteria=_is_public_name
            )


def _fetch_doctests():
    finder = doctest.DocTestFinder()
    yield from _find_docstrings_in_obj(finder, cugraph, criteria=_name_in_all)


class TestDoctests:
    @pytest.fixture(autouse=True)
    def chdir_to_tmp_path(cls, tmp_path):
        original_directory = os.getcwd()
        try:
            os.chdir(tmp_path)
            yield
        finally:
            os.chdir(original_directory)

    @pytest.mark.parametrize(
        "docstring", _fetch_doctests(), ids=lambda docstring: docstring.name
    )
    def test_docstring(self, docstring):
        optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
        runner = doctest.DocTestRunner(optionflags=optionflags)
        globs = dict(cugraph=cugraph, np=np,)
        docstring.globs = globs
        runner.run(docstring)
        results = runner.summarize()
        if results.failed:
            raise AssertionError(results)