"""
TLS probe for MongoDB Atlas SRV hosts.
Resolves SRV records for the cluster and attempts an SSL/TLS handshake to each discovered host:port.
Prints TLS protocol and certificate subject / SANs.

Run from the repo root or this folder with:
python tls_probe.py
"""

import socket
import ssl
import sys

try:
    import dns.resolver
except Exception as e:
    print("dnspython not installed:", e)
    sys.exit(2)

CLUSTER = "cluster0.fkup1pl.mongodb.net"
SRV_NAME = f"_mongodb._tcp.{CLUSTER}"

def resolve_srv(srv_name):
    try:
        answers = dns.resolver.resolve(srv_name, 'SRV')
        hosts = []
        for r in answers:
            hosts.append((str(r.target).rstrip('.'), int(r.port)))
        return hosts
    except Exception as e:
        print(f"SRV lookup failed for {srv_name}: {e}")
        return []


def probe_host(host, port, timeout=10):
    print(f"\n--- {host}:{port}")
    try:
        context = ssl.create_default_context()
        # Enforce hostname verification
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                proto = ssock.version()
                print("TLS protocol:", proto)
                cert = ssock.getpeercert()
                subj = cert.get('subject', ())
                cn = [t[0][1] for t in subj if t and t[0][0] == 'commonName']
                print('Common Name(s):', cn)
                # SubjectAltName
                san = cert.get('subjectAltName', ())
                sans = [v for (k, v) in san if k.lower() == 'dns']
                print('SANs:', sans)
    except ssl.SSLError as e:
        print('SSL error connecting:', e)
    except Exception as e:
        print('Error connecting:', e)


if __name__ == '__main__':
    hosts = resolve_srv(SRV_NAME)
    if not hosts:
        print('No SRV hosts found; exiting')
        sys.exit(1)
    for h, p in hosts:
        probe_host(h, p)
    print('\nProbe complete')
