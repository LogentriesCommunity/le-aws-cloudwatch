import logging
import json
import gzip
import socket
import ssl
import certifi
from StringIO import StringIO
import os
from uuid import UUID

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function...')

REGION = os.environ.get('region')
ENDPOINT = 'data.{}.logentries.com'.format(REGION)
PORT = 20000
TOKEN = os.environ.get('token')


def lambda_handler(event, context):
    sock = create_socket()

    if not validate_uuid(TOKEN):
        logger.critical('{} is not a valid token. Exiting.'.format(TOKEN))
        raise SystemExit
    else:
        cw_data = str(event['awslogs']['data'])
        cw_logs = gzip.GzipFile(fileobj=StringIO(cw_data.decode('base64', 'strict'))).read()
        log_events = json.loads(cw_logs)
        logger.info('Received log stream...')
        for log_event in log_events['logEvents']:
            # look for extracted fields, if not present, send plain message
            try:
                sock.sendall('{} {}\n'.format(TOKEN, json.dumps(log_event['extractedFields'])))
            except KeyError:
                sock.sendall('{} {}\n'.format(TOKEN, log_event['message']))

    sock.close()
    logger.info('Function execution finished.')


def create_socket():
    logger.info('Creating SSL socket')
    s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s = ssl.wrap_socket(
        sock=s_,
        keyfile=None,
        certfile=None,
        server_side=False,
        cert_reqs=ssl.CERT_REQUIRED,
        ssl_version=getattr(
            ssl,
            'PROTOCOL_TLSv1_2',
            ssl.PROTOCOL_TLSv1
        ),
        ca_certs=certifi.where(),
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
    )
    try:
        logger.info('Connecting to {}:{}'.format(ENDPOINT, PORT))
        s.connect((ENDPOINT, PORT))
        return s
    except socket.error, exc:
        logger.error('Exception socket.error : {}'.format(exc))


def validate_uuid(uuid_string):
    try:
        val = UUID(uuid_string)
    except Exception as uuid_exc:
        logger.error('Can not validate token: ' + uuid_exc)
        return False
    return val.hex == uuid_string.replace('-', '')
