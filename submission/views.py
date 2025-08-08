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
import google.generativeai as genai
from dotenv import load_dotenv
import docker
import tempfile

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
            
            problem = submission.problem 
            context = {
                "submission": submission,
                "problem": problem, # Add the problem to the context
            }

            return render(request, "submission/result.html", context)
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
                    output = run_code(submission.language, submission.code, case.input_data, problem.memory_limit)
                    
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

def run_code(language, code, input_data, memory_limit=256):
    # 1. Initialize Docker client
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        return "Error: Docker is not running or misconfigured."

    # 2. Create a temporary directory on the host machine
    # This directory will be shared with the container
    with tempfile.TemporaryDirectory() as temp_dir:
        host_dir = Path(temp_dir)
        
        # Determine the filename based on the language
        if language == "py":
            filename = "main.py"
        elif language == "cpp":
            filename = "main.cpp"
        elif language == "java":
            filename = "Main.java"
        else:
            return "Unsupported language."

        # 3. Save the user's code and input data into the temporary directory
        (host_dir / filename).write_text(code)
        (host_dir / "input.txt").write_text(input_data)

        # 4. Define the command to be executed inside the container
        # This script compiles (if necessary) and runs the code, redirecting I/O
        if language == "py":
            container_command = "/bin/sh -c 'python main.py < input.txt'"
        elif language == "cpp":
            container_command = "/bin/sh -c 'g++ main.cpp -o main && ./main < input.txt'"
        elif language == "java":
            container_command = "/bin/sh -c 'javac Main.java && java Main < input.txt'"

        # 5. Run the code in a new, isolated Docker container
        try:
            container = client.containers.run(
                image="onlinejudge-web:latest", # Use the image you build with docker-compose
                command=container_command,
                volumes={host_dir: {'bind': '/sandbox', 'mode': 'rw'}},
                working_dir="/sandbox",
                mem_limit=f"{memory_limit}m",       # Set memory limit
                nano_cpus=int(0.5 * 1e9),              # Set CPU limit
                network_disabled=True,  # Disable network access
                detach=True,            # Run in the background
            )

            # Wait for the container to finish, with a timeout
            result = container.wait(timeout=10)
            
            # Get the output from the container's logs
            output_data = container.logs(stdout=True, stderr=True).decode('utf-8')

            # Check for errors
            if result['StatusCode'] != 0:
                # If there's an error, the output_data likely contains the error message
                return f"Execution Error:\n{output_data}"

        except docker.errors.ContainerError as e:
            return f"Container Error: {e}"
        except Exception as e:
            # This catches timeouts and other exceptions
            return f"An error occurred: {e}"
        finally:
            # 6. Clean up: Stop and remove the container
            try:
                container.stop()
                container.remove()
            except NameError:
                pass # Container was never created

    return output_data

@login_required
def get_ai_suggestion(request, problem_id):
    # --- 1. SETUP ---
    problem = get_object_or_404(Problem, id=problem_id)
    language = request.POST.get('language', 'py')
    
    # Load the API key from your .env file
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Handle the error case where the API key is not found
        return render(request, 'submission/ai_response.html', {'error': 'API Key not configured.'})
    
    genai.configure(api_key=api_key)

    # --- 2. GET DATA FROM FORM ---
    user_code = request.POST.get('code', '')
    user_question = request.POST.get('user_question', '')
    
    # --- 3. DEFINE THE GUIDING PROMPT ---
    # This is the improved prompt we created earlier
    system_prompt = """
    You are an expert AI Coding Tutor for an Online Judge platform. Your personality is encouraging, helpful, and Socratic. Your primary goal is to guide users to the optimal solution themselves, not to give it away.

    **Your Task:**
    Analyze the user's code for a given problem and respond to their specific question. Guide them step-by-step towards the most optimal solution in terms of time and space complexity.

    **Strict Rules:**
    1. NEVER give away the final solution code. Do not write full, correct solutions. You can provide small snippets to illustrate a concept, but never the complete answer.
    2. NEVER reveal spoilers or talk about parts of the problem the user hasn't reached yet.
    3. Adhere to the user's progress. Base your guidance strictly on the code and question provided.
    4. If the user asks for the direct solution, gently refuse and reiterate your role as a tutor who helps them think.
    5. Structure your response using markdown for clarity. Use bold text for key terms and code blocks for any small examples.

    **Guidance Scenarios:**
    * If the user has written no code: Help them understand the problem. Ask clarifying questions to break it down.
    * If the user has a brute-force solution: Acknowledge their success first, then gently introduce the concept of optimization.
    * If the user's code has errors: Identify the likely logical error without fixing it directly. Ask a question that leads them to the mistake.
    * If the user has an optimal solution: Congratulate them. Only at this stage, you can show them their own code back but with best practices applied, commenting on the changes.
    """

    # --- 4. CONSTRUCT THE FINAL PROMPT FOR THE AI ---
    final_prompt = f"""
    {system_prompt}

    ---
    **Problem Statement:**
    {problem.description}

    ---
    **User's Code:**
    ```
    {user_code}
    ```

    ---
    **User's Question:**
    "{user_question}"
    """
    
    # --- 5. CALL THE API AND RENDER THE RESPONSE ---
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(final_prompt)
        ai_response = response.text
    except Exception as e:
        ai_response = f"An error occurred while communicating with the AI model: {e}"

    context = {
        'problem': problem,
        'user_code': user_code,
        'user_question': user_question,
        'ai_response': ai_response,
        'language': language,
    }

    return render(request, 'submission/ai_response.html', context)

def submission_list(request, problem_id):
    # Get the specific problem object
    problem = get_object_or_404(Problem, id=problem_id)
    
    # Filter submissions to find ones that match:
    # 1. The current logged-in user
    # 2. The specific problem
    # Order them by the most recent submission first
    submissions = CodeSubmission.objects.filter(
        user=request.user, 
        problem=problem
    ).order_by('-timestamp')
    
    context = {
        'problem': problem,
        'submissions': submissions,
    }
    
    return render(request, 'submission/submission_list.html', context)