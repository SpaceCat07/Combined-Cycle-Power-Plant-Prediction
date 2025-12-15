
import os

file_path = 'templates/charts.html'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
fixed = False
while i < len(lines):
    line = lines[i]
    # Check for the broken line
    if 'chartData = {{ chart_data | safe }' in line and '}};' not in line:
        print(f"Found broken line at {i+1}: {line.strip()}")
        # Replace with correct line
        new_lines.append('                        chartData = {{ chart_data | safe }};\n')
        fixed = True
        
        # Check if next line is the stray closing brace
        if i + 1 < len(lines):
            next_line = lines[i+1]
            if next_line.strip() == '};':
                print(f"Removing stray closing brace at {i+2}: {next_line.strip()}")
                i += 1 # Skip next line
    else:
        new_lines.append(line)
    i += 1

if fixed:
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    print("File patched successfully.")
else:
    print("Target line not found or already fixed.")
