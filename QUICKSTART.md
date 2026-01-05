# Quick Start Guide

## 1. Install

Copy `custom_components/cap_alerts` to your Home Assistant `config/custom_components/` directory and restart.

## 2. Configure

1. Go to **Settings** → **Devices & Services**
1. Click **+ Add Integration**
1. Search for "CAP Alerts"
1. Enter:
   - **Feed URL**: `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml` (for CHMI)
   - **Area Filter**: Leave empty for all alerts, or enter area name (e.g., "Prague") or geocode (e.g., "2102", "CZ02102")
   - **Update Interval**: `300` (5 minutes)

## 3. Use

### View Alerts

Check the sensor: `sensor.cap_alerts_alert_count`

### Dashboard Card

```yaml
type: conditional
conditions:
  - entity: sensor.cap_alerts_alert_count
    state_not: "0"
card:
  type: markdown
  content: >
    {% set alerts = state_attr('sensor.cap_alerts_alert_count', 'alerts') %}
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
      platform: numeric_state
      entity_id: sensor.cap_alerts_alert_count
      above: 0
    action:
      service: notify.mobile_app
      data:
        title: "Weather Alert!"
        message: >
          {{ state_attr('sensor.cap_alerts_alert_count', 'alerts')[0].headline }}
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

## Supported Feeds

Any CAP 1.2 compliant XML feed:

- CHMI (Czech): `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
- Other meteorological services with CAP feeds
