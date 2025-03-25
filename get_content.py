import os

# Get the directory where this script is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Path for the master text file where everything will be pasted
master_file_path = os.path.join(current_directory, 'master_file.txt')

# List of directories to skip
directories_to_skip = {'.angular', '.vscode', 'cypress', 'node_modules', 'dist', '.dart_tool', '.idea', 'build', 'test', 'windows', 'linux', 'venv', 'Testing Ingredients', '.git'}

# Open the master file in write mode
with open(master_file_path, 'w', encoding='utf-8') as master_file:
    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(current_directory):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in directories_to_skip]
        
        for file in files:
            # Ignore the master file and package-lock.json
            if file == 'master_file.txt' or file == 'package-lock.json':
                continue
            
            # Get the full path of the file
            file_path = os.path.join(root, file)
            
            # Try to read and append the content of the file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Write a label for each file's content
                    master_file.write(f"\n{'='*40}\n")
                    master_file.write(f"FILE: {file_path}\n")
                    master_file.write(f"{'='*40}\n")
                    
                    # Write the content of the current file into the master file
                    master_file.write(content)
                    master_file.write("\n\n")  # Add spacing after each file content
            except Exception as e:
                # If there's an error, log the filename and the error message
                print(f"Error reading {file_path}: {e}")

print(f"All files' contents have been written to {master_file_path}")