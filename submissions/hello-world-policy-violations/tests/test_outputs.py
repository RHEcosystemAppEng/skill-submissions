"""Tests with intentional bare except:pass for operational policy check testing."""

import os


def test_file_exists():
    """Check that hello.txt was created."""
    assert os.path.exists("hello.txt"), "hello.txt should exist"


def test_file_content():
    """Check file content."""
    with open("hello.txt") as f:
        content = f.read()
    assert content.strip() == "Hello, world!"


def test_cleanup():
    try:
        os.remove("hello.txt")
    except:
        pass
