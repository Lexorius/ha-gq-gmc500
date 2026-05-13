# GMC-500+ Bridge

HTTP-Empfänger für *GQ Electronics GMC-500+* Geigerzähler.
Veröffentlicht CPM, ACPM und Dosisleistung über MQTT mit Home-Assistant-Auto-Discovery – die Sensoren tauchen ohne weitere Konfiguration unter **Einstellungen → Geräte & Dienste → MQTT** auf.

> Diese Datei ist die GitHub-Übersicht. Die ausführliche Anleitung, die HA im Add-on-Tab **Documentation** anzeigt, findest du in [DOCS.md](DOCS.md).

## Voraussetzungen

- **Home Assistant 2026.5+** (Supervisor 2026.04+)
- **Mosquitto-Broker-Add-on** installiert und gestartet
- MQTT-Integration in HA konfiguriert (passiert beim Start des Brokers normalerweise automatisch)
- GMC-500+ im gleichen Netzwerk wie der HA-Host

## Konfiguration

| Option            | Default        | Bedeutung                                              |
|-------------------|----------------|--------------------------------------------------------|
| `device_name`     | `GMC-500+`     | Anzeigename in HA                                      |
| `device_id`       | `gmc500plus`   | Eindeutige ID, prägt Topics & `unique_id` (a-z,0-9,_)  |
| `mqtt_base_topic` | `gmc500`       | Basis-Topic für State/Availability                     |
| `expected_aid`    | *(leer)*       | Whitelist für `AID`. Leer = alles akzeptieren          |
| `expected_gid`    | *(leer)*       | Whitelist für `GID`. Leer = alles akzeptieren          |
| `log_level`       | `info`         | `debug` zeigt jeden eingehenden Request                |

MQTT-Zugangsdaten **musst du nicht eintragen** – das Add-on holt sie automatisch über den HA-Supervisor.

## Port

Der externe Port wird in der HA-UI im Tab **Netzwerk** des Add-ons eingestellt. Default ist `80`, weil viele GMC-Geräte keine alternativen Ports unterstützen. Falls dein Gerät einen freien Port erlaubt, kannst du hier umstellen.

## GMC-500+ konfigurieren

Per **GQ GMC Data Viewer** (USB) unter `Settings → Other`:

| Feld                | Wert                                                  |
|---------------------|-------------------------------------------------------|
| Website             | IP des HA-Hosts (z. B. `192.168.1.20`)                |
| URL                 | `log2.asp` *(alternativ `gmc500` oder `log`)*         |
| Port                | wie im Add-on (Default `80`)                          |
| User ID             | beliebig numerisch, z. B. `555`                       |
| Geiger Counter ID   | beliebig numerisch, z. B. `01234`                     |
| Period              | Sende-Intervall in Minuten, z. B. `1`                 |

> Trägst du diese IDs in `expected_aid` / `expected_gid` ein, ignoriert das Add-on Fremd-Requests.

## Test ohne Geigerzähler

Aus dem HA-Netz heraus (z. B. SSH-Add-on):

```bash
curl "http://localhost/log2.asp?AID=555&GID=01234&CPM=23&ACPM=21.5&uSV=0.115"
```

Erwartet: Antwort `OK.ERR0` und ein Log-Eintrag im Add-on.

## Erzeugte Sensoren

| Entity                              | Einheit | Beschreibung               |
|-------------------------------------|---------|----------------------------|
| `sensor.gmc500plus_cpm`             | CPM     | Counts pro Minute          |
| `sensor.gmc500plus_acpm`            | CPM     | Mittelwert CPM             |
| `sensor.gmc500plus_usv`             | µSv/h   | Dosisleistung              |
| `sensor.gmc500plus_last_seen`       | –       | Zeitstempel letzte Messung |

(Die Präfixe entsprechen `device_id`.)

## Troubleshooting

- **Add-on startet nicht / „Kein MQTT-Service verfügbar"** → Mosquitto-Add-on installieren und MQTT-Integration aktivieren.
- **Keine Sensoren in HA** → MQTT-Explorer öffnen, unter `homeassistant/sensor/<device_id>_*/config` prüfen, ob Discovery-Configs liegen.
- **Zähler sendet nicht** → `log_level: debug` setzen, am Gerät einen Send auslösen. IP/Port im Gerät prüfen.
- **Mehrere Geigerzähler** → das Add-on einfach mehrfach installieren ist nicht direkt möglich; stattdessen `expected_aid/gid` zur Trennung nutzen oder den State im `app.py` pro Gerät unterscheiden.
