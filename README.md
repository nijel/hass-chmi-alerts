# CHMI Alerts for Home Assistant

[![🔌 Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nijel&repository=hass-chmi-alerts&category=integration)

A Home Assistant custom integration for fetching and displaying weather alerts from CHMI (Czech Hydrometeorological Institute).

## Features

- Fetches weather alerts from CHMI (Český hydrometeorologický ústav)
- Updates automatically every hour
- MeteoalarmCard compatible
- Supports multiple instances for different regions

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
1. Search for "CHMI Alerts" in HACS
1. Click Install
1. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/chmi_alerts` directory to your Home Assistant's `custom_components` directory
1. Restart Home Assistant

## Configuration

Add the integration through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
1. Click **Add Integration**
1. Search for "CHMI Alerts"
1. Optionally enter an **Area Filter** to receive alerts for specific regions (e.g., "Prague")
   - Leave empty to receive all alerts for the entire country
   - You can add multiple instances to monitor different regions

## Usage

The integration creates a binary sensor entity: `binary_sensor.chmi_alerts_alert`

- **State**: `on` when alerts are active, `off` when no alerts
- **Attributes**:
  - **awareness_level**: MeteoAlarm-compatible level (e.g., "3; Orange")
  - **awareness_type**: MeteoAlarm-compatible event type (e.g., "6; Low-Temperature")
  - **alerts**: List of active alerts with headline, description, severity, urgency, event type, affected areas, times, and instructions

### MeteoalarmCard Compatibility

The sensor is compatible with [MeteoalarmCard](https://github.com/MrBartusek/MeteoalarmCard):

```yaml
type: 'custom:meteoalarm-card'
integration: 'meteoalarm'
entities: 'binary_sensor.chmi_alerts_alert'
```

### Automation Example

```yaml
automation:
  - alias: "Notify on severe weather alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.chmi_alerts_alert
        to: 'on'
    condition:
      - condition: template
        value_template: >
          {% set level = state_attr('binary_sensor.chmi_alerts_alert', 'awareness_level') %}
          {{ level and (level.startswith('3;') or level.startswith('4;')) }}
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Weather Alert!"
          message: >
            {% set alerts = state_attr('binary_sensor.chmi_alerts_alert', 'alerts') %}
            {% if alerts %}{{ alerts[0].headline }}{% endif %}
```

### Lovelace Card Example

```yaml
type: conditional
conditions:
  - entity: binary_sensor.chmi_alerts_alert
    state: 'on'
card:
  type: markdown
  content: >
    ## Weather Alerts Active

    {% set alerts = state_attr('binary_sensor.chmi_alerts_alert', 'alerts') %}
    {% if alerts %}
      {% for alert in alerts %}
        **{{ alert.headline }}**

        *Severity: {{ alert.severity }}*

        {{ alert.description }}

        Areas: {{ alert.area }}

        ---
      {% endfor %}
    {% endif %}
```

## About CHMI

CHMI (Czech Hydrometeorological Institute / Český hydrometeorologický ústav) is the official meteorological service of the Czech Republic. This integration fetches weather alerts using the CAP (Common Alerting Protocol) v1.2 standard from their public feed.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Credits

- Created by [@nijel](https://github.com/nijel)
- Data provided by CHMI (Czech Hydrometeorological Institute)
