# CAP Alerts Integration - Implementation Summary

## Overview

This repository contains a complete Home Assistant custom integration for fetching and displaying CAP (Common Alerting Protocol) alerts. The integration is designed to be generic and work with any CAP 1.2 compliant XML feed, with pre-configured support for CHMI (Czech Hydrometeorological Institute).

## What is CAP?

CAP (Common Alerting Protocol) is an international standard (OASIS) for public warning and emergency alerts. It allows meteorological services, civil defense agencies, and other organizations to distribute alerts in a standardized XML format.

## Implementation Details

### Core Components

1. **CAP Parser (`cap_parser.py`)**

   - Parses CAP 1.2 XML format
   - Supports both direct CAP XML and Atom feeds containing CAP alerts
   - Extracts all standard CAP fields (severity, urgency, certainty, etc.)
   - Parses geocode values (CISORP, EMMA_ID, etc.) from area sections
   - Handles multiple info sections and areas per alert
   - Case-insensitive area and geocode filtering

1. **Data Coordinator (`coordinator.py`)**

   - Fetches CAP feeds asynchronously using aiohttp
   - Configurable update intervals (default: 5 minutes)
   - Proper error handling and timeout management
   - Filters alerts based on user-defined area or geocode filter

1. **Sensor Platform (`sensor.py`)**

   - Creates a sensor showing the count of active alerts
   - Stores all alert details in sensor attributes
   - Each alert includes: headline, description, severity, urgency, certainty, event, areas, times, instructions

1. **Config Flow (`config_flow.py`)**

   - UI-based configuration (no YAML editing required)
   - Validates feed URLs
   - Prevents duplicate configurations
   - User-friendly setup wizard

1. **Integration Setup (`__init__.py`)**

   - Handles integration lifecycle
   - Sets up coordinator and platforms
   - Proper cleanup on unload

### Features

✅ **Generic CAP Support**: Works with any CAP 1.2 compliant feed
✅ **Area Filtering**: Filter alerts by geographic area description or geocode values (CISORP, EMMA_ID, etc.)
✅ **Configurable Updates**: Set your own update interval
✅ **Rich Alert Data**: Access all CAP fields through sensor attributes
✅ **Multilingual**: English and Czech translations included
✅ **HACS Ready**: Prepared for HACS distribution
✅ **Well Tested**: Unit tests for parser functionality
✅ **Documented**: Comprehensive documentation and examples

### File Structure

```
custom_components/cap_alerts/
├── __init__.py          # Integration setup and lifecycle
├── cap_parser.py        # CAP XML parser
├── config_flow.py       # UI configuration flow
├── const.py            # Constants and configuration keys
├── coordinator.py      # Data update coordinator
├── manifest.json       # Integration metadata
├── sensor.py           # Sensor platform
├── strings.json        # Base translations
└── translations/       # Localized translations
    ├── en.json         # English
    └── cs.json         # Czech
```

### Alert Information Available

Each CAP alert provides:

- **identifier**: Unique alert ID
- **sender**: Who issued the alert
- **headline**: Brief summary
- **description**: Detailed description
- **severity**: Minor, Moderate, Severe, Extreme
- **urgency**: Immediate, Expected, Future, Past
- **certainty**: Observed, Likely, Possible, Unlikely
- **event**: Type of event (e.g., "Severe Weather")
- **category**: Met, Geo, Safety, Security, etc.
- **area**: Affected geographic areas
- **effective**: When alert becomes effective
- **expires**: When alert expires
- **instruction**: What people should do
- **response_type**: Expected response (Shelter, Evacuate, etc.)

## Usage Scenarios

### 1. CHMI (Czech Republic)

Monitor weather alerts from the Czech Hydrometeorological Institute:

- **Feed URL**: `https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml`
- **Examples**: Storm warnings, flood alerts, extreme heat warnings

### 2. Multiple Regions

Set up multiple instances to monitor different regions:

- One for Prague only
- One for Central Bohemia
- One for all of Czech Republic

### 3. Other CAP Feeds

The integration works with any CAP 1.2 compliant feed:

- National weather services
- Emergency management agencies
- Tsunami warning centers
- Any service providing CAP XML

## Integration with Home Assistant

### Automations

Create automations to:

- Send notifications when severe alerts are issued
- Turn on lights when alerts are active
- Announce alerts over speakers
- Adjust climate control based on weather alerts

### Dashboards

Display alerts using:

- Conditional cards (show only when alerts are active)
- Markdown cards with formatted alert details
- Entity cards showing alert count
- Custom cards with severity-based styling

### Scripts

Use alert data in:

- Notification scripts
- TTS announcements
- Multi-step alert response procedures

## Technical Highlights

### Async/Await Pattern

All I/O operations use async/await for non-blocking execution, ensuring Home Assistant remains responsive.

### Proper Error Handling

- Network timeouts handled gracefully
- Invalid XML doesn't crash the integration
- HTTP errors logged and reported

### Efficient Updates

- Only fetches when needed (configurable interval)
- Caches data between updates
- Filters at parse time to reduce memory usage

### Standards Compliant

- Follows Home Assistant integration guidelines
- Uses standard coordinator pattern
- Proper entity naming and unique IDs
- Type hints throughout

## Testing

### Parser Tests

- Direct CAP XML parsing
- Atom feed with CAP entries
- Multiple info sections
- Area filtering
- Invalid/malformed XML handling
- Edge cases

### Manual Testing Recommended

- Test with actual CHMI feed
- Verify updates occur at configured interval
- Check sensor attributes populated correctly
- Test area filtering with real data
- Verify automations trigger properly

## Future Enhancements

Potential improvements:

- Individual sensor per alert
- Alert history tracking
- Severity-based binary sensors
- Alert expiration notifications
- Support for CAP 1.1 feeds
- Polygon/circle area matching
- Multi-language alert display

## Security

✅ No security vulnerabilities detected (CodeQL scan passed)
✅ No hardcoded credentials
✅ Safe XML parsing
✅ Proper input validation
✅ No SQL injection risks
✅ No XSS vulnerabilities

## License

This project is licensed under the Apache License 2.0. See LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Fork the repository
1. Create a feature branch
1. Make your changes
1. Add tests if applicable
1. Submit a pull request

## Support

For questions, issues, or feature requests:

- GitHub Issues: https://github.com/nijel/hass-cap-alerts/issues
- GitHub Discussions: https://github.com/nijel/hass-cap-alerts/discussions

## Credits

- Created by @nijel
- CAP specification by OASIS Emergency Management TC
- Inspired by the need for weather alerts in Home Assistant
