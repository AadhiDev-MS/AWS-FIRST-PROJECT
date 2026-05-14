# 1. Use the official lightweight Python base image
FROM python:3.13-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy only dependency file first (for Docker caching)
COPY requirements.txt .

# 4. Install system dependencies (libgomp1 is REQUIRED for XGBoost) and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. Copy the entire project into the image
COPY . .

# 6. Copy exported model artifacts to the path expected by inference.py
#    inference.py looks for the model at /app/model and feature_columns.txt at /app/model/
COPY models/production/model /app/model
COPY models/production/feature_columns.txt /app/model/feature_columns.txt

# 7. Environment configuration
#    PYTHONUNBUFFERED=1 ensures logs are shown in real-time (no buffering)
#    PYTHONPATH=/app/src lets you import modules using from serving... instead of from src.serving...
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# 8. Expose FastAPI port
EXPOSE 8000

# 9. Run the FastAPI app using uvicorn
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
