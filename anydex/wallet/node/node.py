import json
import logging
import socket
from enum import Enum, auto
from ipaddress import ip_address, IPv4Address
from time import time
from urllib.parse import urlparse

from anydex.config import get_anydex_configuration
from anydex.wallet.cryptocurrency import Cryptocurrency

_logger = logging.getLogger(__name__)


class Source(Enum):
    """
    Enum representing possible provider source for nodes.
    Currently supports nodes provided by users or by AnyDex.
    """

    DEFAULT = auto()
    USER = auto()


class Node:
    """
    Concrete class to create nodes from.
    A node is an abstraction for a node component in a cryptocurrency network.

    Each cryptocurrency should allow for a user-provided node implementation, as well as
    a DefaultNode-class implementation.
    """

    def __init__(self, name: str, host: str, port: int, source: Source, network: Cryptocurrency,
                 latency: float, protocol: str = 'http', username='', password=''):
        self.name = name
        self.host = host
        self.port = port
        self.source = source
        self.network = network
        self.latency = latency
        self.protocol = protocol
        self.username = username
        self.password = password

    def __repr__(self):
        return f'{self.name}\n' \
               f'address: {self.host}:{self.port}\n' \
               f'source: {self.source}\n' \
               f'network: {self.network.value}\n' \
               f'latency: {self.latency}\n' \
               f'protocol: {self.protocol}'


def create_node(network: Cryptocurrency) -> Node:
    """
    Constructs a Node from user-provided parameters if key is present in `config.py`-dictionary.
    Else: constructs Node picked from set of default nodes provided by AnyDex.

    Raise MissingParameterException if required parameters miss from user Node-config: host, port

    :param network: instance of Cryptocurrency enum
    :return: Node
    """
    config = get_anydex_configuration()
    params = {'network': network}

    # TODO split user/default node retrieval
    if 'node' in config:
        _logger.info('Parsing user node config')

        node_config = config['nodes']['node']
        params['source'] = Source.USER
        params['name'] = node_config.get('name', '')

        try:
            params['host'] = node_config['host']
        except KeyError:
            raise CannotCreateNodeException('Missing key `host` from node config')

        try:
            params['port'] = node_config['port']
        except KeyError:
            # TODO don't raise bare exceptions
            raise CannotCreateNodeException('Missing key `port` from node config')

        params['protocol'] = node_config.get('protocol', 'http')
        params['username'] = node_config.get('username', '')
        params['password'] = node_config.get('password', '')

        params['latency'] = determine_latency(params['host'], params['port'])
    else:
        _logger.info('Finding best host from pool of default hosts')

        params['source'] = Source.DEFAULT
        params['name'] = ''

        default_hosts = read_default_hosts()

        try:
            network_hosts = default_hosts[network.value]
        except KeyError:
            # TODO don't raise bare exceptions
            raise CannotCreateNodeException(f'Missing default nodes for {network.value}')

        # host format: protocol://username:password@domain
        selected_host, latency = select_best_host(network_hosts)
        protocol, username, password, host, port = parse_url(selected_host)

        if protocol:
            params['protocol'] = protocol
        if username:
            params['username'] = username
        if password:
            params['password'] = password

        params['host'], params['port'] = host, port
        params['latency'] = latency

    node = Node(**params)
    _logger.info(f'Using following node:\n{node}')
    return node


class CannotCreateNodeException(Exception):
    """
    Raise exception from `create_node` if configuration is lacking.
    """
    pass


def read_default_hosts():
    """
    Read default nodes for each cryptocurrency from `hosts.json`.

    :return: return dictionary of cryptocurrency network and corresponding hosts
    """
    nodes = dict()

    with open('hosts.json') as file:
        try:
            nodes = json.loads(file.read())
        except json.JSONDecodeError as err:
            _logger.error(f'Default nodes file could not be decoded: {err}')

    return nodes


def select_best_host(hosts) -> tuple:
    """
    Returns the host with the lowest latency of all hosts.

    :param hosts: list of host names including ports
    :return: tuple of host and latency
    """
    results = dict()

    for host in hosts:
        # TODO investigate possibilities for multi-threaded or async approach
        _, _, _, address, port = parse_url(host)
        _logger.info(f'Determining latency for {address} at port {port}')
        latency = determine_latency(address, port)
        results[host] = latency

    best_host = [(k, v) for k, v in sorted(results.items(), key=lambda el: el[1])][0]
    return best_host


def determine_latency(address: str, port: int) -> float:
    """
    Returns latency to server with address passed as parameter.
    Attempts to connect to `port` at `host` while timing the roundtrip.

    :param address
    :param port
    :return: latency in ms as float
    """
    try:
        addr = ip_address(address)
    except ValueError:
        return float('inf')

    if isinstance(addr, IPv4Address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    cfg = get_anydex_configuration()
    timeout = cfg['nodes']['timeout']
    sock.settimeout(timeout)

    retry: int = cfg['nodes']['retry']
    durations = []

    for count in range(retry):
        start_time = time()
        try:
            sock.connect((address, port))
            sock.shutdown(socket.SHUT_RD)
        except socket.timeout:
            _logger.warning(f'Ping attempt to host {address} timed out after {timeout} seconds')
            return float('inf')
        except OSError:
            return float('inf')
        durations.append(time() - start_time)

    return round(avg(durations) * 1000, 2)


def avg(elements: list):
    return sum(elements) / len(elements)


def parse_url(url: str) -> tuple:
    parsed = urlparse(url)
    protocol = parsed.scheme
    username = parsed.username
    password = parsed.password
    host, port = parsed.netloc.split(':')
    return protocol, username, password, host, port
