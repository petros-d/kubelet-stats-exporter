FROM python:3.9-slim

ARG UID=1000
ARG GID=1000
ARG VERSION

LABEL version=$VERSION

WORKDIR /app

COPY requirements.txt src ./

RUN pip install -r requirements.txt

RUN groupadd --system -g 1001 kubeletstats && \
    useradd --system --gid kubeletstats --no-create-home \
    --home-dir /app --shell /usr/sbin/nologin \
    --uid 1001 kubeletstats

RUN chown -R kubeletstats:kubeletstats /app

USER 1001:1001

ENV PYTHONUNBUFFERED=1

EXPOSE 9118

ENTRYPOINT ["python", "-u", "/app/main.py"]
