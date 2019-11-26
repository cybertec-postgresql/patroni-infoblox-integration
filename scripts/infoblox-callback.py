#!/usr/bin/env python
import argparse
import logging
import os
import socket
import sys
import time

from infoblox_client import connector, objects
from infoblox_client import exceptions as ib_exc

logger = logging.getLogger(__name__)


def exponential_backoff(start=0.1, max=60, factor=2):
    backoff_time = start
    while True:
        yield
        logger.debug("Delaying retry by {}".format(backoff_time))
        time.sleep(backoff_time)
        backoff_time = min(backoff_time*factor, max)


def claim_master_role(args):
    opts = {'host': args.hostname, 'username': args.username, 'password': args.password}
    if args.wapi_version:
        opts['wapi_version'] = args.wapi_version
    conn = connector.Connector(opts)

    arecord_name = args.arecord.format(cluster=args.cluster)

    if not arecord_name:
        logger.error("Record name not specified")
        return

    for _ in exponential_backoff():
        try:
            found = None
            old_records = objects.ARecord.search_all(conn, name=arecord_name, view=args.dns_view)
            logger.info("Found %d existing records for %s", len(old_records), arecord_name)
            for old_record in old_records:
                logger.info("Existing mapping for %s: %s", arecord_name, old_record.ipv4addr)
                if old_record.ipv4addr != args.ip:
                    logger.info("Deleting existing mapping for %s", old_record.ipv4addr)
                    old_record.delete()
                else:
                    found = True
            if found is None:
                new_record = objects.ARecord.create(conn, update_if_exists=True,
                                                    name=arecord_name, ipv4addr=args.ip, view=args.dns_view,
                                                    comment=args.comment.format(cluster=args.cluster))
                logger.info("Host %s updated to %s", new_record.name, new_record.ipv4addr)
            else:
                logger.info("Keeping existing mapping %s", found.to_dict())
            return
        except ib_exc.BaseExc as e:
            logger.error("Error when updating DNS record %s to %s: %s", arecord_name, args.ip, e)


def record_role_change(args):
    new_role = None if args.action == 'on_stop' else args.new_role
    logger.debug("Changing the nodes role to %s", new_role)
    if new_role == 'master':
        logger.info("Redirecting master service")
        claim_master_role(args)


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except:
        return None
    finally:
        s.close()


def main():
    wapi_host = os.environ.get('WAPI_HOST')
    wapi_user = os.environ.get('WAPI_USER')
    wapi_password = os.environ.get('WAPI_PASSWORD')
    wapi_version = os.environ.get('WAPI_VERSION')
    wapi_dns_view = os.environ.get('WAPI_DNS_VIEW', 'default')
    wapi_comment = os.environ.get('WAPI_COMMENT', "Patroni cluster {cluster} master IP")
    v4_host_template = os.environ.get('DATABASE_MASTER_HOSTNAME_TEMPLATE')

    parser = argparse.ArgumentParser(description="Patroni Infoblox integration script")
    parser.add_argument('-4', '--arecord', required=v4_host_template is None, default=v4_host_template,
                        help="hostname of arecord to create or update. {cluster} "
                             "placeholder will be replaced with value passed in by Patroni")
    parser.add_argument('-i', '--ip', default=get_my_ip(), help="IP address to route DNS to.")
    parser.add_argument('-v', '--dns-view', default=wapi_dns_view, help="DNS view for the arecord")
    parser.add_argument('--comment', default=wapi_comment,
                        help="Comment line on the arecord entry")
    parser.add_argument('-H', '--hostname', required=wapi_host is None, default=wapi_host,
                        help="WAPI endpoint address")
    parser.add_argument('-u', '--username', required=wapi_user is None, default=wapi_user,
                        help="WAPI username")
    parser.add_argument('-p', '--password', required=wapi_password is None, default=wapi_password,
                        help="WAPI password")
    parser.add_argument('--wapi-version', default=wapi_version, help="WAPI version")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    parser.add_argument('action')
    parser.add_argument('new_role')
    parser.add_argument('cluster')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.DEBUG if args.debug else logging.INFO)

    if args.action in ('on_start', 'on_stop', 'on_role_change', 'on_restart'):
        record_role_change(args)
    else:
        parser.print_help()
        sys.exit(1)
    return 0


if __name__ == '__main__':
    main()
