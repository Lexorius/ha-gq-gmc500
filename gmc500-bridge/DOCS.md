# GMC-500+ Bridge

HTTP-Empfänger für *GQ Electronics GMC-500+* Geigerzähler. Veröffentlicht CPM, ACPM und Dosisleistung über MQTT mit Home-Assistant-Auto-Discovery — die Sensoren tauchen ohne weitere Konfiguration unter **Einstellungen → Geräte & Dienste → MQTT** auf.

## Voraussetzungen

- **Mosquitto-Broker-Add-on** installiert und gestartet
- MQTT-Integration in HA konfiguriert (passiert beim Start des Brokers normalerweise automatisch)
- GMC-500+ im gleichen Netzwerk wie der HA-Host

MQTT-Zugangsdaten **musst du nicht eintragen** — das Add-on holt sie automatisch über den HA-Supervisor (`services: mqtt:need`).

## Konfigurationsoptionen

### Option: `device_name` (default: `GMC-500+`)

Anzeigename des Geräts in Home Assistant.

### Option: `device_id` (default: `gmc500plus`)

Eindeutige ID, prägt MQTT-Topics und HA-`unique_id`. Erlaubt sind `a-z`, `0-9` und `_`.

### Option: `mqtt_base_topic` (default: `gmc500`)

Basis-Topic, unter dem State- und Availability-Topics liegen.

### Option: `expected_aid` (default: *leer*)

Whitelist für die `AID` des Geräts. Leer = alles akzeptieren.

### Option: `expected_gid` (default: *leer*)

Whitelist für die `GID` des Geräts. Leer = alles akzeptieren.

### Option: `log_level` (default: `info`)

Eines von `debug`, `info`, `warning`, `error`. `debug` zeigt jeden eingehenden Request.

## Port

Im Tab **Netzwerk** des Add-ons den externen Port wählen (Default `8088`). Genau diesen Port am Geigerzähler eintragen.

## GMC-500+ konfigurieren

Per **GQ GMC Data Viewer** (USB) unter `Settings → Other`:

| Feld              | Wert                                              |
|-------------------|---------------------------------------------------|
| Website           | IP des HA-Hosts (z. B. `192.168.1.20`)            |
| URL               | `log2.asp` *(alternativ `gmc500` oder `log`)*     |
| Port              | wie im Add-on (Default `8088`)                    |
| User ID           | beliebig numerisch, z. B. `555`                   |
| Geiger Counter ID | beliebig numerisch, z. B. `01234`                 |
| Period            | Sende-Intervall in Minuten, z. B. `1`             |

> Trägst du diese IDs in `expected_aid` / `expected_gid` ein, ignoriert das Add-on Fremd-Requests.

## Test ohne Geigerzähler

Aus dem HA-Netz heraus (z. B. SSH-Add-on):

```bash
curl "http://localhost:8088/log2.asp?AID=555&GID=01234&CPM=23&ACPM=21.5&uSV=0.115"
```

Erwartet: Antwort `OK.ERR0` und ein Log-Eintrag im Add-on.

## Erzeugte Sensoren

| Entity                          | Einheit | Beschreibung               |
|---------------------------------|---------|----------------------------|
| `sensor.gmc500plus_cpm`         | CPM     | Counts pro Minute          |
| `sensor.gmc500plus_acpm`        | CPM     | Mittelwert CPM             |
| `sensor.gmc500plus_usv`         | µSv/h   | Dosisleistung              |
| `sensor.gmc500plus_last_seen`   | –       | Zeitstempel letzte Messung |

(Die Präfixe entsprechen `device_id`.)

## Diagnose-Endpunkt

Das Add-on stellt unter `/health` einen Status-Endpunkt bereit:

```bash
curl http://<HA-IP>:8088/health
# {"mqtt_connected":true,"state_topic":"gmc500/gmc500plus/state","status":"ok","version":"2.0.0"}
```

## Troubleshooting

- **Add-on startet nicht / „Kein MQTT-Service verfügbar"** → Mosquitto-Add-on installieren und MQTT-Integration aktivieren.
- **Keine Sensoren in HA** → MQTT-Explorer öffnen, unter `homeassistant/sensor/<device_id>_*/config` prüfen, ob Discovery-Configs liegen.
- **Zähler sendet nicht** → `log_level: debug` setzen, am Gerät einen Send auslösen. IP/Port im Gerät prüfen.
- **Mehrere Geigerzähler** → das Add-on einfach mehrfach installieren ist nicht direkt möglich; stattdessen `expected_aid`/`expected_gid` zur Trennung nutzen oder mehrere Instanzen mit unterschiedlichem `device_id` betreiben.
