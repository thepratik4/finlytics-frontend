FROM python:3.10-bullseye

# Set working directory
WORKDIR /app

# Copy your whole project
COPY . .

# Copy the system requirements list
COPY all_requirements.txt .

# Install the exact same packages your system has
RUN pip install --no-cache-dir -r all_requirements.txt

# Expose app port if needed
EXPOSE 5000

# Run your flask app
CMD ["python", "app.py"]
