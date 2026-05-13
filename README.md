# GMC-500+ Home Assistant Add-on

Home-Assistant-Add-on, das HTTP-Telemetrie eines *GQ Electronics GMC-500+*
Geigerzählers empfängt und via MQTT-Auto-Discovery an Home Assistant weiterleitet.

> **Wichtig:** Funktioniert nur unter **Home Assistant OS** oder **Home Assistant Supervised** (überall, wo der Supervisor läuft). In reinen *HA Container*-Installationen gibt es keine Add-ons – dort die separate Docker-Compose-Variante nutzen.
>
> **Mindestversion:** Home Assistant **2026.5** (Supervisor 2026.04+) — ältere Supervisor-Versionen benötigen die alte BUILD_FROM-Magie, die hier nicht mehr verwendet wird.

## Unterstützte Architekturen

- `aarch64` (Raspberry Pi 4/5, ODROID-N2, generic ARM64)
- `amd64` (Intel/AMD-NUC, generic x86_64)

`armv7`, `armhf` und `i386` werden vom Home-Assistant-Add-on-Framework seit 2026.5 nicht mehr unterstützt.

## Installation

### Variante A — als Add-on-Repository (empfohlen)

1. In HA: **Einstellungen → Add-ons → Add-on Store → ⋮ → Repositories**.
2. URL eintragen: `https://github.com/Lexorius/ha-gq-gmc500` → *Add*.
3. Im Store erscheint *GMC-500+ Bridge* → **Installieren**.
4. Tab **Konfiguration**: Werte anpassen (oder Defaults lassen).
5. Tab **Netzwerk**: externen Port wählen (Default `8088`).
6. **Start**, dann den Geigerzähler auf `http://<HA-IP>:8088/log2.asp` und den gewählten Port konfigurieren.

### Variante B — lokal ohne GitHub

1. Per Samba- oder SSH-Add-on auf den HA-Host verbinden.
2. Ordner `gmc500-bridge/` (also den **inneren** Ordner) nach `/addons/` kopieren.
   - Endstruktur: `/addons/gmc500-bridge/config.yaml`, `/addons/gmc500-bridge/app.py` usw.
3. In HA: **Einstellungen → Add-ons → Add-on Store** → oben rechts **⋮ → Repositories prüfen / neu laden** (oder Browser-Refresh).
4. Unter **„Lokale Add-ons"** erscheint *GMC-500+ Bridge* → **Installieren**.
5. Weiter wie ab Schritt 4 in Variante A.

## Geräte-Setup

Siehe [`gmc500-bridge/DOCS.md`](gmc500-bridge/DOCS.md).

## Lizenz

MIT.
