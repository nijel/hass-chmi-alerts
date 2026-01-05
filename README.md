# CAP Alerts for Home Assistant

A Home Assistant custom integration for fetching and displaying CAP (Common Alerting Protocol) alerts.

## Features

- Fetches CAP alerts from any CAP-compliant XML feed
- Pre-configured for CHMI (Czech Hydrometeorological Institute) alerts
- Filter alerts by geographic area
- Configurable update interval
- Displays alert count and detailed information as sensor attributes
- Supports multiple alert feeds

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
1. Search for "CAP Alerts" in HACS
1. Click Install
1. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/cap_alerts` directory to your Home Assistant's `custom_components` directory
1. Restart Home Assistant

## Configuration

The integration is configured through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
1. Click **Add Integration**
1. Search for "CAP Alerts"
1. Enter the configuration:
   - **CAP Feed URL**: The URL of the CAP XML feed (default: CHMI alerts)
   - **Area Filter** (optional): Filter alerts by area name or geocode (e.g., "Prague", "2102", "CZ02102")
   - **Update Interval**: How often to check for new alerts in seconds (default: 300)

### Area Filtering

The area filter supports multiple matching modes:

- **Area names**: Filter by area description (e.g., "Prague", "Středočeský kraj")
- **Geocode values**: Filter by CISORP codes (e.g., "2102"), EMMA_ID codes (e.g., "CZ02102"), or any other geocode value
- **Partial matching**: Case-insensitive substring matching (e.g., "Bohemia" matches "Central Bohemia")

### Example Configurations

#### CHMI (Czech Republic)

- **Feed URL**: `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
- **Area Filter**: `Prague` (to see only alerts for Prague area)
- **Area Filter**: `2102` (to see only alerts for region with CISORP code 2102)
- **Area Filter**: `CZ02102` (to see only alerts for region with EMMA_ID CZ02102)

#### Multiple Instances

You can add multiple instances of the integration to monitor different feeds or areas:

- One instance for all CHMI alerts
- Another instance filtered for a specific region by name
- Another instance filtered for a specific region by geocode
- Additional instances for other CAP feed providers

## Usage

After configuration, the integration creates a sensor entity showing the count of active alerts:

- **Entity ID**: `sensor.cap_alerts_alert_count`
- **State**: Number of active alerts
- **Attributes**: Detailed information about each alert including:
  - Headline
  - Description
  - Severity (Minor, Moderate, Severe, Extreme)
  - Urgency (Immediate, Expected, Future)
  - Certainty (Observed, Likely, Possible, Unlikely)
  - Event type
  - Affected areas
  - Effective and expiration times
  - Instructions

### Automation Example

```yaml
automation:
  - alias: "Notify on severe weather alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.cap_alerts_alert_count
        above: 0
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.cap_alerts_alert_count', 'alerts')[0].severity in ['Severe', 'Extreme'] }}
    action:
      - service: notify.mobile_app
        data:
          title: "Weather Alert!"
          message: >
            {{ state_attr('sensor.cap_alerts_alert_count', 'alerts')[0].headline }}
```

### Lovelace Card Example

```yaml
type: markdown
content: >
  {% set alerts = state_attr('sensor.cap_alerts_alert_count', 'alerts') %}
  {% if alerts %}
    {% for alert in alerts %}
      **{{ alert.headline }}**

      *Severity: {{ alert.severity }}*

      {{ alert.description }}

      Areas: {{ alert.area }}

      ---
    {% endfor %}
  {% else %}
    No active alerts
  {% endif %}
```

## CAP Alert Specification

This integration supports the [Common Alerting Protocol (CAP) v1.2](http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2.html) specification, which is an international standard for emergency alerts and public warnings.

## Supported Alert Providers

While the integration is pre-configured for CHMI (Czech Hydrometeorological Institute), it can work with any CAP-compliant XML feed. Some examples:

- CHMI (Czech Republic): `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
- National Weather Service (US): Various regional feeds
- Other meteorological services providing CAP XML feeds

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
custom_components/cap_alerts/
├── __init__.py          # Integration setup
├── config_flow.py       # Configuration UI
├── const.py            # Constants
├── coordinator.py      # Data update coordinator
├── cap_parser.py       # CAP XML parser
├── sensor.py           # Sensor platform
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
