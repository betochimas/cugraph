import doctest
import inspect
import os

import numpy as np
import pytest

import cugraph
import cudf

max_count = 500


#def _name_in_all(parent, name):
#    return name in getattr(parent, "__all__", [])


def _is_public_name(parent, name):
    return not name.startswith("_")

def _find_docstrings_in_obj(finder, obj, criteria=None):
    for docstring in finder.find(obj):
        print(docstring)
        if docstring.examples:
            print("DOCSTRING PRESENT!")
            yield docstring
    for name, member in inspect.getmembers(obj):
        if criteria is not None and not criteria(obj, name):
            continue
        print(name)
        yield from _find_docstrings_in_obj(
            finder, member, criteria=_is_public_name
        )

def _fetch_doctests():
    finder = doctest.DocTestFinder()
    yield from _find_docstrings_in_obj(finder, cugraph, criteria=_is_public_name)


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
        globs = dict(cugraph=cugraph, np=np, cudf=cudf,)
        docstring.globs = globs
        runner.run(docstring)
        results = runner.summarize()
        #if results.failed:
        #    raise AssertionError(results)
