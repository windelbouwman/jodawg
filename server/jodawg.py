import tornado.ioloop
import tornado.options
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([(r"/", MainHandler)])
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
    