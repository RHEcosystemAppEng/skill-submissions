import os


def test_filled_document_exists():
    assert os.path.exists("/workspace/filled_document.docx")


def test_filled_document_not_empty():
    size = os.path.getsize("/workspace/filled_document.docx")
    assert size > 0
