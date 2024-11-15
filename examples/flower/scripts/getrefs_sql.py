import json
import os
import sqlite3
from typing import List, Tuple

# Load JSON data
def load_json(path):
    """Load JSON data from a file."""
    with open(path, 'r') as f:
        return json.load(f)

# Function to create tables and import data into the SQLite database
def import_json_to_sqlite(db_path: str, label_defs_path: str, label_refs_path: str):
    """Create tables and import JSON data into the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables for label definitions and references
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS label_defs (
        label TEXT,
        def_file TEXT,
        def_line INTEGER,
        def_content TEXT
    )
    ''')
    cursor.execute('delete from label_defs')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS label_refs (
        label TEXT,
        ref_file TEXT,
        ref_line INTEGER,
        ref_content TEXT
    )
    ''')
    cursor.execute('delete from label_refs')

    # Import label_defs.json data into label_defs table
    label_defs = load_json(label_defs_path)
    for label, defs in label_defs.items():
        for entry in defs:
            cursor.execute('''
            INSERT INTO label_defs (label, def_file, def_line, def_content)
            VALUES (?, ?, ?, ?)
            ''', (label, entry["def_file"], entry["def_line"], entry["def_content"]))

    # Import label_refs.json data into label_refs table
    label_refs = load_json(label_refs_path)
    for label, refs in label_refs.items():
        for entry in refs:
            cursor.execute('''
            INSERT INTO label_refs (label, ref_file, ref_line, ref_content)
            VALUES (?, ?, ?, ?)
            ''', (label, entry["ref_file"], entry["ref_line"], entry["ref_content"]))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Data successfully imported into {db_path}")

def get_label_dependencies(db_path: str, ref_file: str, max_depth: int = 10) -> List[Tuple[str, str, str, str]]:
    """
    Retrieve all dependencies for labels referenced in a specified file, with a maximum recursion depth.

    Returns:
        List[Tuple[str, str, str, str]]: A list of tuples with (root_file, current_file, depends_on_file, label).
    """
    query = """
    WITH RECURSIVE recursive_deps(depth, root_file, current_file, depends_on_file, label) AS (
        -- Anchor member
        SELECT
            1 AS depth,
            r.ref_file AS root_file,
            r.ref_file AS current_file,
            d.def_file AS depends_on_file,
            r.label AS label
        FROM label_refs AS r
        JOIN label_defs AS d ON r.label = d.label
        WHERE r.ref_file = ?

        UNION ALL

        -- Recursive member
        SELECT
            rd.depth + 1,
            rd.root_file,
            rd.depends_on_file AS current_file,
            d.def_file AS depends_on_file,
            r.label AS label
        FROM recursive_deps AS rd
        JOIN label_refs AS r ON r.ref_file = rd.depends_on_file
        JOIN label_defs AS d ON r.label = d.label
        WHERE rd.depth < ?
          AND rd.depends_on_file != rd.current_file
    )
    SELECT DISTINCT root_file, current_file, depends_on_file, label
    FROM recursive_deps
    ORDER BY depth;
    """

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query with the specified ref_file and max_depth
    cursor.execute(query, (ref_file, max_depth))
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    return results


if __name__ == "__main__":
    # Define parameters
    scripts_dir = "scripts"
    os.makedirs(scripts_dir, exist_ok=True)
    db_path = os.path.join(scripts_dir, "data.sqlite")  # Path to SQLite database
    label_defs_path = "basic/label_defs.json"           # Path to label definitions JSON
    label_refs_path = "basic/label_refs.json"           # Path to label references JSON
    ref_file = "tmp.asm"                                # File name to search for dependencies
    max_depth = 10                                      # Maximum recursion depth

    # Import JSON data into SQLite database
    if True: import_json_to_sqlite(db_path, label_defs_path, label_refs_path)

    if False:
        # Retrieve and print dependencies for the specified file
        dependencies = get_label_dependencies(db_path, ref_file, max_depth)
        print(f"Dependencies for '{ref_file}':")
        for root_label, current_file, depends_on_label in dependencies:
            print(f"Root Label: {root_label}, Current File: {current_file}, Depends On: {depends_on_label}")
