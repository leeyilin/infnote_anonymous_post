import sys
import websocket
import threading
import time
import requests
import struct
import socks
from key import Key


def on_message(ws, message):
    print('receive: ', message)
    time.sleep(1)
    print('send message: ping')
    ws.send('ping')


def on_error(ws, error):
    print('in on_error():', error)


def on_close(ws):
    print('in on_close()')


def on_open(ws):
    print('in on_open()')
    print('send: foo')
    ws.send('foo')


def http_request(url, method, proxy_url=None, data=None):
    tor_session = requests.session()
    if proxy_url:
        tor_session.proxies = {
                'http': proxy_url,
                'https': proxy_url,
            }

    print('request of %s to: %s ...' % (method, url))
    if method.upper() == 'GET':
        print('response:\n', tor_session.get(url).text)
    elif method.upper() == 'POST':
        print('response:\n', tor_session.post(url, data=data).text)
    else:
        print('Unknown method: ', method)
        sys.exit()


def forum_post(url, proxy_url, data):
    data = str(data)
    public_key = 'w2vCKeZTQSaUqPsQ2BGL8tCuzfGjtbtkXPKwruwu9L9X'
    private_key = 'GPdbe25KbTJqAVfKXrYsg4uMREkZSuCPdCBL1vZsb4fb'
    key = Key(public_key=public_key, private_key=private_key)
    signature = key.sign(data=data.encode())
    raw = struct.pack('<i', len(signature)) + signature\
            +struct.pack('<i', len(data)) + data.encode()
    http_request(url, 'POST', proxy_url, raw)


def main():
    server_hostname = None
    with open('/tmp/tor/hostname', 'r') as f:
        server_hostname = f.read().strip()
    for i in range(10):
        try:
            print('number of trial:', i)
            http_request('http://'+server_hostname, 'GET', 'socks5h://localhost:7000')
            forum_post('http://'+server_hostname, 'socks5h://localhost:7000',
                data = {
                        'title': 'To be or not to be, that is a question', 
                        'author': 'goldman', 
                        'content': 'Where is this famous quote from?'
                    })
            #websocket.enableTrace(True)
            url = 'ws://'+server_hostname+'/websocket'
            print('websocket to:', url, ' ...')
            ws = websocket.WebSocketApp(url,
                    on_message=on_message, on_error=on_error, 
                    on_close=on_close, on_open=on_open)
            ws.run_forever(proxy_type='socks5h',
                    http_proxy_host='localhost',
                    http_proxy_port=7000)
            break
        except (socks.SOCKS5Error, requests.exceptions.ConnectionError) as e:
            print(e, '\n', 'try again ... ...')
            time.sleep(1)


if __name__ == '__main__':
    main()
    
