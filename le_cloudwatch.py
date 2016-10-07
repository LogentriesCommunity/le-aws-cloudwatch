import logging
import json
import gzip
import re
import socket
import uuid
import ssl
import certifi
from StringIO import StringIO
from le_config import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
HOST = 'data.logentries.com'
PORT = 20000


def lambda_handler(event, context):
    # create stream uuid
    stream_id = str(uuid.uuid4())
    # validate and store debug log tokens
    tokens = []
    if validate_uuid(debug_token) is True:
        tokens.append(debug_token)
    if validate_uuid(lambda_token) is True:
        tokens.append(lambda_token)
    else:
        pass

    # Create socket connection to Logentries
    sock = create_socket()

    # get CloudWatch logs
    cw_data = str(event['awslogs']['data'])

    # decode and uncompress CloudWatch logs
    cw_logs = gzip.GzipFile(fileobj=StringIO(cw_data.decode('base64', 'strict'))).read()

    # convert the log data from JSON into a dictionary
    log_events = json.loads(cw_logs)

    # Send debug info re start of stream
    for token in tokens:
        send_to_le("\"streamID\": \"{}\" le_cloudwatch"
                   " \"user\": \"{}\" started sending logs".format(stream_id[:8], username), sock, token)

    # loop through the events and send to Logentries
    for log_event in log_events['logEvents']:

        # look for extracted fields, if not present, send plain message
        try:
            send_to_le(json.dumps(log_event['extractedFields']), sock, log_token)
        except KeyError:
            send_to_le(log_event['message'], sock, log_token)

    # Send debug info re end of stream
    for token in tokens:
        send_to_le("\"streamID\": \"{}\" le_cloudwatch"
                   " \"user\": \"{}\" finished sending logs".format(stream_id[:8], username), sock, token)
    # close socket
    sock.close()


def create_socket():
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
        s.connect((HOST, PORT))
        return s
    except socket.error, exc:
        print "Caught exception socket.error : %s" % exc


def send_to_le(line, le_socket, token):
    le_socket.sendall('%s %s\n' % (token, line))


def validate_uuid(uuid_string):
    regex = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.I)
    match = regex.match(uuid_string)
    return bool(match)
