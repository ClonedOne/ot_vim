import json
import socket

class Document:
    def __init__(self, name, port, replicas):
        self.name = name
        self.replicas = set(replicas)
        self.collabs = set()
        self.ip = ''
        self.port = port

        for r in replicas:
            self._activate_replica(r)

        return

    def open(self, pid):
        if 0 == len(self.collabs):
            # TODO load balance, pick worker to launch on
            self.ip = self.replicas[0]

        self.collabs.add(pid)

        return self.ip, self.port

    def close(self, pid):
        self.collabs.remove(pid)

        if 0 == len(self.collabs):
            self.ip = ''

        return

    def _activate_replica(self, replica):
        """
        Connect to document server at replica and tell
        it to start the server for this document at
        this port.
        """
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((replica, 4444))

        msg = dict()
        msg['op'] = 'ACTIVATE'
        msg['docfn'] = self.name
        msg['ip'] = replica
        msg['port'] = self.port
        msg['reps'] = self.replicas

        sk.send(json.dumps(msg))

        sk.close()

        return
