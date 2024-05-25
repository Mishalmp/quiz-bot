FROM python:3.11

ENV DockerHOME=/app/

RUN mkdir -p $DockerHOME

WORKDIR $DockerHOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt
RUN chmod +x /app/run_server.sh

# Set the entrypoint
ENTRYPOINT ["/app/run_server.sh"]