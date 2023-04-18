import pickle
import traceback
from uuid import uuid4
from pathlib import Path

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, request
from models.config import ConfigSortModel
from models.data import SortResultModel, RawModel
from models.project import ProjectModel
from models.user import UserModel
from resources.funcs.sorting import startSorting, startReSorting


class Sort(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)

    # alignment settings
    parser.add_argument('max_shift', type=int, required=True)
    parser.add_argument('histogram_bins', type=int, required=True)
    parser.add_argument('num_peaks', type=int, required=True)
    parser.add_argument('compare_mode', type=str, required=True, choices=('magnitude', 'index'))

    # filtering settings
    parser.add_argument('max_std', type=float, required=True)
    parser.add_argument('max_mean', type=float, required=True)
    parser.add_argument('max_outliers', type=float, required=True)

    # sort settings
    parser.add_argument('nu', type=float, required=True)
    parser.add_argument('max_iter', type=int, required=True)
    parser.add_argument('PCA_num', type=int, required=True)
    parser.add_argument('g_max', type=int, required=True)
    parser.add_argument('g_min', type=int, required=True)
    parser.add_argument('u_lim', type=float, required=True)
    parser.add_argument('error', type=float, required=True)
    parser.add_argument('tol', type=float, required=True)
    parser.add_argument('N', type=int, required=True)
    parser.add_argument('matching_mode', type=str, required=True, choices=('Euclidean', 'Chi_squared', 'Correlation'))
    parser.add_argument('alpha', type=float, required=True)
    parser.add_argument('combination', type=bool, required=True)
    parser.add_argument('custom_template', type=bool, required=True)
    parser.add_argument('sorting_type', type=str,
                        choices=('t dist', 'skew-t dist', 'GMM', 'K-means', 'template matching'), required=True)
    parser.add_argument('max_iter', type=int, required=True)
    parser.add_argument('alignment', type=bool, required=True)
    parser.add_argument('filtering', type=bool, required=True)
    parser.add_argument('run_sorting', type=bool, default=False)

    @jwt_required
    def get(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        config = proj.config
        if config:
            return config.json()
        return {'message': 'Detection config does not exist'}, 404

    @jwt_required
    def post(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        config = proj.config
        if config:
            return {'message': "Config Detection already exists."}, 400

        data = Sort.parser.parse_args()

        config = ConfigSortModel(user_id, **data, project_id=proj.id)

        try:
            config.save_to_db()
        except:
            return {"message": "An error occurred inserting detection config."}, 500

        # if data['run_detection']:
        #     try:
        #         print('starting Detection ...')
        #         startDetection()
        #     except:
        #         return {"message": "An error occurred in detection."}, 500

        return config.json(), 201

    @jwt_required
    def delete(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        config = proj.config
        if config:
            config.delete_from_db()
            return {'message': 'Detection config deleted.'}
        return {'message': 'Detection config does not exist.'}, 404

    @jwt_required
    def put(self, name):
        data = Sort.parser.parse_args()
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        config = proj.config
        if config:
            for key in data:
                config.key = data[key]
            try:
                config.save_to_db()
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting detection config."}, 500

            return config.json(), 201

        else:
            config = ConfigSortModel(user_id, **data, project_id=proj.id)

            try:
                config.save_to_db()
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting detection config."}, 500

            return config.json(), 201


class SortDefault(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)

    # alignment settings
    parser.add_argument('max_shift', type=int, required=True)
    parser.add_argument('histogram_bins', type=int, required=True)
    parser.add_argument('num_peaks', type=int, required=True)
    parser.add_argument('compare_mode', type=str, required=True, choices=('magnitude', 'index'))

    # filtering settings
    parser.add_argument('max_std', type=float, required=True)
    parser.add_argument('max_mean', type=float, required=True)
    parser.add_argument('max_outliers', type=float, required=True)

    # sort settings
    parser.add_argument('nu', type=float, required=True)
    parser.add_argument('max_iter', type=int, required=True)
    parser.add_argument('PCA_num', type=int, required=True)
    parser.add_argument('g_max', type=int, required=True)
    parser.add_argument('g_min', type=int, required=True)
    parser.add_argument('u_lim', type=float, required=True)
    parser.add_argument('error', type=float, required=True)
    parser.add_argument('tol', type=float, required=True)
    parser.add_argument('N', type=int, required=True)
    parser.add_argument('matching_mode', type=str, required=True, choices=('Euclidean', 'Chi_squared', 'Correlation'))
    parser.add_argument('alpha', type=float, required=True)
    parser.add_argument('combination', type=bool, required=True)
    parser.add_argument('custom_template', type=bool, required=True)
    parser.add_argument('sorting_type', type=str,
                        choices=('t dist', 'skew-t dist', 'GMM', 'K-means', 'template matching'), required=True)
    parser.add_argument('max_iter', type=int, required=True)
    parser.add_argument('alignment', type=bool, required=True)
    parser.add_argument('filtering', type=bool, required=True)

    parser.add_argument('run_sorting', type=bool, default=False)

    # -------------------------------------------------------------
    parser.add_argument('project_id', type=int, required=True)
    parser.add_argument('clusters', type=list, default=None)
    parser.add_argument('selected_clusters', type=list, default=None)

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        project_id = request.form['project_id']
        user = UserModel.find_by_id(user_id)
        config = ConfigSortModel.find_by_project_id(project_id)
        if config:
            return config.json()
        return {'message': 'Sort config does not exist'}, 404

    @jwt_required
    def delete(self):
        user_id = get_jwt_identity()
        config = ConfigSortModel.find_by_user_id(user_id)
        if config:
            config.delete_from_db()
            return {'message': 'Sorting config deleted.'}
        return {'message': 'Sorting config does not exist.'}, 404

    @jwt_required
    def put(self):
        data = SortDefault.parser.parse_args()
        user_id = get_jwt_identity()
        project_id = data['project_id']

        if 'clusters' in data:
            clusters = data['clusters']
            selected_clusters = data['selected_clusters']
        else:
            clusters = None
            selected_clusters = None

        config = ConfigSortModel.find_by_project_id(project_id)
        if config:
            config.max_shift = data['max_shift']
            config.num_peaks = data['num_peaks']
            config.histogram_bins = data['histogram_bins']
            config.compare_mode = data['compare_mode']

            config.max_std = data['max_std']
            config.max_mean = data['max_mean']
            config.max_outliers = data['max_outliers']

            config.nu = data['nu']
            config.max_iter = data['max_iter']
            config.pca_num = data['PCA_num']
            config.g_max = data['g_max']
            config.g_min = data['g_min']
            config.u_lim = data['u_lim']
            config.error = data['error']
            config.tol = data['tol']
            config.N = data['N']
            config.matching_mode = data['matching_mode']
            config.alpha = data['alpha']
            config.custom_template = data['custom_template']
            config.sorting_type = data['sorting_type']
            config.alignment = data['alignment']
            config.filtering = data['filtering']

            try:
                config.save_to_db()
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting sorting config."}, 500

        else:
            config = ConfigSortModel(user_id, **data)
            try:
                config.save_to_db()
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting sort config."}, 500

        if data['run_sorting']:
            try:
                print('Starting Sorting ...')

                if clusters is not None:
                    clusters_index = startReSorting(project_id, clusters, selected_clusters)
                    return {'clusters': clusters_index}, 201
                else:
                    clusters_index = startSorting(project_id)

                    data = {"clusters": clusters_index}

                    sort_result_path = str(Path(RawModel.find_by_project_id(project_id).data).parent /
                                           (str(uuid4()) + '.pkl'))

                    with open(sort_result_path, 'wb') as f:
                        pickle.dump(data, f)

                    sortResult = SortResultModel.find_by_project_id(project_id)

                    if sortResult:
                        sortResult.data = sort_result_path
                    else:
                        sortResult = SortResultModel(user_id, sort_result_path, project_id)

                    try:
                        sortResult.save_to_db()
                    except:
                        print(traceback.format_exc())
                        return {"message": "An error occurred inserting sorting result."}, 500
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred in sorting."}, 500

        return config.json(), 201
