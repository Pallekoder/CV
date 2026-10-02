FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONUNBUFFERED=1 WORLD_HOST=0.0.0.0 WORLD_STATE=/data/world.json
VOLUME ["/data"]
EXPOSE 8000
CMD ["python", "serve.py"]
