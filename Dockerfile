FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgles2 \
    libegl1 \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /appgit 


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

 #Start the server (Render provides the $PORT)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}