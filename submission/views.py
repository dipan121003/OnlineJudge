# submission/views.py
from django.shortcuts import render
from django.conf import settings
import os
import uuid
import subprocess
from pathlib import Path
from .forms import CodeSubmissionForm
from django.contrib.auth.decorators import login_required

@login_required
def submit_code(request):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            # Don't save to the database yet, we need the output first
            submission = form.save(commit=False)
            
            # 2. Assign the logged-in user to the submission
            submission.user = request.user

            output = run_code(
                submission.language, submission.code, submission.input_data
            )

            submission.output_data = output
            submission.save() # Now save the complete object

            return render(request, "submission/result.html", {"submission": submission})
    else:
        form = CodeSubmissionForm()
    return render(request, "submission/result.html", {"form": form})

def run_code(language, code, input_data):
    # Your run_code function is great. Let's make a few small improvements.
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    unique = str(uuid.uuid4())

    # Define file paths
    code_file_path = codes_dir / f"{unique}.{language}"
    input_file_path = inputs_dir / f"{unique}.txt"
    output_file_path = outputs_dir / f"{unique}.txt"

    # Write code and input to files
    code_file_path.write_text(code)
    input_file_path.write_text(input_data)

    output_data = ""
    command = []

    if language == "py":
        command = ["python", str(code_file_path)]
    elif language == "cpp":
        executable_path = codes_dir / unique
        compile_process = subprocess.run(
            ["g++", str(code_file_path), "-o", str(executable_path)],
            capture_output=True, text=True
        )
        if compile_process.returncode != 0:
            return f"Compilation Error:\n{compile_process.stderr}"
        command = [str(executable_path)]

    # Execute the code
    try:
        with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
            subprocess.run(
                command,
                stdin=input_file,
                stdout=output_file,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10 # Add a timeout!
            )
        output_data = output_file_path.read_text()
    except subprocess.TimeoutExpired:
        output_data = "Execution Timed Out (10 seconds)"
    except Exception as e:
        output_data = f"An unexpected error occurred: {str(e)}"

    return output_data