import os
import re

def remove_comments_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        in_docstring = False
        docstring_quote = None
        
        for line in lines:
            if '"""' in line:
                triple_quote_count = line.count('"""')
                if not in_docstring and triple_quote_count >= 1:
                    in_docstring = True
                    docstring_quote = '"""'
                    if triple_quote_count >= 2:
                        in_docstring = False
                elif in_docstring and docstring_quote == '"""':
                    in_docstring = False
                new_lines.append(line)
                continue
            elif "'''" in line:
                triple_quote_count = line.count("'''")
                if not in_docstring and triple_quote_count >= 1:
                    in_docstring = True
                    docstring_quote = "'''"
                    if triple_quote_count >= 2:
                        in_docstring = False
                elif in_docstring and docstring_quote == "'''":
                    in_docstring = False
                new_lines.append(line)
                continue
            
            if in_docstring:
                new_lines.append(line)
                continue
            
            if re.match(r'^\s*#.*$', line):
                continue
            
            if '#' in line:
                in_single_quote = False
                in_double_quote = False
                i = 0
                while i < len(line):
                    char = line[i]
                    if char == "'" and not in_double_quote and (i == 0 or line[i-1] != '\\'):
                        in_single_quote = not in_single_quote
                    elif char == '"' and not in_single_quote and (i == 0 or line[i-1] != '\\'):
                        in_double_quote = not in_double_quote
                    elif char == '#' and not in_single_quote and not in_double_quote:
                        line = line[:i].rstrip() + '\n'
                        break
                    i += 1
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f'Processed: {filepath}')
    except Exception as e:
        print(f'Error processing {filepath}: {e}')

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py') and file != 'remove_comments.py':
            filepath = os.path.join(root, file)
            remove_comments_from_file(filepath)

print('Completed removing comments from all Python files')
