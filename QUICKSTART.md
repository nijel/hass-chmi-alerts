# Quick Start Guide

## 1. Install

Copy `custom_components/chmi_alerts` to your Home Assistant `config/custom_components/` directory and restart.

## 2. Configure

1. Go to **Settings** → **Devices & Services**
1. Click **+ Add Integration**
1. Search for "CHMI Alerts"
1. Enter:
   - **Area Filter**: Leave empty for all alerts, or enter area name (e.g., "Prague") or geocode (e.g., "2102", "CZ02102")
   - **Update Interval**: `300` (5 minutes)

## 3. Use

### View Alerts

Check the sensor: `binary_sensor.chmi_alerts_alert`

### Dashboard Card

```yaml
type: conditional
conditions:
  - entity: binary_sensor.chmi_alerts_alert
    state: 'on'
card:
  type: markdown
  content: >
    {% set alerts = state_attr('binary_sensor.chmi_alerts_alert', 'alerts') %}
    {% for alert in alerts %}
      ## {{ alert.headline }}
      {{ alert.description }}

      **Severity:** {{ alert.severity }}
      **Areas:** {{ alert.area }}
    {% endfor %}
```

### Automation

```yaml
automation:
  - alias: "Weather Alert"
    trigger:
      platform: state
      entity_id: binary_sensor.chmi_alerts_alert
      to: 'on'
    action:
      service: notify.mobile_app
      data:
        title: "Weather Alert!"
        message: >
          {{ state_attr('binary_sensor.chmi_alerts_alert', 'alerts')[0].headline }}
```

## Alert Attributes

Each alert includes:

- `headline` - Brief description
- `description` - Detailed description
- `severity` - Minor, Moderate, Severe, Extreme
- `urgency` - Immediate, Expected, Future
- `certainty` - Observed, Likely, Possible
- `event` - Event type
- `area` - Affected areas
- `effective` - Start time
- `expires` - End time
- `instruction` - What to do

## Data Source

CHMI (Czech Hydrometeorological Institute): `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
