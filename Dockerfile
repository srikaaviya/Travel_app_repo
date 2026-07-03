FROM python:3.11-slim
#version available in linux, make it a slim version, not big

WORKDIR /app
#create directiry app and runs everything inside

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#now install everything inside the container

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 5000

CMD ["./entrypoint.sh"]