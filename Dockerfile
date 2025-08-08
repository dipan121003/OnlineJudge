# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# MODIFICATION: Add the compilers back to this image
RUN apt-get update && apt-get install -y g++ default-jdk

# Set the working directory in the container
WORKDIR /app

# Copy and install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# The command to run the development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]