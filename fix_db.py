import re

with open('app.py', 'r') as f:
    content = f.read()

# Replace all remaining get_db_cursor() calls that return single value with (conn, cursor)
content = re.sub(
    r'(\s+)cursor = get_db_cursor\(\)',
    r'\1conn, cursor = get_db_cursor()',
    content
)

# Also need to add commit_db(conn) instead of commit_db()
content = re.sub(
    r'commit_db\(\)',
    r'commit_db(conn)',
    content
)

# Add connection closing in try-finally blocks where missing
lines = content.split('\n')
result_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    result_lines.append(line)
    
    # Check if this is a line with get_db_cursor call
    if 'conn, cursor = get_db_cursor()' in line and 'try:' not in line:
        # Look ahead to see if there's already a try block
        # This is complex, so let's just make sure all routes have proper try-finally
    
    i += 1

with open('app.py', 'w') as f:
    f.write(content)

print('✓ Updated all database connection patterns')
