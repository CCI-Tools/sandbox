import tornado.ioloop
import tornado.websocket


def on_http_response(response):
    if response.error:
        print('Error:', response.error)
    else:
        print('HTTP response:', response.body)


port = 8080

http_client = tornado.httpclient.AsyncHTTPClient()
http_client.fetch("http://localhost:%s/sum/25" % port, on_http_response, request_timeout=30)
http_client.fetch("http://localhost:%s/sum/50" % port, on_http_response, request_timeout=30)
http_client.fetch("http://localhost:%s/sum/75" % port, on_http_response, request_timeout=30)
http_client.fetch("http://localhost:%s/sum/100" % port, on_http_response, request_timeout=30)
http_client.fetch("http://localhost:%s/sum/250" % port, on_http_response, request_timeout=30)


def on_ws_open(connect_future):
    connect = connect_future.result()
    connect.write_message('25')
    connect.write_message('50')
    connect.write_message('75')
    connect.write_message('100')
    connect.write_message('250')


def on_ws_message(message):
    print('WebSocket message:', message)


tornado.websocket.websocket_connect("ws://localhost:%s/sum/ws" % port, callback=on_ws_open,
                                    on_message_callback=on_ws_message)

io_loop = tornado.ioloop.IOLoop.current()
io_loop.start()
