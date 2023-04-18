from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from models.config import ConfigDetectionModel, ConfigSortModel
from models.data import RawModel
from models.project import ProjectModel


class Project(Resource):

    @jwt_required
    def get(self, name):  # for loading project as default project
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if proj:
            # copy project to default project
            raw_proj = proj.raw
            # RawModel.find_by_project_id(user_id=user_id, project_id=proj.id)
            # if raw_proj:
            raw_default = RawModel.find_by_user_id(user_id)
            if raw_default:
                raw_default.data = raw_proj.data
            else:
                raw_default = RawModel(user_id=user_id, data=raw_proj.data, project_id=0)
            # else:
            #     raw_default = RawModel(user_id = user_id, data = None, project_id=0)
            try:
                raw_default.save_to_db()
            except:
                return {"message": "An error occurred loading project."}, 500

            config_detect_proj = proj.config_detect
            # ConfigDetectionModel.find_by_project_id(user_id=user_id, project_id=proj.id)
            config_detect_default = ConfigDetectionModel.find_by_user_id(user_id)
            if config_detect_default:
                config_detect_default.filter_type = config_detect_proj.filter_type
                config_detect_default.filter_order = config_detect_proj.filter_order
                config_detect_default.pass_freq = config_detect_proj.pass_freq
                config_detect_default.stop_freq = config_detect_proj.stop_freq
                config_detect_default.sampling_rate = config_detect_proj.sampling_rate
                config_detect_default.thr_method = config_detect_proj.thr_method
                config_detect_default.side_thr = config_detect_proj.side_thr
                config_detect_default.pre_thr = config_detect_proj.pre_thr
                config_detect_default.post_thr = config_detect_proj.post_thr
                config_detect_default.dead_time = config_detect_proj.dead_time
            else:
                config_detect_default = ConfigDetectionModel(user_id=user_id, project_id=0,
                                                             filter_type=config_detect_proj.filter_type,
                                                             filter_order=config_detect_proj.filter_order,
                                                             pass_freq=config_detect_proj.pass_freq,
                                                             stop_freq=config_detect_proj.stop_freq,
                                                             sampling_rate=config_detect_proj.sampling_rate,
                                                             thr_method=config_detect_proj.thr_method,
                                                             side_thr=config_detect_proj.side_thr,
                                                             pre_thr=config_detect_proj.pre_thr,
                                                             post_thr=config_detect_proj.post_thr,
                                                             dead_time=config_detect_proj.dead_time)
            try:
                config_detect_default.save_to_db()
            except:
                return {"message": "An error occurred loading project."}, 500

            config_sort_proj = proj.config_sort
            config_sort_default = ConfigSortModel.find_by_user_id(user_id)
            if config_sort_default:
                config_sort_default.filter_type = config_sort_proj.filter_type
                config_sort_default.filter_order = config_sort_proj.filter_order
                config_sort_default.pass_freq = config_sort_proj.pass_freq
                config_sort_default.stop_freq = config_sort_proj.stop_freq
                config_sort_default.sampling_rate = config_sort_proj.sampling_rate
                config_sort_default.thr_method = config_sort_proj.thr_method
                config_sort_default.side_thr = config_sort_proj.side_thr
                config_sort_default.pre_thr = config_sort_proj.pre_thr
                config_sort_default.post_thr = config_sort_proj.post_thr
                config_sort_default.dead_time = config_sort_proj.dead_time
            else:
                config_sort_default = ConfigSortModel(user_id=user_id, project_id=0,
                                                      max_shift=config_sort_proj.max_shift,
                                                      histogram_bins=config_sort_proj.histogram_bins,
                                                      num_peaks=config_sort_proj.histogram_bins,
                                                      compare_mode=config_sort_proj.compare_mode,
                                                      max_std=config_sort_proj.max_std,
                                                      max_mean=config_sort_proj.max_mean,
                                                      max_outliers=config_sort_proj.max_outliers,
                                                      nu=config_sort_proj.nu, PCA_num=config_sort_proj.PCA_num,
                                                      g_max=config_sort_proj.g_max, g_min=config_sort_proj.g_min,
                                                      u_lim=config_sort_proj.u_lim, error=config_sort_proj.u_lim,
                                                      tol=config_sort_proj.tol, N=config_sort_proj.N,
                                                      matching_mode=config_sort_proj.matching_mode,
                                                      alpha=config_sort_proj.alpha,
                                                      combination=config_sort_proj.combination,
                                                      custom_template=config_sort_proj.custom_template,
                                                      sorting_type=config_sort_proj.sorting_type,
                                                      max_iter=config_sort_proj.max_iter)
            try:
                config_sort_default.save_to_db()
            except:
                return {"message": "An error occurred loading project."}, 500

            return proj.json(), 201

        return {'message': 'Project does not exist'}, 404

    @jwt_required
    def post(self, name):
        user_id = get_jwt_identity()
        if ProjectModel.find_by_project_name(user_id, name):
            return {'message': "Project with this name already exists."}, 400

        default_project = ProjectModel.find_by_user_id(user_id)
        proj = ProjectModel(user_id, name, isDefault=False)

        try:
            proj.save_to_db()
        except:
            return {"message": "An error occurred inserting project."}, 500
        # copying default raw data
        raw_default = RawModel.find_by_project_id(user_id=user_id, project_id=0)
        if raw_default:
            raw = RawModel(user_id=user_id, data=raw_default.data, project_id=proj.id)
        else:
            raw = RawModel(user_id=user_id, data=None, project_id=proj.id)
        try:
            raw.save_to_db()
        except:
            return {"message": "An error occurred inserting project."}, 500

        # copying detection config
        config_detect_default = ConfigDetectionModel.find_by_project_id(user_id=user_id, project_id=0)
        if config_detect_default:
            config = ConfigDetectionModel(user_id=user_id, project_id=proj.id,
                                          filter_type=config_detect_default.filter_type,
                                          filter_order=config_detect_default.filter_order,
                                          pass_freq=config_detect_default.pass_freq,
                                          stop_freq=config_detect_default.stop_freq,
                                          sampling_rate=config_detect_default.sampling_rate,
                                          thr_method=config_detect_default.thr_method,
                                          side_thr=config_detect_default.side_thr,
                                          pre_thr=config_detect_default.pre_thr,
                                          post_thr=config_detect_default.post_thr,
                                          dead_time=config_detect_default.dead_time)
            # config = copy.deepcopy(config_detect_default)
            config.project_id = proj.id
        else:
            config = ConfigDetectionModel(user_id=user_id)
            # config.project_id = proj.id
        try:
            config.save_to_db()
        except:
            return {"message": "An error occurred inserting project."}, 500

        # copying sort config
        config_sort_default = ConfigSortModel.find_by_project_id(user_id=user_id, project_id=0)
        if config_sort_default:
            config = ConfigSortModel(user_id=user_id, project_id=proj.id, max_shift=config_sort_default.max_shift,
                                     histogram_bins=config_sort_default.histogram_bins,
                                     num_peaks=config_sort_default.num_peaks,
                                     compare_mode=config_sort_default.compare_mode, max_std=config_sort_default.max_std,
                                     max_mean=config_sort_default.max_mean,
                                     max_outliers=config_sort_default.max_outliers,
                                     nu=config_sort_default.nu, PCA_num=config_sort_default.PCA_num,
                                     g_max=config_sort_default.g_max, g_min=config_sort_default.g_min,
                                     u_lim=config_sort_default.u_lim, error=config_sort_default.error,
                                     tol=config_sort_default.tol, N=config_sort_default.N,
                                     matching_mode=config_sort_default.matching_mode, alpha=config_sort_default.alpha,
                                     combination=config_sort_default.combination,
                                     custom_template=config_sort_default.custom_template,
                                     sorting_type=config_sort_default.sorting_type,
                                     max_iter=config_sort_default.max_iter, run_sorting=config_sort_default.run_sorting,
                                     alignment=config_sort_default.alignment, filtering=config_sort_default.filtering)
            # config = copy.deepcopy(config_detect_default)
            # config.project_id = proj.id
        else:
            config = ConfigSortModel(user_id=user_id)
            config.project_id = proj.id
        try:
            config.save_to_db()
        except:
            return {"message": "An error occurred inserting project."}, 500

        return proj.json(), 201

    @jwt_required
    def delete(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if proj:
            proj.delete_from_db()
            return {'message': 'Project deleted.'}
        return {'message': 'Project does not exist.'}, 404

    @jwt_required
    def put(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': "Project with this name does not exist."}, 400

        default_project = ProjectModel.find_by_user_id(user_id)
        raw_default = RawModel.find_by_project_id(user_id=user_id, project_id=0)
        raw = RawModel.find_by_project_id(user_id=user_id, project_id=proj.id)
        if raw_default:
            # if raw:
            #     raw.data = raw_default.data
            # else:
            raw = RawModel(user_id=user_id, data=raw_default.data, project_id=proj.id)

            try:
                raw.save_to_db()
            except:
                return {"message": "An error occurred inserting project."}, 500

        # copying detection config
        config_detect_default = ConfigDetectionModel.find_by_project_id(user_id=user_id, project_id=0)
        if config_detect_default:
            config = ConfigDetectionModel(user_id=user_id, project_id=proj.id,
                                          filter_type=config_detect_default.filter_type,
                                          filter_order=config_detect_default.filter_order,
                                          pass_freq=config_detect_default.pass_freq,
                                          stop_freq=config_detect_default.stop_freq,
                                          sampling_rate=config_detect_default.sampling_rate,
                                          thr_method=config_detect_default.thr_method,
                                          side_thr=config_detect_default.side_thr,
                                          pre_thr=config_detect_default.pre_thr,
                                          post_thr=config_detect_default.post_thr,
                                          dead_time=config_detect_default.dead_time)
            # config = copy.deepcopy(config_detect_default)
            config.project_id = proj.id
            try:
                config.save_to_db()
            except:
                return {"message": "An error occurred inserting project."}, 500

        return proj.json(), 201


class Projects(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        proj = ProjectModel.get_all_by_user_id(user_id)
        if proj:
            return proj

        return {'message': 'Project does not exist'}, 404
