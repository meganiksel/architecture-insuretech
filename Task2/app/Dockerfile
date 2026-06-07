FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.3 prometheus_client==0.20.0
COPY app.py /app/app.py
EXPOSE 8080
CMD ["python", "/app/app.py"]
