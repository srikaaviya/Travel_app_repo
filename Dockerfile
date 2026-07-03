FROM python:3.11-slim
#version available in linux, make it a slim version, not big

WORKDIR /app
#create directiry app and runs everything inside

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#now install everything inside the container

COPY . .
#copy rest of project files

EXPOSE 5000
#container will listen on port 5000

CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
#Uses Railway's PORT env var, falls back to 5000 for local Docker.