# In /sandbox/Dockerfile
FROM python:3.11-slim

# Install compilers
RUN apt-get update && apt-get install -y g++ default-jdk

# Create a secure, non-root user to run the code
RUN useradd -ms /bin/bash sandboxuser
USER sandboxuser
WORKDIR /home/sandboxuser

# Copy the runner script that will execute the code
COPY runner.py .

# Set the command to run the script when the container starts
CMD ["python", "runner.py"]