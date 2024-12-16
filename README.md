# prometheus-i2p-exporter
A Prometheus exporter for I2P node metrics fetched from I2PControl. Currently I've only tested it with i2pd, and password authentication is not implemented since it is broken in i2pd anyway.

## Installation
1. Enable I2PControl. In I2P you need to get the I2PControl plugin, in i2pd you enable it through the [config file.](https://i2pd.readthedocs.io/en/latest/user-guide/configuration/#i2pcontrol-interface) I've only tested i2pd so if you're running I2P this may or may not work. Open a ticket if it doesn't!
2. Install dependencies: `pip install -r requirements.txt`
3. Run `python prometheus-i2p-exporter.py`  
The default settings should work if I2P and Prometheus are running on the same server, but there's `--help` to see the full list of arguments.  
There's also `-v/--validate-tls` if you for some reason went through the trouble of getting a valid TLS cert for I2PControl.
4. Add prometheus-i2p-exporter as a target to your Prometheus config. The default port is 8000 but it can be changed with `-p/--listen-port`
5. Probably set it up as a service rather than running it manually.

## Prometheus alerts
There are some basic alerts in `prom-alerts.yaml` if you really want to get woken up at 4am because your I2P node is broken

## Grafana dashboard
There's also a Grafana dashboard in `dashboard.json`
