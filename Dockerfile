FROM python:3.12-slim

WORKDIR /app

COPY chat/server.py chat/index.html chat/
COPY .cursor/skills/ryan-review .cursor/skills/ryan-review

ENV HOST=0.0.0.0 \
    PORT=8080 \
    DB_PATH=/data/ryan.db \
    MODEL=gpt-4.1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python3", "-u", "chat/server.py"]
