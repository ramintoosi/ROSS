from view.detectedMatSelect import Detected_Mat_Dialog


class DetectedMatSelectApp(Detected_Mat_Dialog):
    def __init__(self, variables):
        super(DetectedMatSelectApp, self).__init__(variables)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
