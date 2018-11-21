import websocket
import threading
import time
import requests


def on_message(ws, message):
    print('receive: ', message)
    print('send message: ping')
    time.sleep(1)
    ws.send('ping')


def on_error(ws, error):
    print('in on_error():', error)


def on_close(ws):
    print('in on_close()')


def on_open(ws):
    print('in on_open()')
    print('send: foo')
    ws.send('foo')


def http_get(url, proxy_url):
    tor_session = requests.session()
    tor_session.proxies = {
            'http': proxy_url,
            'https': proxy_url,
        }
    print('Request:%s:\n%s\n' % (url, tor_session.get(url).text))


def main():
    server_hostname = None
    with open('/tmp/tor/hostname', 'r') as f:
        server_hostname = f.read().strip()

    http_get('http://'+server_hostname+'/get_my_ip', 'socks5h://localhost:7000')
    
    #websocket.enableTrace(True)
    url = 'ws://'+server_hostname+'/websocket'
    print('websocket to:', url, ' ...')
    ws = websocket.WebSocketApp(url,
            on_message=on_message, on_error=on_error, 
            on_close=on_close, on_open=on_open)
    ws.run_forever(proxy_type='socks5h',
            http_proxy_host='localhost',
            http_proxy_port=7000)
        


if __name__ == '__main__':
    main()


    
