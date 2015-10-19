from twisted.python.failure import Failure

from twisted.internet import reactor
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

    def connectionMade(self):
        if self.factory.echoers.__len__() < self.factory.connectionLimit:
            self.factory.echoers.append(self)
        else:
            # Reject extra connections
            self.transport.loseConnection()

    def dataReceived(self, data):
        self.factory.prompter.otherSaid(data)

    def connectionLost(self, reason):
        if self in self.factory.echoers:
            self.factory.echoers.remove(self)
        # Close the program when all client shuts down
        if self.factory.echoers.__len__() == 0:
            reactor.stop()

class ChatServerFactory(Factory):
    def __init__(self):
        self.echoers = []
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

    def connectionMade(self):
        self.factory.echoers.append(self)

    def dataReceived(self, data):
        self.factory.prompter.otherSaid(data)

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)
        # Close the program when the server shuts down
        reactor.stop()

class ChatClientFactory(ClientFactory):
    def __init__(self):
        self.echoers = []
        self.prompter = ConsolePrompter(self)

    def buildProtocol(self, addr):
        return ChatClient(self)

    def tellAllClients(self, message):
        for echoer in self.echoers:
            echoer.transport.write(message + "\r\n")

try:
    # Create a server if possible
    fact = ChatServerFactory()
    reactor.listenTCP(8000, fact,interface='127.0.0.1')
except CannotListenError:
    # else create a client
    fact = ChatClientFactory()
    reactor.connectTCP('127.0.0.1',8000, fact)

runWithProtocol(lambda: fact.prompter)
