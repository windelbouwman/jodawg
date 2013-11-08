import sys
import time
from PyQt5.QtCore import QSocketNotifier, QTimer, QCoreApplication
import zmq
from multiprocessing import Process

def xMitter():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.bind('tcp://*:5677')
    for i in range(20):
        msg = 'hello world {}'.format(i)
        print('xmit:', msg)
        sock.send(msg.encode('ascii'))
        time.sleep(0.1)

if __name__ == '__main__':
    p = Process(target=xMitter)
    p.start()
    try:
        ctx = zmq.Context()
        sock = ctx.socket(zmq.SUB)
        sock.connect('tcp://localhost:5677')
        sock.setsockopt(zmq.SUBSCRIBE, bytes()) # Get all!
        app = QCoreApplication(sys.argv)
        t = QTimer()
        t.timeout.connect(app.quit)
        t.start(3000)  # Quit app after 3 seconds.
        fd = sock.getsockopt(zmq.FD)
        sn = QSocketNotifier(fd, QSocketNotifier.Read)
        def gotMsg(sock_fd):
            msg = sock.recv()
            print('rcv:', msg)
        sn.activated.connect(gotMsg)
        app.exec()
    finally:
        p.terminate()
        p.join()


