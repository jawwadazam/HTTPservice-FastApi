FROM python:buster

# Define environment variable
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
    gettext \
    python3-pip \
     && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U wheel setuptools pip
RUN pip3 install pip-tools

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .
# Install Python dependencies
RUN pip3 install pipenv
RUN pipenv install --system --skip-lock
# --deploy --dev
EXPOSE 8000/tcp

# ENTRYPOINT [ "/bin/bash" ]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]