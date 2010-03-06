import unittest

dictionary = """
ATTRIBUTE	User-Name		1	string
ATTRIBUTE	User-Password		2	string encrypt=1
"""

class TrivialObject:
    """dummy object"""

class RadiusMiddlewareTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.who.plugins.authradius import RadiusPlugin
        return RadiusPlugin

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_implements(self):
        from repoze.who.interfaces import IAuthenticator
        from zope.interface.verify import verifyClass
        klass = self._getTargetClass()
        verifyClass(IAuthenticator, klass)

    def test_null_login_ok(self):
        server = NullServer(True)
        s = self._makeOne(server)
        environ = {}
        identity = {'login': 'user', 'password': 'password'}
        result = s.authenticate(environ, identity)
        self.assertEqual(result, 'user')

    def test_null_login_bad(self):
        server = NullServer(False)
        s = self._makeOne(server)
        environ = {}
        identity = {'login': 'user', 'password': 'password'}
        result = s.authenticate(environ, identity)
        self.assertEqual(result, None)

class RadiusServerTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.who.plugins.authradius import Server
        return Server

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_getServer(self):
        server = self._makeOne('localhost', 61812, 'secret', timeout=42)
        self.assertEqual(server.host, 'localhost')
        self.assertEqual(server.authport, 61812)
        self.assertEqual(server.secret, 'secret')
        self.assertEqual(server.timeout, 42)

    def test_server_down(self):
        from pyrad.client import Timeout
        server = self._makeOne('localhost', 61812, 'secret', timeout=0.2)
        self.assertRaises(Timeout, server.authenticate, 'user', 'password')        

    def test_server_accept(self):
        from pyrad.packet import AccessRequest
        server = ServerAccept()
        client_pkt = TrivialObject()
        client_pkt.code=AccessRequest
        client_pkt.source=("host", "port")
        result = server._HandleAuthPacket(client_pkt)
        self.assertEqual(result, None)

    def test_server_deny(self):
        from pyrad.packet import AccessRequest
        from pyrad.server import ServerPacketError
        server = ServerDeny()
        client_pkt = TrivialObject()
        client_pkt.code=AccessRequest
        client_pkt.source=("host", "port")
        self.assertRaises(ServerPacketError, server._HandleAuthPacket, client_pkt)

from pyrad.server import Server


class NullServer(object):
    def __init__(self, result):
        self.result = result

    def authenticate(self, username, password):
        return self.result

class ServerWithRemoteHost(Server):
    """Subclass Server and create a remote host that can talk to us.
    The server does actually bind to its sockets so avoid standard ports.
    """
    def __init__(self, addresses=[], authport=1812, acctport=1813, hosts=None, dict=None):
        from StringIO import StringIO
        from pyrad.server import RemoteHost
        from pyrad.dictionary import Dictionary
        remotehost = RemoteHost("127.0.0.1", "secret", "host", authport=61812)
        Server.__init__(self,
                        addresses=["127.0.0.1"],
                        authport=61812,
                        acctport=61813,
                        hosts={"127.0.0.1": remotehost},
                        dict=Dictionary(StringIO(dictionary)))
        self.hosts["host"] = TrivialObject()
        self.hosts["host"].secret = "secretBAD"

class ServerAccept(ServerWithRemoteHost):
    """Always act like we accept the packet
    This doesn't decode or check any secret and password.
    """
    def HandleAuthPacket(self, pkt):
        pass

class ServerDeny(ServerWithRemoteHost):
    """Always act like we deny the authentication request.
    This doesn't decode or check any secret or password.
    """
    def HandleAuthPacket(self, pkt):
        from pyrad.server import ServerPacketError
        raise ServerPacketError, "Authentication denied."
