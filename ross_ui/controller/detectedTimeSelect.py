from view.detectedTimeSelect import Detected_Time_Dialog


class DetectedTimeSelectApp(Detected_Time_Dialog):
    def __init__(self, variables):
        super(DetectedTimeSelectApp, self).__init__(variables)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
