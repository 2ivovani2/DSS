FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py db.py model_whitelist.py sample_bulk_weapons.json ./
ENV PYTHONUNBUFFERED=1
CMD ['python', '/app/main.py', '--help']
