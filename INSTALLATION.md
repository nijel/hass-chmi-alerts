# Installation Guide for CHMI Alerts

This guide walks you through installing and configuring the CHMI Alerts integration for Home Assistant.

## Prerequisites

- Home Assistant 2023.1 or newer
- Access to your Home Assistant configuration directory

## Installation Methods

### Method 1: Manual Installation (Recommended for now)

1. **Download the integration**

   - Download or clone this repository
   - Copy the `custom_components/chmi_alerts` directory to your Home Assistant `config/custom_components/` directory

1. **Restart Home Assistant**

   - Go to **Settings** → **System** → **Restart**
   - Wait for Home Assistant to fully restart

1. **Verify installation**

   - The integration should now be available in the integrations list

### Method 2: HACS (Future)

Once this integration is added to HACS:

1. Open HACS in your Home Assistant
1. Click on "Integrations"
1. Click the three dots in the top right corner
1. Select "Custom repositories"
1. Add `https://github.com/nijel/hass-chmi-alerts` as an integration
1. Install "CHMI Alerts"
1. Restart Home Assistant

## Configuration

### Adding the Integration

1. **Navigate to Integrations**

   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**

1. **Search for CHMI Alerts**

   - Type "CHMI Alerts" in the search box
   - Click on the "CHMI Alerts" integration

1. **Configure the integration**

   - **Area Filter** (optional): Enter an area name to filter alerts

     - Examples: "Prague", "Bohemia", "Moravia"
     - Leave empty to receive all alerts
     - Filter is case-insensitive and matches partial names

   - **Update Interval**: How often to check for new alerts (in seconds)

     - Default: 300 (5 minutes)
     - Recommended: 300-600 (5-10 minutes)
     - Minimum: 60 (1 minute)

1. **Complete setup**

   - Click **Submit**
   - The integration will fetch the initial data from CHMI

### Multiple Instances

You can add multiple instances of the integration to monitor different areas:

1. **Different areas**

   - Instance 1: No filter (all alerts)
   - Instance 2: Filter: "Prague" (Prague only)
   - Instance 3: Filter: "Brno" (Brno only)

## Verification

After configuration, verify the integration is working:

1. **Check the sensor entity**

   - Go to **Developer Tools** → **States**
   - Search for `binary_sensor.chmi_alerts_alert`
   - You should see the entity with the current alert status

1. **View alert details**

   - Click on the entity to see its attributes
   - The `alerts` attribute contains details of all active alerts

1. **Check for errors**

   - Go to **Settings** → **System** → **Logs**
   - Search for "chmi_alerts"
   - There should be no errors (warnings are okay)

## Usage

### In Automations

See `examples/configuration.yaml` for automation examples.

### In Lovelace Dashboard

See `examples/lovelace_card.yaml` for dashboard card examples.

## Troubleshooting

### Integration doesn't appear in the list

- Make sure you copied the files to the correct directory
- Restart Home Assistant completely
- Clear your browser cache

### No data after configuration

- Verify the CHMI feed is accessible
- Check the Home Assistant logs for errors
- Try accessing https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml in your browser to ensure it's working

### Area filter not working

- Check the exact area names in the feed
- The filter matches partial names (case-insensitive)
- Try a broader filter first, then narrow it down

### Too many requests / Rate limiting

- Increase the update interval
- CHMI feed is typically updated every few minutes
- 5-10 minutes interval is usually sufficient

## Uninstallation

1. **Remove the integration**

   - Go to **Settings** → **Devices & Services**
   - Find "CHMI Alerts"
   - Click the three dots and select **Delete**

1. **Remove files** (optional)

   - Delete the `custom_components/chmi_alerts` directory
   - Restart Home Assistant

## Support

For issues, questions, or feature requests:

- GitHub Issues: https://github.com/nijel/hass-chmi-alerts/issues
- Discussions: https://github.com/nijel/hass-chmi-alerts/discussions
