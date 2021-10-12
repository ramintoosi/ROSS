from view.serverAddress import Server_Dialog

class ServerApp(Server_Dialog):
    def __init__(self, server_text):
        super(ServerApp, self).__init__(server_text)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)