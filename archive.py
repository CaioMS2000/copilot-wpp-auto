import os
from pathlib import Path

def combine_code_files():
    output_file = "project_code.txt"
    extensions = {'.py', '.js', '.ts', '.json', '.yml', '.yaml'}
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk('.'):
            # Skip virtual environment directories and __pycache__
            if '.venv' in root or '__pycache__' in root or '.git' in root or '.vscode' in root:
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to('.')
                    
                    if file == '__init__.py' and os.path.getsize(file_path) == 0:
                        continue
                    
                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f"File: {relative_path}\n")
                    outfile.write(f"{'='*80}\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                            outfile.write('\n')
                    except Exception as e:
                        outfile.write(f"Error reading file: {e}\n")

if __name__ == "__main__":
    combine_code_files()
