# Use the official Python base image with version 3.9
FROM python:3.11.5-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose port 5000 for the Flask app to run on
EXPOSE 5000

# Set the environment variable for the Flask app
ENV FLASK_APP=app.py

# Run the Flask app using gunicorn as the server
CMD ["gunicorn", "--chdir", "/app", "-b", "0.0.0.0:5000", "main:app"]
