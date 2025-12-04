# Gunakan image Python 3.11 yang ringan
FROM python:3.11-slim

# Set folder kerja di dalam container
WORKDIR /app

# Copy file requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode source
COPY . .

# Expose port 8000
EXPOSE 8000

# Perintah untuk menjalankan aplikasi
CMD ["python", "main.py"]
