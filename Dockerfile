FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir huggingface_hub
COPY . /app
RUN mkdir -p /data && chmod 777 /data
ENV PYTHONUNBUFFERED=1 WORLD_HOST=0.0.0.0 WORLD_STATE=/data/world.json PORT=8000
VOLUME ["/data"]
EXPOSE 8000
CMD ["python", "serve.py"]
