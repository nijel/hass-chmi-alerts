# CHMI Alerts for Home Assistant

[![🔌 Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nijel&repository=hass-chmi-alerts&category=integration)

A Home Assistant custom integration for fetching and displaying weather alerts from CHMI (Czech Hydrometeorological Institute).

## Features

- Fetches weather alerts from CHMI (Český hydrometeorologický ústav)
- Filter alerts by geographic area
- Configurable update interval
- Displays alert count and detailed information as sensor attributes
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

The integration is configured through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
1. Click **Add Integration**
1. Search for "CHMI Alerts"
1. Enter the configuration:
   - **Area Filter** (optional): Filter alerts by area name or geocode (e.g., "Prague", "2102", "CZ02102")
   - **Update Interval**: How often to check for new alerts in seconds (default: 300)

### Area Filtering

The area filter supports multiple matching modes:

- **Area names**: Filter by area description (e.g., "Prague", "Středočeský kraj")
- **Geocode values**: Filter by CISORP codes (e.g., "2102"), EMMA_ID codes (e.g., "CZ02102"), or any other geocode value
- **Partial matching**: Case-insensitive substring matching (e.g., "Bohemia" matches "Central Bohemia")

### Example Configurations

#### All Czech Republic

- **Area Filter**: Leave empty to receive all alerts for the entire country

#### Specific Region

- **Area Filter**: `Prague` (to see only alerts for Prague area)
- **Area Filter**: `2102` (to see only alerts for region with CISORP code 2102)
- **Area Filter**: `CZ02102` (to see only alerts for region with EMMA_ID CZ02102)

#### Multiple Instances

You can add multiple instances of the integration to monitor different regions:

- One instance for all CHMI alerts (no filter)
- Another instance filtered for Prague by name
- Another instance filtered for a specific region by geocode

## Usage

After configuration, the integration creates a binary sensor entity showing alert status with MeteoalarmCard compatibility:

- **Entity ID**: `binary_sensor.chmi_alerts_alert`
- **State**: `on` when alerts are active, `off` when no alerts
- **Attributes**: Detailed information including:
  - **awareness_level**: MeteoAlarm-compatible level (e.g., "3; Orange")
  - **awareness_type**: MeteoAlarm-compatible event type (e.g., "6; Low-Temperature")
  - **attribution**: Always set to "Information provided by MeteoAlarm"
  - **alerts**: Detailed list of all active alerts with:
    - Headline
    - Description
    - Severity (Minor, Moderate, Severe, Extreme)
    - Urgency (Immediate, Expected, Future)
    - Certainty (Observed, Likely, Possible, Unlikely)
    - Event type
    - Affected areas
    - Effective and expiration times
    - Instructions

### MeteoalarmCard Compatibility

The binary sensor provides meteoalarm-compatible attributes, making it compatible with [MeteoalarmCard](https://github.com/MrBartusek/MeteoalarmCard):

- **Binary Sensor State**: On when alerts are active, Off when no alerts

- **Alert Severity Levels** (mapped from CAP severity):

  - 🟢 Green: No alerts
  - 🟡 Yellow: Minor severity alerts
  - 🟠 Orange: Moderate/Severe alerts
  - 🔴 Red: Extreme alerts

The sensor icon automatically changes based on the current awareness level.

#### Using with MeteoalarmCard

To use this integration with [MeteoalarmCard](https://github.com/MrBartusek/MeteoalarmCard), configure it as follows:

```yaml
type: 'custom:meteoalarm-card'
integration: 'meteoalarm'
entities: 'binary_sensor.chmi_alerts_alert'
```

The binary sensor uses the native meteoalarm format with `awareness_level` and `awareness_type` attributes directly from CAP XML parameters, ensuring full compatibility with MeteoalarmCard without requiring any format conversions.

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
          {# Check for severe alerts (Orange or Red) #}
          {% set level = state_attr('binary_sensor.chmi_alerts_alert', 'awareness_level') %}
          {{ level and (level.startswith('3;') or level.startswith('4;')) }}
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Weather Alert!"
          message: >
            {% set alerts = state_attr('binary_sensor.chmi_alerts_alert', 'alerts') %}
            {% if alerts %}{{ alerts[0].headline }}{% endif %}

  - alias: "Notify on any new alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.chmi_alerts_alert
        to: 'on'
    action:
      - service: notify.mobile_app
        data:
          title: "Weather Alert!"
          message: >
            {% set alerts = state_attr('binary_sensor.chmi_alerts_alert', 'alerts') %}
            {% if alerts %}{{ alerts[0].headline }}{% endif %}
```

### Lovelace Card Example

```yaml
# Card with alert display
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

# Simple entity card showing current status
type: entity
entity: binary_sensor.chmi_alerts_alert
name: Weather Alert Status
```

## About CHMI

CHMI (Czech Hydrometeorological Institute / Český hydrometeorologický ústav) is the official meteorological service of the Czech Republic. This integration fetches weather alerts using the CAP (Common Alerting Protocol) v1.2 standard from their public feed.

Feed URL: `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
custom_components/chmi_alerts/
├── __init__.py          # Integration setup
├── config_flow.py       # Configuration UI
├── const.py            # Constants
├── coordinator.py      # Data update coordinator
├── cap_parser.py       # CAP XML parser
├── binary_sensor.py    # Binary sensor platform
├── manifest.json       # Integration manifest
└── translations/       # UI translations
    ├── en.json
    └── cs.json
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Credits

- Created by [@nijel](https://github.com/nijel)
- CAP specification by OASIS Emergency Management Technical Committee
- Data provided by CHMI (Czech Hydrometeorological Institute)
