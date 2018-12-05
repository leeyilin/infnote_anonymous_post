import tornado.web
import tornado.websocket
import tornado
import sys, threading, time
from stem.control import Controller
from stem import SocketError, UnsatisfiableRequest, CircStatus
import stem.process
import struct
from stem.util import term
from base58 import b58encode
from key import Key


WEB_PORT = 8080
CONTROL_PORT = 7001
SOCKS_PORT = 7000
HIDDEN_SERVICE_DIR = '/tmp/tor/'


class MyTorProcess(object):
    def __init__(self, socks_port, control_port):
        self._socks_port = socks_port
        self._control_port = control_port
        self._tor_process = None
        self._controller = None
        self._onion_name = ''

    def launch_tor(self):

        def print_bootstrap_lines(line):
            if "Bootstrapped " in line:
                print(term.format(line, term.Color.BLUE))
        
        print(term.format("Starting Tor:", term.Attr.BOLD))
        self.tor_process = stem.process.launch_tor_with_config(
          config = {
            'SocksPort': str(self._socks_port),
            'ControlPort': str(self._control_port),
            #'ExitNodes': '{ru}',
          },
          init_msg_handler = print_bootstrap_lines,
        )
        
    def list_circuits(self):
        print('='*30, '\nlist circuits:')
        for circ in sorted(self._controller.get_circuits()):
            if circ.status != CircStatus.BUILT:
                continue
            print('\nCircuit ID(%s) (purpose: %s)' % (circ.id, circ.purpose))
            for i, entry in enumerate(circ.path):
                div = '+' if (i == len(circ.path) - 1) else '|'
                fingerprint, nickname = entry
                desc = self._controller.get_network_status(fingerprint, None)
                address = desc.address if desc else 'unknown'
                print('div:%s- fingerprint:%s (nickname:%s, address: %s)' %\
                        (div, fingerprint, nickname, address))
        print('='*30)

    def create_hidden_service(self, from_port, to_port, hidden_service_dir):
        # wait for the web app to launch
        time.sleep(1)
        try:
            # Connect to the Tor control port
            self._controller = Controller.from_port(port=self._control_port)
            self._controller.authenticate()
            print('Creating hidden service')
            result = self._controller.create_hidden_service(hidden_service_dir, 
                    to_port, target_port=from_port)
            print(" * Created host: %s" % result.hostname)
            self._onion_name = result.hostname
            self.list_circuits()
        except (SocketError, UnsatisfiableRequest) as e:
            print(e)
            sys.exit()


@tornado.web.stream_request_body
class MainHandler(tornado.web.RequestHandler):
    connections = {}
    # Normal http get for testing.
    def get(self):
        print('One client connected!')
        #return self.write('Ack!\n\n')
        return self.render('template/index.html', title='Discussion Forum', 
                items=['to be,', 'or not to be,', 'that is a question.'])
    
    def post(self):
        print('One client posted me')
        return self.write('post accepted!')
    
    def data_received(self, chunk):
        if str(self) in self.connections:
            self.connections[str(self)] += chunk
        else:
            self.connections[str(self)] = chunk
        self._handle_buffer()

    # hard-decoding is not interesting and elegant...
    def _handle_buffer(self):
        buf = self.connections[str(self)]
        receive_len = 0
        if len(buf) >= 4:
            public_key = 'w2vCKeZTQSaUqPsQ2BGL8tCuzfGjtbtkXPKwruwu9L9X'
            key = Key(public_key=public_key)
            signature_length, = struct.unpack_from('<i', buf, offset=receive_len)
            receive_len += 4
            if len(buf) >= receive_len + signature_length:
                receive_len += signature_length
                mysignature = buf[4:receive_len]
                if len(buf) >= receive_len + 4:
                    content_length, = struct.unpack_from('<i', buf, offset=receive_len)
                    receive_len += 4
                    if len(buf) >= receive_len + content_length:
                        receive_len += content_length
                        raw_mypost = buf[receive_len-content_length:receive_len]
                        if key.verify(b58encode(mysignature), raw_mypost):
                            print('verification pass!')
                        else:
                            print('verification failed...')
                        print('post received:\n', raw_mypost.decode())
                        self.connections[str(self)] = \
                            self.connections[str(self)][receive_len:]


class IPHandler(tornado.web.RequestHandler):
    def get(self):
        print('One client connected!')
        return self.write(repr(self.request) + '\n\n')


class SimpleWebSocket(tornado.websocket.WebSocketHandler):
    connections = set()

    # Had better check the origin later.
    def check_origin(self, origin):
        return True

    def open(self):
        print('one client connected!')
        self.write_message('Tell me more!\n')
        self.connections.add(self)

    def on_message(self, message):
        print('receive: ', message)
        #time.sleep(1)
        [client.write_message(message) for client in self.connections]

    def on_close(self):
        print('one client disconnected!')
        self.connections.remove(self)


def start_web_app(listen_port):
    app = tornado.web.Application([
            (r'/websocket', SimpleWebSocket),
            (r'/', MainHandler),
            (r'/get_my_ip', IPHandler)
        ])
    app.listen(listen_port)
    print('Begin to Push traffic periodically as long as there is any client ...')
    tornado.ioloop.PeriodicCallback(push_traffic, 1000).start()
    tornado.ioloop.IOLoop.instance().start()


def push_traffic():
    time.sleep(1)
    for conn in SimpleWebSocket.connections:
        conn.write_message(u'Push traffic...\n')


if __name__ == '__main__':
    my_tor_process = MyTorProcess(SOCKS_PORT, CONTROL_PORT)
    my_tor_process.launch_tor()

    threading.Thread(target=my_tor_process.create_hidden_service, 
            args=(WEB_PORT, 80, HIDDEN_SERVICE_DIR)).start()
    start_web_app(WEB_PORT)

