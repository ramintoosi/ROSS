from view.projectSelect import Project_Dialog


class projectSelectApp(Project_Dialog):
    def __init__(self, projects):
        super(projectSelectApp, self).__init__(projects)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
