from zope.interface import implements
from repoze.who.interfaces import IAuthenticator

class RadiusPlugin(object):

    implements(IAuthenticator)

    def __init__(self, server):
        self.server = server

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None
        if self.server.authenticate(login, password):
            return login
        return None

class Server(object):
    """A RADIUS server has host, authport, shared secret.
    The host can be an DNS name or IP address,
    authport is (UDP) typically 1812 or 1845;
    shared secret is a string the server keeps for this client.
    Optional timeout is jammed into server to speed testing.
    """
    def __init__(self, host, authport, secret, timeout=None):
        self.host     = host
        self.authport = authport
        self.secret   = secret
        self.timeout  = timeout

    def authenticate(self, username, password):
        """Return True or False per the RADIUS server's response.
        TODO: Do we need to worry about realms like chris@realmname
        and different realm separators?
        Different username versus login name?
        """
        from StringIO import StringIO
        import pyrad.packet
        from pyrad.client import Client
        from pyrad.dictionary import Dictionary
        dictionary = """
ATTRIBUTE	User-Name		1	string
ATTRIBUTE	User-Password		2	string encrypt=1
"""
        client = Client(server=self.host,
                     authport=self.authport,
                     secret=self.secret,
                     dict=Dictionary(StringIO(dictionary)),
                     )
        if self.timeout:
            client.timeout = self.timeout # pyrad init has no way to set
        req = client.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                                      User_Name=username)
        req["User-Password"] = req.PwCrypt(password)
        reply = client.SendPacket(req)
        if reply.code == pyrad.packet.AccessAccept:
            # don't save reply since we don't have full dictionary to decode it
            return True
        return False

def make_plugin(host=None,
                authport=None,
                secret=None,
                timeout=None):

    if host is None:
        raise ValueError('host must not be None')
    if authport is None:
        raise ValueError('authport must not be None')
    if secret is None:
        raise ValueError('secret must not be None')


    return RadiusPlugin(Server(host, int(authport), secret, int(timeout)))


def make_test_middleware(app, global_conf):
    # be able to test without a config file
    import sys
    import os
    import logging
    from repoze.who.plugins.form import FormPlugin
    from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
    from repoze.who.middleware import PluggableAuthenticationMiddleware
    from repoze.who.classifiers import default_request_classifier
    from repoze.who.classifiers import default_challenge_decider

    form           = FormPlugin('__do_login', rememberer_name='auth_tkt')
    auth_tkt       = AuthTktCookiePlugin('secret squirrel',
                                         cookie_name='test_auth_tkt',
                                         include_ip=True)
    identifiers    = [('form', form), ('auth_tkt', auth_tkt)]
    server         = Server('localhost', 1812, 'testing123')
    radiusplugin   = RadiusPlugin(server)
    authenticators = [('radius', radiusplugin)]
    mdproviders    = []                 # I don't know what this is
    challengers    = [('form', form) ]
    log_stream     = sys.stdout
    if os.environ.get('NO_WHO_LOG'):
        log_stream = None
    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream = log_stream,
        log_level = logging.DEBUG,       # default=INFO, should be configable
        remote_user_key = 'REMOTE_USER',
        )
    return middleware

