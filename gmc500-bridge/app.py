#!/usr/bin/env python3
"""
GMC500+ Bridge für Home Assistant.

Empfängt HTTP-GET-Requests eines GQ Electronics GMC-500+ Geigerzählers
(Standard-URL des Geräts: /log2.asp?AID=...&GID=...&CPM=...&ACPM=...&uSV=...)
und veröffentlicht die Werte via MQTT mit Home-Assistant-Auto-Discovery.
"""

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request

__version__ = "2.0.0"

# ---------- Konfiguration aus Environment ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
HTTP_PORT = int(os.getenv("HTTP_PORT", "80"))

MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASS = os.getenv("MQTT_PASS", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "gmc500_bridge")
MQTT_DISCOVERY_PREFIX = os.getenv("MQTT_DISCOVERY_PREFIX", "homeassistant")
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", "gmc500")

EXPECTED_AID = os.getenv("EXPECTED_AID", "").strip()
EXPECTED_GID = os.getenv("EXPECTED_GID", "").strip()

DEVICE_NAME = os.getenv("DEVICE_NAME", "GMC-500+")
DEVICE_ID = os.getenv("DEVICE_ID", "gmc500plus")

PROJECT_URL = "https://github.com/Lexorius/ha-gq-gmc500"

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("gmc500")

# ---------- MQTT ----------
# paho-mqtt 2.x verlangt eine explizite CallbackAPIVersion.
mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=MQTT_CLIENT_ID,
    clean_session=True,
)
if MQTT_USER:
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

AVAILABILITY_TOPIC = f"{MQTT_BASE_TOPIC}/{DEVICE_ID}/availability"
STATE_TOPIC = f"{MQTT_BASE_TOPIC}/{DEVICE_ID}/state"

DEVICE_INFO = {
    "identifiers": [DEVICE_ID],
    "name": DEVICE_NAME,
    "manufacturer": "GQ Electronics",
    "model": "GMC-500+",
    "sw_version": __version__,
    "configuration_url": PROJECT_URL,
}

ORIGIN_INFO = {
    "name": "GMC-500+ Bridge",
    "sw_version": __version__,
    "support_url": PROJECT_URL,
}


def publish_discovery() -> None:
    """Veröffentlicht MQTT-Discovery-Konfigurationen für Home Assistant."""
    sensors = [
        {"name": "CPM", "key": "cpm", "unit": "CPM",
         "icon": "mdi:radioactive", "state_class": "measurement"},
        {"name": "ACPM", "key": "acpm", "unit": "CPM",
         "icon": "mdi:radioactive", "state_class": "measurement"},
        {"name": "Dosisleistung", "key": "usv", "unit": "µSv/h",
         "icon": "mdi:radioactive", "state_class": "measurement"},
        {"name": "Letzte Messung", "key": "last_seen",
         "device_class": "timestamp", "icon": "mdi:clock-outline"},
    ]

    for s in sensors:
        unique = f"{DEVICE_ID}_{s['key']}"
        cfg_topic = f"{MQTT_DISCOVERY_PREFIX}/sensor/{unique}/config"
        cfg = {
            "name": s["name"],
            "unique_id": unique,
            "object_id": unique,
            "state_topic": STATE_TOPIC,
            "availability_topic": AVAILABILITY_TOPIC,
            "value_template": f"{{{{ value_json.{s['key']} }}}}",
            "device": DEVICE_INFO,
            "origin": ORIGIN_INFO,
        }
        for k in ("unit", "state_class", "device_class", "icon"):
            if k in s:
                target = "unit_of_measurement" if k == "unit" else k
                cfg[target] = s[k]
        mqtt_client.publish(cfg_topic, json.dumps(cfg), retain=True)
        log.debug("Discovery: %s", cfg_topic)

    log.info("HA-Discovery veröffentlicht (%d Sensoren)", len(sensors))


def _on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        log.info("MQTT verbunden mit %s:%s", MQTT_HOST, MQTT_PORT)
        client.publish(AVAILABILITY_TOPIC, "online", retain=True)
        publish_discovery()
    else:
        log.error("MQTT-Verbindung fehlgeschlagen: %s", reason_code)


def _on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    log.warning("MQTT getrennt (%s) – paho versucht reconnect", reason_code)


mqtt_client.on_connect = _on_connect
mqtt_client.on_disconnect = _on_disconnect
mqtt_client.will_set(AVAILABILITY_TOPIC, "offline", retain=True)


def start_mqtt() -> None:
    """Verbindet zum Broker und startet den Netzwerk-Loop im Hintergrund."""
    def _connect_forever():
        while True:
            try:
                mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
                mqtt_client.loop_start()
                return
            except Exception as e:  # noqa: BLE001
                log.error("MQTT-Connect fehlgeschlagen: %s – retry in 5s", e)
                time.sleep(5)

    threading.Thread(target=_connect_forever, daemon=True).start()


# ---------- HTTP-Server ----------
app = Flask(__name__)


def _handle_gmc_request():
    """Verarbeitet log2.asp-Requests vom Geigerzähler."""
    args = request.args
    aid = args.get("AID", "")
    gid = args.get("GID", "")

    log.debug("Eingang von %s: %s", request.remote_addr, dict(args))

    if EXPECTED_AID and aid != EXPECTED_AID:
        log.warning("AID %r nicht erlaubt", aid)
        return "ERR1", 403
    if EXPECTED_GID and gid != EXPECTED_GID:
        log.warning("GID %r nicht erlaubt", gid)
        return "ERR1", 403

    try:
        cpm = float(args.get("CPM"))
        acpm = float(args.get("ACPM", cpm))
        usv = float(args.get("uSV"))
    except (TypeError, ValueError):
        log.warning("Ungültige Messwerte: %s", dict(args))
        return "ERR2", 400

    payload = {
        "aid": aid,
        "gid": gid,
        "cpm": cpm,
        "acpm": acpm,
        "usv": usv,
        "last_seen": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    mqtt_client.publish(STATE_TOPIC, json.dumps(payload), retain=True)
    log.info("CPM=%.1f  ACPM=%.1f  µSv/h=%.4f", cpm, acpm, usv)

    return "OK.ERR0"


@app.route("/log2.asp", methods=["GET"])
@app.route("/gmc500", methods=["GET"])
@app.route("/log", methods=["GET"])
def log_route():
    return _handle_gmc_request()


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        status="ok",
        version=__version__,
        mqtt_connected=mqtt_client.is_connected(),
        state_topic=STATE_TOPIC,
    )


start_mqtt()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT)
