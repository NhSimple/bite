import os
import sqlite3
import sys
from blessed import Terminal
from simple_term_menu import TerminalMenu


def display_table_data(term, conn, table_name):
    current_row = 0
    horizontal_scroll = 0
    rows_per_page = term.height - 5  # Adjust for title, header, and footer
    sort_column_index = 0  # Default to first column
    sort_order = "ASC"
    search_term = ""

    def print_table(columns, data, highlight_col):
        nonlocal horizontal_scroll, max_scroll
        print(term.clear)
        print(term.bold(term.center(f"Table: {table_name}")))
        print()

        # Calculate column widths
        col_widths = [
            max(len(str(row[i])) for row in data + [columns])
            for i in range(len(columns))
        ]
        col_widths = [max(width, 10) for width in col_widths]  # Minimum width of 10

        # Calculate total width and visible columns
        total_width = sum(col_widths) + len(columns) * 2
        visible_width = term.width - 2

        # Recalculate max_scroll
        max_scroll = max(0, len(columns) - 1)
        horizontal_scroll = min(horizontal_scroll, max_scroll)

        visible_columns = []
        current_width = 0
        for i, width in enumerate(col_widths[horizontal_scroll:]):
            if current_width + width > visible_width:
                break
            visible_columns.append(i + horizontal_scroll)
            current_width += width + 2

        # Display header
        header = ""
        for i in visible_columns:
            col = columns[i]
            if i == highlight_col:
                header += term.bold(col.ljust(col_widths[i] + 2))
            else:
                header += term.bold(col.ljust(col_widths[i] + 2))
        print(header[:visible_width])
        print(term.bold("-" * min(visible_width, total_width)))

        # Display data
        for row in data:
            row_str = ""
            for i in visible_columns:
                row_str += str(row[i]).ljust(col_widths[i] + 2)
            print(row_str[:visible_width])

        # Display scroll indicator
        if total_width > visible_width and max_scroll > 0:
            scroll_percent = (horizontal_scroll / max_scroll) * 100
            scroll_bar = f"[{' ' * int(scroll_percent // 10)}|{' ' * (10 - int(scroll_percent // 10))}]"
            print(term.move_y(term.height - 3) + term.center(scroll_bar))

        # Display left/right indicators
        if horizontal_scroll > 0:
            print(term.move_xy(0, term.height - 3) + "<<")
        if horizontal_scroll < max_scroll:
            print(term.move_xy(term.width - 2, term.height - 3) + ">>")

        return total_width, visible_width, len(columns)

    def prompt_for_sort(columns):
        print(term.clear)
        print(term.bold(term.center("Sort by Column")))
        print()
        for i, col in enumerate(columns):
            print(f"{i}: {col}")
        print()
        return input("Enter column number to sort by: ")

    columns = get_columns(conn, table_name)
    max_scroll = max(0, len(columns) - 1)

    while True:
        # Construct the SQL query with search and sorting
        search_clause = (
            f"WHERE {' OR '.join([f'{col} LIKE ?' for col in columns])}"
            if search_term
            else ""
        )
        sort_clause = f"ORDER BY [{columns[sort_column_index]}] {sort_order}"
        query = f"SELECT * FROM [{table_name}] {search_clause} {sort_clause} LIMIT {rows_per_page} OFFSET {current_row}"

        cursor = conn.cursor()
        if search_term:
            cursor.execute(query, tuple(["%" + search_term + "%"] * len(columns)))
        else:
            cursor.execute(query)
        data = cursor.fetchall()

        # Get total number of filtered rows
        count_query = f"SELECT COUNT(*) FROM [{table_name}] {search_clause}"
        if search_term:
            cursor.execute(count_query, tuple(["%" + search_term + "%"] * len(columns)))
        else:
            cursor.execute(count_query)
        total_rows = cursor.fetchone()[0]

        total_width, visible_width, total_columns = print_table(
            columns, data, sort_column_index
        )

        # Display footer
        footer = f"Showing rows {current_row+1}-{min(current_row+rows_per_page, total_rows)} of {total_rows}"
        sorted_by = f"Sorted by: {columns[sort_column_index]} ({sort_order})"
        footer += f" | {term.color_rgb(173, 216, 230)}{sorted_by}{term.normal}"
        if search_term:
            footer += f" | Search: {search_term}"
        footer += " | 'q': Quit, 's': Sort, 'f': Search, ←/→: Change Sort, 'h'/'l': Scroll Left/Right, ↑/↓: Navigate, PgUp/PgDn: Page"
        print(term.move_y(term.height - 2) + footer)

        # Handle key presses
        with term.cbreak(), term.hidden_cursor():
            key = term.inkey()
            if key.lower() == "q":
                return  # Exit the function, returning to the main menu
            elif key.lower() == "s":
                col_num = prompt_for_sort(columns)
                try:
                    col_num = int(col_num)
                    if 0 <= col_num < len(columns):
                        if sort_column_index == col_num:
                            # If same column, toggle sort order
                            sort_order = "DESC" if sort_order == "ASC" else "ASC"
                        else:
                            # If new column, default to ASC
                            sort_column_index = col_num
                            sort_order = "ASC"
                except ValueError:
                    pass  # Invalid input, do nothing
            elif key.lower() == "f":
                search_term = input("Enter search term: ")
                current_row = 0  # Reset to first page after searching
            elif key.lower() == "h" and horizontal_scroll > 0:
                horizontal_scroll -= 1
            elif key.lower() == "l" and horizontal_scroll < max_scroll:
                horizontal_scroll += 1
            elif key.name == "KEY_LEFT" and sort_column_index > 0:
                sort_column_index -= 1
            elif key.name == "KEY_RIGHT" and sort_column_index < len(columns) - 1:
                sort_column_index += 1
            elif key.name == "KEY_UP" and current_row > 0:
                current_row = max(0, current_row - 1)
            elif key.name == "KEY_DOWN" and current_row + rows_per_page < total_rows:
                current_row += 1
            elif key.name == "KEY_PGUP":  # Page Up
                current_row = max(0, current_row - rows_per_page)
            elif key.name == "KEY_PGDOWN":  # Page Down
                current_row = min(
                    total_rows - rows_per_page, current_row + rows_per_page
                )

            key = term.inkey()
            if key.lower() == "q":
                return  # Exit the function, returning to the main menu
            elif key.lower() == "s":
                col_num = prompt_for_sort(columns)
                try:
                    col_num = int(col_num)
                    if 0 <= col_num < len(columns):
                        if sort_column_index == col_num:
                            # If same column, toggle sort order
                            sort_order = "DESC" if sort_order == "ASC" else "ASC"
                        else:
                            # If new column, default to ASC
                            sort_column_index = col_num
                            sort_order = "ASC"
                except ValueError:
                    pass  # Invalid input, do nothing
            elif key.lower() == "f":
                search_term = input("Enter search term: ")
                current_row = 0  # Reset to first page after searching
            elif key.lower() == "h" and horizontal_scroll > 0:
                horizontal_scroll = max(0, horizontal_scroll - 1)
            elif key.lower() == "l" and horizontal_scroll < max_scroll:
                horizontal_scroll += 1
            elif key.name == "KEY_LEFT" and sort_column_index > 0:
                sort_column_index -= 1
            elif key.name == "KEY_RIGHT" and sort_column_index < len(columns) - 1:
                sort_column_index += 1
            elif key.name == "KEY_UP" and current_row > 0:
                current_row = max(0, current_row - 1)
            elif key.name == "KEY_DOWN" and current_row + rows_per_page < total_rows:
                current_row += 1
            elif key.name == "KEY_PGUP":  # Page Up
                current_row = max(0, current_row - rows_per_page)
            elif key.name == "KEY_PGDOWN":  # Page Down
                current_row = min(
                    total_rows - rows_per_page, current_row + rows_per_page
                )


def get_columns(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info([{table_name}])")
    return [row[1] for row in cursor.fetchall()]


def connect_to_db(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def get_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]


def get_table_data(conn, table_name, offset=0, limit=10):
    cursor = conn.cursor()

    # Get the total number of rows
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_rows = cursor.fetchone()[0]

    # Get the rows with offset and limit
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset};")
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()

    return columns, data, total_rows


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m bite <database_file>")
        sys.exit(1)

    db_file = sys.argv[1]
    if os.path.exists(db_file):
        conn = connect_to_db(db_file)
    else:
        print(f"Database file '{db_file}' does not exist.")
        sys.exit(1)

    term = Terminal()

    while True:
        tables = get_tables(conn)
        terminal_menu = TerminalMenu(tables, title="Select a table:")
        table_index = terminal_menu.show()

        if table_index is None:
            break

        selected_table = tables[table_index]
        display_table_data(term, conn, selected_table)

    conn.close()


if __name__ == "__main__":
    main()
