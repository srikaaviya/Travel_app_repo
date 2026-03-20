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

CMD ["python", "app.py"]
#When the container starts, run this command.
#Exactly like typing python app.py in your terminal