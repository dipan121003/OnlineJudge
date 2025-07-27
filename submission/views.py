# submission/views.py
from django.shortcuts import render
from django.conf import settings
import os
import uuid
import subprocess
from pathlib import Path
from .forms import CodeSubmissionForm
from django.contrib.auth.decorators import login_required
from problems.models import Problem
from .models import CodeSubmission
from django.shortcuts import get_object_or_404, redirect

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

@login_required
def submit_solution(request, problem_id):
    # Get the specific problem we are submitting a solution for
    problem = get_object_or_404(Problem, id=problem_id)
    
    if request.method == 'POST':
        # Create a form instance with the submitted data
        form = CodeSubmissionForm(request.POST)
        
        if form.is_valid():
            # Create a submission object in memory without saving to the database yet
            submission = form.save(commit=False)
            
            # Add the user and problem to the submission object
            submission.user = request.user
            submission.problem = problem # Link the submission to the problem
            
            # Determine the final verdict by running against all official test cases
            final_verdict = "Accepted" # Assume success initially
            test_cases = problem.test_cases.all()

            if not test_cases.exists():
                final_verdict = "System Error: No Test Cases"
            else:
                for case in test_cases:
                    # Use your existing run_code utility for each test case
                    output = run_code(submission.language, submission.code, case.input_data)
                    
                    # Check for execution errors first
                    if "Error" in output or "Timed Out" in output:
                        final_verdict = output # Set verdict to the error message
                        break # Stop checking other test cases

                    # Check if the code's output matches the test case's expected output
                    if output.strip() != case.output_data.strip():
                        final_verdict = "Wrong Answer"
                        break # Stop on the first wrong answer
            
            # Add the final verdict to our submission object
            submission.verdict = final_verdict
            
            # Now, save the complete submission object to the database
            # The UUID for the 'id' will be generated automatically here
            submission.save()

            # Redirect to the result page, passing the new submission's ID
            return redirect('submission_result', submission_id=submission.id)

    # If the request is not POST, just redirect back to the problem page
    return redirect('problem_detail', problem_id=problem_id)


# This view remains the same, but it now displays a CodeSubmission object
@login_required
def submission_result(request, submission_id):
    # We fetch a CodeSubmission object instead of a Solution object
    submission = get_object_or_404(CodeSubmission, id=submission_id)
    return render(request, 'submission/solution_result.html', {'submission': submission})

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