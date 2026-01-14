# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements files into the container at /usr/src/app
COPY requirements.txt requirements-dev.txt ./

# Install any needed packages specified in requirements.txt and requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy the rest of the application's code into the container
COPY . .

# Set the command to run the application
CMD ["python", "main.py"]
