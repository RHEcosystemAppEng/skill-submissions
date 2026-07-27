---
name: docx-template-filler
description: Fill Word document templates with placeholder replacement using python-docx. Handles split placeholders across XML runs, headers/footers, nested tables, and conditional sections.
---

# Word Document Template Filler

Fill Word (.docx) templates by replacing `{{PLACEHOLDER}}` markers with actual values using python-docx.

## Critical: Split Placeholder Problem

Word often splits placeholder text across multiple XML runs. For example, `{{CANDIDATE_NAME}}` might be stored as:
- Run 1: `{{CANDI`
- Run 2: `DATE_NAME}}`

### Wrong Approach (fails on split placeholders)

```python
# DON'T DO THIS - won't find split placeholders
for para in doc.paragraphs:
    for run in para.runs:
        if '{{NAME}}' in run.text:
            run.text = run.text.replace('{{NAME}}', value)
```

### Correct Approach: Paragraph-Level Search and Rebuild

```python
import re

def replace_placeholder(paragraph, placeholder, value):
    """Replace placeholder that may be split across runs."""
    full_text = paragraph.text
    if placeholder not in full_text:
        return False

    new_text = full_text.replace(placeholder, str(value))

    # Preserve first run's formatting, clear others
    runs = paragraph.runs
    for i, run in enumerate(runs):
        if i == 0:
            run.text = new_text
        else:
            run.text = ''

    return True
```

## Headers and Footers

`doc.paragraphs` only covers the document body. Headers and footers are separate:

```python
for section in doc.sections:
    for para in section.header.paragraphs:
        replace_placeholder(para, placeholder, value)
    for para in section.footer.paragraphs:
        replace_placeholder(para, placeholder, value)
```

## Nested Tables

Tables can contain tables. Process recursively:

```python
def process_table(table, data):
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                for key, value in data.items():
                    replace_placeholder(para, '{{' + key + '}}', value)
            # Handle nested tables
            for nested_table in cell.tables:
                process_table(nested_table, data)
```

## Conditional Sections

Remove paragraphs between conditional markers when condition is false:

```python
def handle_conditional(doc, marker, keep):
    start_marker = '{{IF_' + marker + '}}'
    end_marker = '{{END_IF_' + marker + '}}'

    removing = False
    to_remove = []

    for para in doc.paragraphs:
        if start_marker in para.text:
            removing = not keep
            to_remove.append(para)
            continue
        if end_marker in para.text:
            removing = False
            to_remove.append(para)
            continue
        if removing:
            to_remove.append(para)

    for para in to_remove:
        p = para._element
        p.getparent().remove(p)
```

## Complete Usage

```python
from docx import Document

doc = Document('template.docx')

data = {
    'CANDIDATE_NAME': 'John Smith',
    'POSITION': 'Software Engineer',
    'START_DATE': '2024-01-15',
    'SALARY': '$120,000',
}

# Replace in body paragraphs
for para in doc.paragraphs:
    for key, value in data.items():
        replace_placeholder(para, '{{' + key + '}}', value)

# Replace in tables
for table in doc.tables:
    process_table(table, data)

# Replace in headers/footers
for section in doc.sections:
    for para in section.header.paragraphs:
        for key, value in data.items():
            replace_placeholder(para, '{{' + key + '}}', value)
    for para in section.footer.paragraphs:
        for key, value in data.items():
            replace_placeholder(para, '{{' + key + '}}', value)

# Handle conditionals
handle_conditional(doc, 'BONUS', has_bonus)

doc.save('output.docx')
```
