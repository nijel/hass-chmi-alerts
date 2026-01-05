# Installation Guide for CAP Alerts

This guide walks you through installing and configuring the CAP Alerts integration for Home Assistant.

## Prerequisites

- Home Assistant 2023.1 or newer
- Access to your Home Assistant configuration directory

## Installation Methods

### Method 1: Manual Installation (Recommended for now)

1. **Download the integration**
   - Download or clone this repository
   - Copy the `custom_components/cap_alerts` directory to your Home Assistant `config/custom_components/` directory

2. **Restart Home Assistant**
   - Go to **Settings** → **System** → **Restart**
   - Wait for Home Assistant to fully restart

3. **Verify installation**
   - The integration should now be available in the integrations list

### Method 2: HACS (Future)

Once this integration is added to HACS:

1. Open HACS in your Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/nijel/hass-cap-alerts` as an integration
6. Install "CAP Alerts"
7. Restart Home Assistant

## Configuration

### Adding the Integration

1. **Navigate to Integrations**
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**

2. **Search for CAP Alerts**
   - Type "CAP Alerts" in the search box
   - Click on the "CAP Alerts" integration

3. **Configure the integration**
   - **CAP Feed URL**: Enter the URL of your CAP XML feed
     - For CHMI (Czech Republic): `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
     - For other providers: Enter their CAP feed URL
   
   - **Area Filter** (optional): Enter an area name to filter alerts
     - Examples: "Prague", "Bohemia", "Moravia"
     - Leave empty to receive all alerts
     - Filter is case-insensitive and matches partial names
   
   - **Update Interval**: How often to check for new alerts (in seconds)
     - Default: 300 (5 minutes)
     - Recommended: 300-600 (5-10 minutes)
     - Minimum: 60 (1 minute)

4. **Complete setup**
   - Click **Submit**
   - The integration will fetch the initial data

### Multiple Instances

You can add multiple instances of the integration to monitor different feeds or areas:

1. **Different areas from the same feed**
   - Instance 1: CHMI feed, no filter (all alerts)
   - Instance 2: CHMI feed, filter: "Prague" (Prague only)
   - Instance 3: CHMI feed, filter: "Brno" (Brno only)

2. **Different feeds**
   - Instance 1: CHMI (Czech Republic)
   - Instance 2: Another CAP provider
   - Instance 3: Regional CAP feed

## Verification

After configuration, verify the integration is working:

1. **Check the sensor entity**
   - Go to **Developer Tools** → **States**
   - Search for `sensor.cap_alerts_alert_count`
   - You should see the entity with the current alert count

2. **View alert details**
   - Click on the entity to see its attributes
   - The `alerts` attribute contains details of all active alerts

3. **Check for errors**
   - Go to **Settings** → **System** → **Logs**
   - Search for "cap_alerts"
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

- Verify the feed URL is accessible
- Check the Home Assistant logs for errors
- Try accessing the feed URL in your browser to ensure it's working

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
   - Find "CAP Alerts"
   - Click the three dots and select **Delete**

2. **Remove files** (optional)
   - Delete the `custom_components/cap_alerts` directory
   - Restart Home Assistant

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/nijel/hass-cap-alerts/issues
- Discussions: https://github.com/nijel/hass-cap-alerts/discussions
