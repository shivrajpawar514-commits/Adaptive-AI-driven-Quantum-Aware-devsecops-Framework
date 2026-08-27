import os
import re
from collections import defaultdict
import json

def audit_repo():
    files_to_check = []
    for root, _, files in os.walk('.'):
        if any(x in root for x in ['.venv', '__pycache__', '.git', 'node_modules']):
            continue
        for f in files:
            if f.endswith('.py') or f.endswith('.js') or f == 'Dockerfile':
                files_to_check.append(os.path.join(root, f))
    
    findings = {
        'todos': [],
        'print_statements': [],
        'console_log': [],
        'missing_docstrings': [],
        'missing_type_hints': [],
        'api_responses': defaultdict(list)
    }

    def_regex = re.compile(r'^\s*def\s+(\w+)\s*\((.*?)\)(?:.*?:)?\s*$')
    class_regex = re.compile(r'^\s*class\s+(\w+).*?:')

    for filepath in files_to_check:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        in_docstring = False
        in_function = False
        func_name = ""
        has_docstring = False
        has_type_hints = False

        for i, line in enumerate(lines):
            line_str = line.strip()
            
            # TODOs
            if 'TODO' in line_str or 'placeholder' in line_str.lower() or 'pass' == line_str:
                findings['todos'].append(f"{filepath}:{i+1}: {line_str}")
                
            # Logging
            if filepath.endswith('.py') and 'print(' in line_str and not line_str.startswith('#'):
                findings['print_statements'].append(f"{filepath}:{i+1}")
            if filepath.endswith('.js') and 'console.log(' in line_str and not line_str.startswith('//'):
                findings['console_log'].append(f"{filepath}:{i+1}")
                
            # API responses
            if 'res.status(' in line_str or 'res.json(' in line_str or 'res.send(' in line_str:
                findings['api_responses'][filepath].append(f"Line {i+1}: JS Response")
            if 'JSONResponse(' in line_str or 'return {' in line_str:
                findings['api_responses'][filepath].append(f"Line {i+1}: PY Response")
                
            # Naive python func check for docstrings and type hints
            if filepath.endswith('.py'):
                match = def_regex.match(line)
                if match:
                    func_name = match.group(1)
                    args = match.group(2)
                    in_function = True
                    has_docstring = False
                    has_type_hints = ':' in args or '->' in line
                    
                    if not has_type_hints and func_name not in ['__init__']:
                        findings['missing_type_hints'].append(f"{filepath}:{i+1} {func_name}")
                        
                    # Check next few lines for docstring
                    for j in range(i+1, min(i+5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line.startswith('\"\"\"') or next_line.startswith('\'\'\''):
                            has_docstring = True
                            break
                        if next_line and not next_line.startswith('#'):
                            break
                            
                    if not has_docstring:
                        findings['missing_docstrings'].append(f"{filepath}:{i+1} {func_name}")

    with open('audit_results.json', 'w') as f:
        json.dump(findings, f, indent=2)

if __name__ == '__main__':
    audit_repo()
