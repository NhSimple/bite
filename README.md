# Bite - SQLite Database Viewer

Bite is a command-line interface tool for viewing and interacting with SQLite databases. It provides an easy-to-use, interactive way to explore SQLite database contents directly from your terminal.

## Features

- Browse tables in SQLite databases
- View table contents with pagination
- Sort table data by columns
- Search within tables
- Horizontal scrolling for wide tables

## Installation

To install Bite, follow these steps:

1. Clone the repository:
2. git clone https://github.com/NhSimple/bite.git
cd bite

2. Install the package:
pip install -e .

## Usage

After installation, you can use Bite by running:
bite <path_to_sqlite_database>

For example:
bite mydatabase.db

## Navigation

Once you've opened a database, you can:

- Use arrow keys to navigate through tables and data
- Press 'q' to quit the current view or the application
- Press 's' to sort by a column
- Press 'f' to search within the current table
- Use 'h' and 'l' to scroll horizontally in wide tables
- Use Page Up and Page Down to navigate through pages of data

## Requirements

- Python 3.6+
- blessed
- simple-term-menu

## Contributing

Contributions to Bite are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Author

Created by [NhSimple](https://github.com/NhSimple)

