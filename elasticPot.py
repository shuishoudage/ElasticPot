import asyncio
from aiohttp import server
import aiohttp
import logging
import json
import uuid
import os
from handler import Handler
import argparse

fakeDataPrefix = './FakeData/'


class HttpRequestHandler(aiohttp.server.ServerHttpProtocol):
    def __init__(self, debug=False, keep_alive=75, **kwargs):
        super().__init__(debug=debug,
                         keep_alive=keep_alive, access_log=None, **kwargs)

    def create_data(self, request):
        request_data = dict(
            method=None,
            path=None,
            headers=None,
            uuid=None,
            )
        if request:
            header = {key: value for(key, value) in request.headers.items()}
            request_data['method'] = request.method
            request_data['headers'] = header
            request_data['path'] = request.path
        return request_data

    @asyncio.coroutine
    def send_data(self, req_data):
        try:
            with aiohttp.Timeout(10.0):
                with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                    r = yield from session.put(
                        'http://localhost:9200/attack/attack_info/{0}?pretty'.format(uuid.uuid1()),
                        data=json.dumps(req_data)
                        )
                    assert r.status == 201
        except Exception as e:
            raise e
        finally:
            r.close()

    @asyncio.coroutine
    def handle_request(self, request, payload):
        req_data = self.create_data(request)
        yield from self.send_data(req_data)
        logging.info('\trequest data has send to database')
        response = aiohttp.Response(
            self.writer, 200, http_version=request.version
            )
        if request.method == 'GET':
            logging.info('\tGET path:{}'.format(request.path))
            contents = Handler().GET_handler(request)
        if request.method == 'POST':
            logging.info('\tPOST payload:{}'.format(payload))
            contents = Handler().POST_handler(request)
        if request.method == 'PUT':
            logging.info('\tPUT payload:{}'.format(payload))
            contents = Handler().PUT_handler(request)
        if request.method == 'DELETE':
            logging.info('\tDELETE path:{}'.format(request.path))
            contents = Handler().DELETE_handler(request)
        response.add_header('Content-Type', 'text/plain')
        response.add_header('Content-Length', str(len(contents)))
        response.send_headers()
        response.write(contents.encode('utf-8'))
        yield from response.write_eof()


def parseArguments():
    parser = argparse.ArgumentParser(description='An elastic search honeypot')
    parser.add_argument('-ht', '--host', help='host address of this honeypot',
                        default='localhost', type=str)
    parser.add_argument('-p', '--port', help='port of this honeypot',
                        default=9200, type=int)
    parser.add_argument('-d', '--debug', help='turn on debug mode',
                        action='store_true')
    parser.add_argument('-l', '--log_path', help='specify a log path',
                        default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parseArguments()
    if args.debug:
        logging.basicConfig(level=logging.INFO)
    if args.log_path is not None:
        if os.path.exists(args.log_path):
            logging.basicConfig(filename=args.log_path,
                                filemode='a',
                                level=logging.INFO)
        else:
            open(args.log_path, 'a').close()
            logging.basicConfig(filename=args.log_path,
                                filemode='a',
                                level=logging.INFO)

    loop = asyncio.get_event_loop()
    # register the handler within a server
    f = loop.create_server(
        lambda: HttpRequestHandler(debug=True, keep_alive=75),
        host=args.host, port=args.port)
    logging.info('\tserver started')
    srv = loop.run_until_complete(f)
    logging.info('\tserver on: {0}'.format(srv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
