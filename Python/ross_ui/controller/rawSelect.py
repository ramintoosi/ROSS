from view.rawSelect import Raw_Dialog

class RawSelectApp(Raw_Dialog):
    def __init__(self, variables):
        super(RawSelectApp, self).__init__(variables)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)