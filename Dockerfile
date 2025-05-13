FROM python:3.11-slim
ENV PYTHONPATH=/app


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium chromium-driver curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Устанавливаем часовой пояс
ENV TZ=Europe/Kyiv


ENV PATH="/usr/lib/chromium:$PATH"


CMD ["python", "-m", "app.scheduler"]
