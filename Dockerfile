# Use an official lightweight Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy dependency file and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and templates
COPY src ./src
COPY templates ./templates
COPY sample_data/sessions.json ./sample_data/sessions.json

# Default command
CMD ["python", "-m", "src.main", "--input", "sample_data/sessions.json", "--out-dir", "out", "--html", "--sqlite-db", "results.db"]