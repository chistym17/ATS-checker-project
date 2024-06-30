# Use the official Python image as a base
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the rest of the application code
COPY . .

RUN apt-get update
RUN apt-get install poppler-utils -y
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install google
# Expose the port the app runs on
EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development 

# Run the Flask app
CMD ["flask", "run"]
