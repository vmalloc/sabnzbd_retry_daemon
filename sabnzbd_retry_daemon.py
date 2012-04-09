#! /usr/bin/python
from __future__ import print_function
import argparse
import json
import logging
import re
import sys
from urllib2 import urlopen

parser = argparse.ArgumentParser(usage="%(prog)s [options] args...")
parser.add_argument("-v", "--verbose", action="store_true", default=False)
parser.add_argument("-a", "--apikey", dest="api_key", required=True)
parser.add_argument("-H", "--host", default="127.0.0.1")
parser.add_argument("-p", "--port", default=8080, type=int)
parser.add_argument("-l", "--history-limit", default=20, type=int)

def main(args):
    for retry_url in _get_retry_urls(args):
        _retry(args, retry_url)
    return 0

def _get_retry_urls(args):
    url = "http://{}:{}/api?mode=history&limit={}&output=json&apikey={}".format(args.host, args.port, args.history_limit, args.api_key)
    logging.debug("Getting %s", url)
    data = json.loads(urlopen(url).read())
    for slot in data['history']['slots']:
        retry_url = _extract_retry_url(slot)
        if retry_url is not None:
            yield retry_url

_RETRY_URL_REGEXP = r"fetching failed.+a href=\"\.(/retry.+?)\">Try again"
def _extract_retry_url(slot):
    fail_msg = slot.get('fail_message', None)
    if fail_msg is not None:
        match = re.search(_RETRY_URL_REGEXP, fail_msg, re.I)
        if match is not None:
            logging.debug("Found failed fetching: %s", slot['name'])
            return match.group(1)

def _retry(args, url):
    url = "http://{}:{}{}".format(args.host, args.port, url)
    logging.debug("Retrying %s", url)
    data = urlopen(url).read()
################################## Boilerplate #################################
_LOGGING_FORMAT = "%(asctime)s -- %(message)s"
def _configure_logging(args):
    if not args.verbose:
        return
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format=_LOGGING_FORMAT,
        )

#### For use with entry_points/console_scripts
def main_entry_point():
    args = parser.parse_args()
    _configure_logging(args)
    sys.exit(main(args))
if __name__ == '__main__':
    main_entry_point()
