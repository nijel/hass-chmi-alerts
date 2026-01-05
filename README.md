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
2. Search for "CAP Alerts" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/cap_alerts` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

The integration is configured through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "CAP Alerts"
4. Enter the configuration:
   - **CAP Feed URL**: The URL of the CAP XML feed (default: CHMI alerts)
   - **Area Filter** (optional): Filter alerts by area name (e.g., "Prague", "Bohemia")
   - **Update Interval**: How often to check for new alerts in seconds (default: 300)

### Example Configurations

#### CHMI (Czech Republic)
- **Feed URL**: `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
- **Area Filter**: `Prague` (to see only alerts for Prague area)

#### Multiple Instances

You can add multiple instances of the integration to monitor different feeds or areas:
- One instance for all CHMI alerts
- Another instance filtered for a specific region
- Additional instances for other CAP feed providers

## Usage

After configuration, the integration creates a sensor entity showing alert status with meteoalarm compatibility:

- **Entity ID**: `sensor.cap_alerts_alert`
- **State**: `off` when no alerts, or awareness level (`yellow`, `orange`, `red`) when alerts are active - compatible with meteoalarm
- **Attributes**: Detailed information including:
  - **awareness_level**: Highest alert level in MeteoalarmCard format ("2; Yellow", "3; Orange", "4; Red")
  - **awareness_type**: Event type in MeteoalarmCard format ("1; Wind", "10; Rain", etc.)
  - **alert_count**: Number of active alerts
  - **alerts**: List of all active alerts with:
    - Headline
    - Description
    - Severity (Minor, Moderate, Severe, Extreme)
    - Urgency (Immediate, Expected, Future)
    - Certainty (Observed, Likely, Possible, Unlikely)
    - Event type
    - Affected areas
    - Effective and expiration times
    - Instructions

### Meteoalarm Compatibility

The sensor provides meteoalarm-compatible attributes, making it easy to use with cards and automations designed for the built-in meteoalarm integration and custom cards like [MeteoalarmCard](https://github.com/MrBartusek/MeteoalarmCard):

- **Awareness Levels**:
  - 🟢 Green: No alerts
  - 🟡 Yellow: Minor severity alerts
  - 🟠 Orange: Moderate/Severe alerts
  - 🔴 Red: Extreme alerts

- **Format**: Attributes use MeteoalarmCard-compatible format:
  - `awareness_level`: "2; Yellow", "3; Orange", "4; Red"
  - `awareness_type`: "1; Wind", "10; Rain", etc.

The sensor icon automatically changes based on the current awareness level.

#### Using with MeteoalarmCard

To use this integration with [MeteoalarmCard](https://github.com/MrBartusek/MeteoalarmCard), configure it as follows:

```yaml
type: 'custom:meteoalarm-card'
integration: 'meteoalarm'
entities: 'sensor.cap_alerts_alert'
```

The card will automatically detect and display your CAP alerts with the appropriate colors and icons.

### Automation Example

```yaml
automation:
  - alias: "Notify on severe weather alert"
    trigger:
      - platform: state
        entity_id: sensor.cap_alerts_alert
        to:
          - orange
          - red
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Weather Alert!"
          message: >
            {{ state_attr('sensor.cap_alerts_alert', 'awareness_type') }}
            - Level: {{ states('sensor.cap_alerts_alert') }}
            
  - alias: "Notify on any new alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.cap_alerts_alert
        attribute: alert_count
        above: 0
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.cap_alerts_alert', 'alerts')[0].severity in ['Severe', 'Extreme'] }}
    action:
      - service: notify.mobile_app
        data:
          title: "Weather Alert!"
          message: >
            {{ state_attr('sensor.cap_alerts_alert', 'alerts')[0].headline }}
```

### Lovelace Card Example

```yaml
# Card with awareness level display
type: conditional
conditions:
  - entity: sensor.cap_alerts_alert
    state_not: "off"
card:
  type: markdown
  content: >
    ## Weather Alerts - {{ states('sensor.cap_alerts_alert') | upper }}
    
    **Type:** {{ state_attr('sensor.cap_alerts_alert', 'awareness_type') }}
    
    **Active Alerts:** {{ state_attr('sensor.cap_alerts_alert', 'alert_count') }}
    
    ---
    
    {% set alerts = state_attr('sensor.cap_alerts_alert', 'alerts') %}
    {% if alerts %}
      {% for alert in alerts %}
        **{{ alert.headline }}**
        
        *Severity: {{ alert.severity }} | Level: {{ alert.awareness_level }}*
        
        {{ alert.description }}
        
        Areas: {{ alert.area }}
        
        ---
      {% endfor %}
    {% endif %}

# Simple entity card showing current status
type: entity
entity: sensor.cap_alerts_alert
name: Weather Alert Status
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
