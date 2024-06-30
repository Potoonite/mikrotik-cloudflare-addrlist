# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y iproute2 curl && apt-get clean

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./requirements.txt .
COPY ./update_mikrotik_cloudflareips.py .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# Run update_mikrotik.py when the container launches
CMD ["python", "-u", "./update_mikrotik_cloudflareips.py"]
