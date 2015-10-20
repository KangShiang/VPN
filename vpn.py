from twisted.python.failure import Failure

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.error import CannotListenError
from twisted.conch.recvline import HistoricRecvLine
from twisted.conch.stdio import runWithProtocol

class ConsolePrompter(HistoricRecvLine, object):
    ps = [">>: "]

    def __init__(self, multiEcho):
        self.multiEcho = multiEcho

    def encrypt(self,inputstr):
        return inputstr
    
    def decrypt(self,inputstr):
        return inputstr
    
    def lineReceived(self, line):
        try:
            if not line:
                reactor.stop()
                if self.factory.kivyobj:
                    self.factory.kivyobj.apptools.get_running_app().stop()
            self.drawInputLine()
            line = self.encrypt(line)
            self.multiEcho.tellAllClients(line)
        except:
            f = Failure()
            data = f.getTraceback()
            self.terminal.write(data)

    def otherSaid(self, data):
        self.terminal.write("\r")
        self.terminal.eraseLine()
        data = self.decrypt(repr(data))
        self.terminal.write("Other Said:" + data)
        self.terminal.write("\n")
        self.drawInputLine()

class ChatServer(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def handle_first_out(self, var=None):
        # Here you can use self.factory.infostore (a dict)
        # to add info about this connection (if you wish)
        # or use the function to send something to the client
        # :param var: optional can pass anything
        if var!=None:
            # do something with var
            pass
        pass

    def handle_first_in(self, data):
        # Here you can use self.factory.infostore (a dict)
        # to add info about this connection (if you wish)
        pass

    def connectionMade(self):
        if self.factory.echoers.__len__() < self.factory.connectionLimit:
            self.factory.echoers.append(self)
            # Mark that we haven't received anything on self
            self.factory.statuses[self] = False
            self.factory.infostore[self] = {}
            # Can send something out
            self.handle_first_out()
        else:
            # Reject extra connections
            self.transport.loseConnection()

    def dataReceived(self, data):
        if self.factory.statuses[self] == False:
            self.handle_first_in(data)
            self.factory.statuses[self] = True
        else:
            self.factory.prompter.otherSaid(data)

    def connectionLost(self, reason):
        if self in self.factory.echoers:
            self.factory.echoers.remove(self)
            # Mark that we haven't received anything on self
            del self.factory.statuses[self]
            del self.factory.infostore[self]
        # Close the program when all client shuts down
        if self.factory.echoers.__len__() == 0:
            reactor.stop()
            if self.factory.kivyobj:
                self.factory.kivyobj.apptools.get_running_app().stop()

class ChatServerFactory(Factory):
    def __init__(self):
        self.echoers = []
        self.statuses = {}
        self.infostore = {}
        # allow connection to just one server
        self.connectionLimit = 1
        self.prompter = ConsolePrompter(self)

    def buildProtocol(self, addr):
        return ChatServer(self)

    def tellAllClients(self, message):
        for echoer in self.echoers:
            echoer.transport.write(message + "\r\n")

class ChatClient(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def handle_first_out(self,var=None):
        # Here you can use self.factory.infostore (a dict)
        # to add info about this connection (if you wish)
        # or use the function to send something to the client
        # :param var: optional can pass anything
        if var!=None:
            # do something with var
            pass
        pass

    def handle_first_in(self, data):
        # Here you can use self.factory.infostore (a dict)
        # to add info about this connection (if you wish)
        pass

    def connectionMade(self):
        self.factory.echoers.append(self)
        # Mark that we haven't received anything on self
        self.factory.statuses[self] = False
        self.factory.infostore[self] = {}
        # Can send something out
        self.handle_first_out()

    def dataReceived(self, data):
        if self.factory.statuses[self] == False:
            self.handle_first_in(data)
            self.factory.statuses[self] = True
        else:
            self.factory.prompter.otherSaid(data)

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)
        # Close the program when the server shuts down
        reactor.stop()
        if self.factory.kivyobj:
            self.factory.kivyobj.apptools.get_running_app().stop()

class ChatClientFactory(ClientFactory):
    def __init__(self):
        self.echoers = []
        self.statuses = {}
        self.infostore = {}
        self.prompter = ConsolePrompter(self)

    def buildProtocol(self, addr):
        return ChatClient(self)

    def tellAllClients(self, message):
        for echoer in self.echoers:
            echoer.transport.write(message + "\r\n")

def start_server_client(kivyobj=None,reactor=None):
    #if not reactor:
    #    from twisted.internet import reactor
    try:
        # Create a server if possible
        fact = ChatServerFactory()
        fact.kivyobj = kivyobj
        reactor.listenTCP(8000, fact,interface='127.0.0.1')
    except CannotListenError:
        # else create a client
        fact = ChatClientFactory()
        fact.kivyobj = kivyobj
        reactor.connectTCP('127.0.0.1',8000, fact)

    runWithProtocol(lambda: fact.prompter)

if __name__ == "__main__":
    start_server_client()
