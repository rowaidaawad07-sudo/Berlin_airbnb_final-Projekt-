import os

# Define the path containing the files
# If the files are in the same folder as run_all.py, use "."
# If they are in a folder named src, use "src/"
folder = "src/" 

#   list of files to run
files = [
    "data_cleaning.py",
    "eda_analysis.py",
    "statistical_analysis.py",
    "import_raw_data.py",
    "relational_model.py"
]

for file in files:
    file_path = os.path.join(folder, file)
    print(f"Running {file_path}...")
    # use the virtual environment (.venv)
    os.system(f"python {file_path}")

print("All tasks completed!")