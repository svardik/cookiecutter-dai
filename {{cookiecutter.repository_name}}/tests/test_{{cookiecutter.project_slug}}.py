#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `{{ cookiecutter.project_slug }}` package."""

import pytest

@pytest.fixture
def setup_teardown():
    """Set up and tear down test fixtures, if any."""
    yield

@pytest.mark.usefixtures("setup_teardown")
def test_000_something():
    """Test something."""
    assert True
