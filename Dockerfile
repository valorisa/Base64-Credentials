FROM python:3.13-slim

LABEL maintainer="valorisa" \
      description="Gestionnaire de credentials Base64/Fernet"

WORKDIR /app

COPY credentials_manager.py .
COPY requirements.txt .

RUN pip install --no-cache-dir cryptography argcomplete

ENTRYPOINT ["python", "credentials_manager.py"]
CMD ["--help"]
