# 1. Use an official Python runtime as a parent image
FROM python:3.12-alpine

# 2. Install Ghostscript and any other system dependencies
# We add 'bash' because it's friendlier than 'sh' for Git Bash users
RUN apk add --no-cache \
    ghostscript \
    bash \
    build-base

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Set the working directory inside the container
WORKDIR /app

COPY . .

# 5. This command keeps the container alive indefinitely 
# so you can 'exec' into it anytime.
# DEV
CMD ["tail", "-f", "/dev/null"]

#PROD
# CMD ["python", "api_layer.py"]