import os
import re

files = [
    'setup.py',
    'stages/stage_6_qa.py',
    'stages/stage_7_email.py',
    'stages/stage_8_jira_close.py'
]

base_path = r'C:\Users\Abc\Documents\Zero Human Touch Pipeline\pipeline'
os.chdir(base_path)

print("Starting replacements...")

for file in files:
    if not os.path.exists(file):
        print(f'File not found: {file}')
        continue
    
    print(f'Processing: {file}')
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace \\\" with \"
    count1 = content.count(r'\"')
    content = content.replace(r'\"', '"')
    
    # Replace \\n with actual newlines
    count2 = content.count(r'\n')
    content = content.replace(r'\n', '\n')
    
    # Replace \\\\ with \\
    count3 = content.count(r'\\')
    content = content.replace(r'\\', '\\')
    
    if content != original_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {file}')
        print(f'  Replacements of \\\\\": {count1}')
        print(f'  Replacements of \\\\n: {count2}')
        print(f'  Replacements of \\\\\\\\: {count3}')
    else:
        print(f'No changes needed in: {file}')

print("Done!")
