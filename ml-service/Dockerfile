FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn
COPY app ./app
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
