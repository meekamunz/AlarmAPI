Run roar.exe either from a File Explorer window or from command line.  You can optionally pass a GV Orbit server IP Address on the command line:
roar [IP address of GV Orbit server]

The application launches a GUI window with four tabs:

**Collect Alarms** — Connect to a source GV Orbit server, browse devices, filter by severity (Critical/Warn/OK/Unknown/All), and collect alarms into a table.  Save collected alarms to CSV or JSON.

**Publish Alarms** — Set a destination GV Orbit server, create a publisher, and publish alarms.  You can publish the alarms collected on the Collect tab, import from a CSV or JSON file, or publish a single alarm manually.  Use "Start Maintaining" to keep the publisher alive in the background.

**Live Data** — Subscribe to alarm changes on a server (selected devices or all) and view live alarm updates in real time.

**Utilities** — Purge stale alarm data from a server.

On exit, the application automatically cleans up any active publishers and subscribers.

The old CLI version is preserved as roar_cli.py for reference.

Michael.Munns@grassvalley.com