import concurrent.futures

import tornado.ioloop
import tornado.websocket
import tornado.gen
import tornado.web
import os.path
import threading
import time

thread_pool = concurrent.futures.ThreadPoolExecutor()


def slowly_compute_sum(n):
    sum = 0
    for i in range(n):
        time.sleep(0.1)
        print("thread %s: worked %s of %s" % (id(threading.current_thread()), i + 1, n))
        sum += i + 1
    return dict(sum=sum)


# noinspection PyAbstractClass
class SumWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, n):
        future = thread_pool.submit(slowly_compute_sum, int(n))
        future.add_done_callback(lambda f: self.write_message(str(f.result())))

    def on_close(self):
        print("WebSocket closed")


# noinspection PyAbstractClass
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


# noinspection PyAbstractClass
class SumHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, n):
        future = thread_pool.submit(slowly_compute_sum, int(n))
        yield future
        self.write(future.result())


def make_app():
    settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))

    return tornado.web.Application([
        ("/", MainHandler),
        ("/sum/ws", SumWebSocketHandler),
        ("/sum/([0-9]+)", SumHandler),
        ("/(favicon\.ico)",
         tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
    ], **settings)


def main():
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
