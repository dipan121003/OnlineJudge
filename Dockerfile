# Useing an official Python runtime as a parent image
FROM python:3.11-slim

# Setting environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Adding the Docker CLI to this image so it can run 'docker' commands
RUN apt-get update && apt-get install -y ca-certificates curl
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install -y docker-ce-cli

# Set the working directory in the container
WORKDIR /app

# Copy and install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# The command to run the development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]