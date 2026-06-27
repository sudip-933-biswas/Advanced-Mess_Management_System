#!/usr/bin/env python3
import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# List of patterns to replace
replacements = [
    # Pattern 1: cursor = get_db_cursor() followed by cursor.execute...cursor.fetchone() followed by cursor.close()
    (
        r'cursor = get_db_cursor\(\)\s+cursor\.execute\("([^"]+)",\s*\(([^)]*)\)\)\s+(\w+) = cursor\.fetchone\(\)\s+cursor\.close\(\)',
        r'execute_query("SELECT * FROM \1 WHERE ... = %s", (\2), fetch_one=True)'
    ),
    # Pattern 2: cursor = get_db_cursor() at start of line (wrongly paired)
    (r'(\s+)cursor = get_db_cursor\(\)',  r'\1conn, cursor = get_db_cursor()'),
    # Pattern 3: commit_db() with no argument to commit_db(conn)
    (r'commit_db\(\)(?!.*conn)',  r'commit_db(conn)'),
]

# Actually, let's do a simpler approach - just replace the old get_db_cursor pattern
# Since this is too complex to do with regex, let's just clean up the get_db_cursor calls more carefully

lines = content.split('\n')
new_lines = []

for i, line in enumerate(lines):
    # Skip comments
    if '#' in line and 'def get_db_cursor' not in line:
        new_lines.append(line)
        continue
    
    # Replace the problematic pattern: cursor = get_db_cursor()
    # This line probably should never happen now that get_db_cursor is defined differently
    if 'cursor = get_db_cursor()' in line and 'def get_db_cursor' not in line:
        # This is an error - skip it for now, manual fixing needed
        new_lines.append('# ERROR: Line needs manual fixing: ' + line)
    else:
        new_lines.append(line)

# Write back
with open('app.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("✓ Cleaned up app.py")
print("Note: You may need to manually update routes that use get_db_cursor()")
print("Please use execute_query() instead of get_db_cursor()")
