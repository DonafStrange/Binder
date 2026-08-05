# Binder - Research Work Management System
<img width="1920" height="1048" alt="Screenshot from 2026-08-04 18-08-03" src="https://github.com/user-attachments/assets/8761152b-8ee5-417f-b4aa-84ae6221e227" />

## Overview

**Binder** is a research documents management system designed to organize scientific projects, notes, references, and associated files in a structured way.

The goal of Binder is to provide a local, lightweight alternative to traditional reference managers by combining:

* Research project organization
* Markdown-based note taking
* Reference library management
* File and attachment organization
* Tag-based knowledge linking
* Structured metadata storage using SQLite

The application is designed for researchers, students, and academics who need to manage multiple projects, papers, experiments, and ideas in one place.

---

# Directory Structure

The main directory contains the following components:

```
Binder/
│
├── app.py                  # Main application launcher
│
├── database/
│   └── database.db         # SQLite database
│
├── services/               # Backend logic
│   ├── work_service.py
│   ├── reference_service.py
│   ├── attachment.py
│   └── markdown_service.py
│
├── widgets/                # GUI components
│   ├── properties_panel.py
│   ├── reference_library.py
│   ├── project_tree.py
│   └── ...
│
├── models/                 # Data models
│
├── ui/                     # Application windows
│
├── works/                  # Research projects
│   └── Work_Name/
│       ├── note.md
│       ├── pdf/
│       ├── images/
│       └── files/
│
├── reference_library/      # Stored references
│   └── ref_xxxxxx/
│       ├── notes.md
│       ├── figures/
│       ├── supplementary/
│       └── reference files
│
├── attachments/            # Global attachments
│
├── requirements.txt        # Python dependencies
│
└── README.md
```

---

# Features

## 1. Work / Project Management

Binder organizes research activities into independent works.

Each work contains:

* Title
* Category
* Creation date
* Modification date
* Markdown notes
* Attached files
* Tags
* Linked references

Example:

```
Computational Neuroscience:
Mathematical Modelling of Brain Dynamics

    note.md
    papers/
    figures/
    datasets/
```

---

# 2. Markdown Based Notes

Each work contains a `note.md` file.

Markdown allows:

* Writing research notes
* Adding equations
* Creating lists
* Embedding images
* Adding citations

Example:

```markdown
Computational neuroscience combines neuroscience,
mathematics, physics and computer science.

<a href="reference-pdf://Ref000015">
Ref000015
</a>
```

---

# 3. Reference Library

Binder maintains a separate reference database.

Each reference contains:

* Citation key
* Title
* PDF/document
* Notes
* Figures
* Supplementary files

Example:

```
reference_library/

ref_000015/

    Mathematical framework.pdf
    notes.md
    figures/
    supplementary/
```

References can be linked to multiple research works.

---

# 4. Tags

Tags allow linking and categorizing different works.

Example tags:

```
computational neuroscience
EEG
brain modelling
machine learning
dynamical systems
```

A work can have multiple tags.

Tags are stored using a many-to-many database relationship:

```
works
 |
 |
work_tags
 |
 |
tags
```

This allows future features such as:

* Searching by tags
* Related work discovery
* Knowledge graph generation

---

# 5. Attachments

Attachments can include:

* PDFs
* Images
* Research files

They are organized separately:

```
attachments/

    pdf/
    images/
    files/
```

---

# Installation

## Requirements

Binder requires:

* Python >= 3.10
* SQLite3
* PySide6

---

# Download the Repository

Clone the repository:

```bash
git clone https://github.com/DonafStrange/Binder.git
```

Move into the project directory:

```bash
cd Binder
```

---

# Create Virtual Environment (Recommended)

Create an isolated Python environment:

```bash
python -m venv binderenv
```

Activate it.

### Linux / macOS

```bash
source binderenv/bin/activate
```

### Windows

```bash
binderenv\Scripts\activate
```

---

# Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

---

# Running the Application

Start Binder using:

```bash
python app.py
```

The graphical interface will open.

---

# Current Application Options

## Main Interface

Currently available modules:

### Projects

Manage research works.

Available information:

* Work title
* Category
* Creation date
* Modification date
* Notes

---

## Properties Panel

For the selected work:

### Work Information

Displays:

* Title
* Category
* Created date
* Modified date

### Tags

Displays all tags associated with the work.

(Currently implemented)

* Add tags through database service
* Display tags for selected work

### References

Displays references cited in the selected work.

Citation extraction is based on citation keys.

Example:

```
Ref000015
WILSON19721
```

---

### Attachments

Displays files linked inside the Markdown document.

Supported Markdown links:

```markdown
[paper.pdf](path/to/file.pdf)

![figure](path/to/image.png)
```

---

# Database

Binder uses SQLite.

Current tables:

```
works

reference_library

tags

work_tags
```

The database is located at:

```
database/database.db
```

---

# Development Status

Current implemented features:

* [x] Work creation
* [x] Work deletion
* [x] Markdown notes
* [x] Reference library
* [x] Reference linking
* [x] Attachments
* [x] Tag database system
* [x] Tag display in properties

Planned features:

* [ ] Tag editing from GUI
* [ ] Tag search
* [ ] Reference import from BibTeX
* [ ] Citation manager
* [ ] Knowledge graph visualization
* [ ] Full-text search
* [ ] Cloud synchronization
* [ ] Export/import backup system

---

# Technologies Used

## Programming Language

* Python

## GUI

* PySide6

## Database

* SQLite

## Data Format

* Markdown

## Scientific Libraries

* NumPy
* SciPy
* Matplotlib

---

# License

This project is currently under development.

License information will be added later.

---

# Author

Developed as a personal research productivity tool for managing computational neuroscience and scientific projects and still in progress.
