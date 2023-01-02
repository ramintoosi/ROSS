from db import db


class ConfigDetectionModel(db.Model):
    __tablename__ = 'config_detect'

    id = db.Column(db.Integer, primary_key=True)

    filter_type = db.Column(db.String)
    filter_order = db.Column(db.Integer)
    pass_freq = db.Column(db.Integer)
    stop_freq = db.Column(db.Integer)
    sampling_rate = db.Column(db.Integer)
    thr_method = db.Column(db.String)
    side_thr = db.Column(db.String)
    pre_thr = db.Column(db.Integer)
    post_thr = db.Column(db.Integer)
    dead_time = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))
    # project = db.relationship('ProjectModel', backref="config_detect")
    # user = db.relationship('UserModel', back_populates="config_detect")

    def __init__(self, user_id, filter_type="butter", filter_order=4, pass_freq=300, stop_freq=3000, sampling_rate=40000,
                 thr_method="median", side_thr="negative", pre_thr=40, post_thr=59, dead_time=20, run_detection=False,
                 project_id=0):
        self.user_id = user_id
        self.project_id = project_id

        self.filter_type = filter_type
        self.filter_order = filter_order
        self.pass_freq = pass_freq
        self.stop_freq = stop_freq
        self.sampling_rate = sampling_rate
        self.thr_method = thr_method
        self.side_thr = side_thr
        self.pre_thr = pre_thr
        self.post_thr = post_thr
        self.dead_time = dead_time
        self.run_detection = run_detection

    def json(self):
        return {'filter_type': self.filter_type, 'filter_order': self.filter_order, 'pass_freq': self.pass_freq,
                'stop_freq': self.stop_freq, 'sampling_rate': self.sampling_rate, 'thr_method': self.thr_method,
                'side_thr': self.side_thr, 'pre_thr': self.pre_thr, 'post_thr': self.post_thr,
                'dead_time': self.dead_time}

    def save_to_db(self):
        # update or insert
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls):
        return cls.query.first()

    # @classmethod
    # def find_by_user_id(cls, _id):
    #     return cls.query.filter_by(user_id=_id).first()

    @classmethod
    def find_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class ConfigSortModel(db.Model):
    __tablename__ = 'config_sort'

    id = db.Column(db.Integer, primary_key=True)

    # settings for alignment
    max_shift = db.Column(db.Integer)
    histogram_bins = db.Column(db.Integer)
    num_peaks = db.Column(db.Integer)
    compare_mode = db.Column(db.String)

    # settings for filtering
    max_std = db.Column(db.Float)
    max_mean = db.Column(db.Float)
    max_outliers = db.Column(db.Float)

    # settings for sorting
    nu = db.Column(db.Float)
    PCA_num = db.Column(db.Integer)
    g_max = db.Column(db.Integer)
    g_min = db.Column(db.Integer)
    u_lim = db.Column(db.Float)
    error = db.Column(db.Float)
    tol = db.Column(db.Float)
    N = db.Column(db.Integer)
    matching_mode = db.Column(db.String)
    alpha = db.Column(db.Float)
    combination = db.Column(db.Boolean)
    custom_template = db.Column(db.Boolean)
    sorting_type = db.Column(db.String)
    max_iter = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))

    alignment = db.Column(db.Boolean)
    filtering = db.Column(db.Boolean)

    def __init__(self, user_id, max_shift=10, histogram_bins=75, num_peaks=3, compare_mode='index', max_std=3,
                 max_mean=1, max_outliers=5, nu=20, PCA_num=15, g_max=9, g_min=1, u_lim=0.01, error=0.1, tol=0.01, N=15,
                 matching_mode='Euclidean',alpha=0.01, combination=False, custom_template=False, sorting_type='t dist',
                 max_iter=500, run_sorting=False, project_id=0, alignment=True, filtering=True):

        self.project_id = project_id
        self.user_id = user_id

        # alignment settings
        self.max_shift = max_shift
        self.histogram_bins = histogram_bins
        self.num_peaks = num_peaks
        self.compare_mode = compare_mode

        # filtering settings
        self.max_std = max_std
        self.max_mean = max_mean
        self.max_outliers = max_outliers

        # sorting settings
        self.nu = nu
        self.PCA_num = PCA_num
        self.g_max = g_max
        self.g_min = g_min
        self.u_lim = u_lim
        self.error = error
        self.tol = tol
        self.N = N
        self.matching_mode = matching_mode
        self.alpha = alpha
        self.combination = combination
        self.custom_template = custom_template
        self.sorting_type = sorting_type
        self.max_iter = 500

        self.alignment = alignment
        self.filtering = filtering
        self.max_iter = max_iter
        self.run_sorting = run_sorting

    def json(self):
        return {'max_shift': self.max_shift, 'histogram_bins': self.histogram_bins, 'num_peaks': self.num_peaks,
                'compare_mode': self.compare_mode, 'max_std': self.max_std, 'max_mean': self.max_mean,
                'max_outliers': self.max_outliers, 'nu': self.nu, 'PCA_num': self.PCA_num, 'g_max':self.g_max,
                'g_min': self.g_min, 'u_lim': self.u_lim, 'error': self.error, 'tol': self.tol, 'N': self.N,
                'matching_mode': self.matching_mode, 'alpha': self.alpha, 'combination': self.combination,
                'custom_templates': self.custom_template, 'sorting_type': self.sorting_type, 'max_iter': self.max_iter,
                'alignment': self.alignment, 'filtering': self.filtering}

    def save_to_db(self):
        # update or insert
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls):
        return cls.query.first()

    # @classmethod
    # def find_by_user_id(cls, _id):
    #     return cls.query.filter_by(user_id=_id, project_id=0).first()

    @classmethod
    def find_by_project_id(cls,project_id):
        return cls.query.filter_by(project_id=project_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
