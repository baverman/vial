from threading import Thread
from vial.ipc import Server, Client, Connection, arbitrary_address, Listener

def test_flow():
    class Boo(Server):
        def add(self, a, b):
            return a + b

    def run(address):
        server = Boo(Listener(address).accept())
        server.run()

    address = arbitrary_address()
    Thread(target=run, args=(address,)).start()

    cl = Client(Connection(address))
    result = cl.add(1, 2)
    assert result == 3

    result = cl.add('1', '2')
    assert result == '12'

    try:
        cl.add(1, None)
        assert False
    except Exception as e:
        assert e.message[0] == 'TypeError'

    cl.close()