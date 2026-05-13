#!/usr/bin/with-contenv bashio
# ==============================================================================
# Startet die GMC-500+ Bridge.
# MQTT-Zugangsdaten werden automatisch vom HA-Supervisor bezogen
# (dank `services: - mqtt:need` in config.yaml).
# ==============================================================================
set -e

# --- Optionen aus der HA-Add-on-UI ----------------------------------------------
export DEVICE_NAME="$(bashio::config 'device_name')"
export DEVICE_ID="$(bashio::config 'device_id')"
export MQTT_BASE_TOPIC="$(bashio::config 'mqtt_base_topic')"
export EXPECTED_AID="$(bashio::config 'expected_aid')"
export EXPECTED_GID="$(bashio::config 'expected_gid')"
export REDIRECT_URL="$(bashio::config 'redirect_url')"
export REDIRECT_STATUS="$(bashio::config 'redirect_status')"
export LOG_LEVEL="$(bashio::config 'log_level' | tr '[:lower:]' '[:upper:]')"

# --- MQTT-Service vom Supervisor ------------------------------------------------
if bashio::services.available "mqtt"; then
    export MQTT_HOST="$(bashio::services 'mqtt' 'host')"
    export MQTT_PORT="$(bashio::services 'mqtt' 'port')"
    export MQTT_USER="$(bashio::services 'mqtt' 'username')"
    export MQTT_PASS="$(bashio::services 'mqtt' 'password')"
    bashio::log.info "MQTT-Broker: ${MQTT_HOST}:${MQTT_PORT}"
else
    bashio::log.fatal "Kein MQTT-Service verfügbar."
    bashio::log.fatal "Bitte zuerst das Mosquitto-Add-on installieren und konfigurieren."
    exit 1
fi

# --- Discovery- und Base-Topic festschreiben (HA-Standard) ----------------------
export MQTT_DISCOVERY_PREFIX="homeassistant"
export HTTP_PORT="80"

bashio::log.info "Starte GMC-500+ Bridge auf Port ${HTTP_PORT} …"
bashio::log.info "  Gerätename:  ${DEVICE_NAME}"
bashio::log.info "  Gerätekennung: ${DEVICE_ID}"
bashio::log.info "  Base-Topic:  ${MQTT_BASE_TOPIC}"
if [[ -n "${EXPECTED_AID}" || -n "${EXPECTED_GID}" ]]; then
    bashio::log.info "  Whitelist:   AID=${EXPECTED_AID:-*} GID=${EXPECTED_GID:-*}"
fi
if [[ -n "${REDIRECT_URL}" ]]; then
    bashio::log.info "  Redirect:    unbekannte Pfade -> ${REDIRECT_URL} (HTTP ${REDIRECT_STATUS})"
fi

cd /app
exec gunicorn \
    --bind "0.0.0.0:${HTTP_PORT}" \
    --workers 1 \
    --threads 4 \
    --access-logfile - \
    app:app
