# Changelog

## 2.1.0 — 2026-05-13

### Neu

- **Redirect-Modus**: Aufrufe auf unbekannte Pfade können jetzt auf eine
  konfigurierbare URL umgeleitet werden. Geräte-Telemetrie-Pfade
  (`/log2.asp`, `/gmc500`, `/log`) und `/health` bleiben unverändert.
  - Neue Option `redirect_url` (leer = aus, Default).
  - Neue Option `redirect_status` (`301`, `302`, `307` oder `308`; Default `302`).
- `/health` zeigt das aktuelle Redirect-Ziel mit an.

## 2.0.0 — 2026-05-13

### Breaking

- **Architektur**: nur noch `aarch64` und `amd64` (HA 2026.5 entfernt `armv7`, `armhf`, `i386`).
- **`build.yaml` entfernt**: Inhalte wandern in den `Dockerfile` (Supervisor 2026.04 entfernt `BUILD_FROM`-Magic).

### Neu

- `apparmor.txt` mit eigenem Profil → +1 Security-Point in HA.
- `DOCS.md` für den Add-on-Tab „Documentation".
- MQTT-Discovery: `origin`-Block (HA 2024.11+), `sw_version` und `configuration_url` im `device`-Block.
- `/health`-Endpunkt zeigt jetzt auch die Version.

### Geändert

- `paho-mqtt` auf 2.x (mit `CallbackAPIVersion.VERSION2` — paho-mqtt 1.x ist EOL).
- `gunicorn` auf >= 23.0.
- Schema-Defaults: `expected_aid` / `expected_gid` sind jetzt `str?` (optional).
- Repository- und Maintainer-Daten gesetzt.

## 1.0.0

- Erstveröffentlichung
- HTTP-Endpunkte `/log2.asp`, `/gmc500`, `/log`
- MQTT-Auto-Discovery für CPM, ACPM, µSv/h, Last-Seen
- Optionale Whitelist für AID/GID
- Automatischer MQTT-Service-Bezug vom Supervisor
