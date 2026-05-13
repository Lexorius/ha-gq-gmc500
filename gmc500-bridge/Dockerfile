ARG BUILD_ARCH=amd64
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Python + pip aus den Alpine-Repos der HA-Basis
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app.py /app/
COPY run.sh /
RUN chmod a+x /run.sh

LABEL \
    org.opencontainers.image.title="GMC-500+ Bridge" \
    org.opencontainers.image.description="Empfängt GMC-500+ Telemetrie und veröffentlicht sie auf MQTT." \
    org.opencontainers.image.source="https://github.com/Lexorius/ha-gq-gmc500" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.authors="Thomas Kloppholz <thomas+claude@kloppholz.de>" \
    io.hass.type="addon" \
    io.hass.name="GMC-500+ Bridge" \
    io.hass.description="Empfängt GMC-500+ Telemetrie und veröffentlicht sie auf MQTT." \
    io.hass.url="https://github.com/Lexorius/ha-gq-gmc500" \
    io.hass.arch="aarch64|amd64"

CMD [ "/run.sh" ]
