import time
import requests
import json
import urllib3
import argparse
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client.registry import Collector

metric_types = [
    {"name": "i2p.router.status", "description": "What the status of the router is. A free-format, translated string intended for display to the user. May include information such as whether the router is accepting participating tunnels. Content is implementation-dependent."},
    {"name": "i2p.router.uptime", "description": "What the uptime of the router is in ms. Note: i2pd routers prior to version 2.41 returned this value as a string. For compatibility, clients should handle both string and long."}, # Haha we don't and it's probably fine since 2.40 is a 3 year old release
    {"name": "i2p.router.version", "description": "What version of I2P the router is running."},
    {"name": "i2p.router.net.bw.inbound.1s", "description": "The 1 second average inbound bandwidth in Bps."},
    {"name": "i2p.router.net.bw.inbound.15s", "description": "The 15 second average inbound bandwidth in Bps."},
    {"name": "i2p.router.net.bw.outbound.1s", "description": "The 1 second average outbound bandwidth in Bps."},
    {"name": "i2p.router.net.bw.outbound.15s", "description": "The 15 second average outbound bandwidth in Bps."},
    {"name": "i2p.router.net.status", "description": "What the current network status is. See enum at https://geti2p.net/en/docs/api/i2pcontrol"},
    {"name": "i2p.router.net.tunnels.participating", "description": "How many tunnels on the I2P net are we participating in."},
    {"name": "i2p.router.netdb.activepeers", "description": "How many peers have we communicated with recently."},
    # These next 3 are defined in the spec but i2pd doesn't provide them.
    {"name": "i2p.router.netdb.fastpeers", "description": "How many peers are considered 'fast'."},
    {"name": "i2p.router.netdb.highcapacitypeers", "description": "How many peers are considered 'high capacity'."},
    {"name": "i2p.router.netdb.isreseeding", "description": "Is the router reseeding hosts to its NetDB?"},
    {"name": "i2p.router.netdb.knownpeers", "description": "How many peers are known to us (listed in our NetDB)."},
]

class I2pdCollector(Collector):
    def __init__(self, i2pcontrol_host, validate_tls):
        self.i2pcontrol_host = i2pcontrol_host
        self.validate_tls = validate_tls

    def get_metrics(self):
        payload = {
            "id": 1,
            "method": "RouterInfo",
            "params": dict((metric["name"], None) for metric in metric_types),
            "jsonrpc": "2.0"
        }

        return requests.post(
            self.i2pcontrol_host,
            data=json.dumps(payload),
            headers={'content-type': 'application/json'},
            timeout=10,
            verify=self.validate_tls
        ).json()['result']

    def collect(self):
        metrics = self.get_metrics()

        for metric in metric_types:
            if metric["name"] not in metrics:
                continue

            if metric["name"] == 'i2p.router.version':
                # Special handling for i2p.router.version since it's a string
                version_gauge = GaugeMetricFamily(
                    metric["name"].replace('.', '_'),
                    metric["description"],
                    labels = ['router_version']
                )

                version_gauge.add_metric([metrics[metric["name"]]], 1)

                yield version_gauge
            else:
                yield GaugeMetricFamily(
                    metric["name"].replace('.', '_'),
                    metric["description"],
                    value = metrics[metric["name"]]
                )

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p", "--listen-port",
        type = int,
        help = "Port to expose metrics on",
        default = 8000
    )

    parser.add_argument(
        "-l", "--listen-address",
        help="IP address to expose metrics on",
        default="127.0.0.1"
    )

    parser.add_argument(
        "-a", "--i2pcontrol-address",
        help = "IP address of I2P server",
        default = "127.0.0.1"
    )

    parser.add_argument(
        "-c", "--i2pcontrol-port",
        help = "Port for I2PControl",
        type = int,
        default = 7650
    )

    parser.add_argument(
        "-v", "--validate-tls",
        help = "Validate TLS certificate of I2PControl",
        action='store_true'
    )

    args = parser.parse_args()

    if not args.validate_tls:
        # urllib3 will warn on every request if we don't do this
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    REGISTRY.register(I2pdCollector(f'https://{args.i2pcontrol_address}:{args.i2pcontrol_port}/', args.validate_tls))
    start_http_server(args.listen_port, addr=args.listen_address)

    while True:
        time.sleep(30)

if __name__ == '__main__':
    main()
