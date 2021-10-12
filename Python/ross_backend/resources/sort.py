from flask_restful import Resource, reqparse
from models.config import ConfigSortModel
from resources.funcs.sorting import startSorting
from flask_jwt_extended import jwt_required, get_jwt_identity
import io
import numpy as np


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
    parser.add_argument('sorting_type', type=str, choices=('t dist', 'skew-t dist', 'GMM', 'K-means', 'template matching'), required=True)
    parser.add_argument('max_iter', type=int, required=True)
    parser.add_argument('alignment', type=bool, required=True)
    parser.add_argument('filtering', type=bool, required=True)

    parser.add_argument('run_sorting', type=bool, default=False)

    @jwt_required
    def get(self):
        user_id = get_jwt_identity() 
        config = ConfigSortModel.find_by_user_id(user_id)
        if config:
            return config.json()
        return {'message': 'Sort config does not exist'}, 404

    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        if ConfigSortModel.find_by_user_id(user_id):
            return {'message': "Sorting config already exists."}, 400

        data = SortDefault.parser.parse_args()


        config = ConfigSortModel(user_id, **data)

        try:
            config.save_to_db()
        except:
            return {"message": "An error occurred inserting sorting config."}, 500

        if data['run_sorting']:
            try:
                print('starting Sorting ...')
                startSorting(user_id)
            except:
                return {"message": "An error occurred in sorting."}, 500

        return config.json(), 201

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
        print(data)
        user_id = get_jwt_identity()
        config = ConfigSortModel.find_by_user_id(user_id)
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
                return {"message": "An error occurred inserting sorting config."}, 500


        else:
            config = ConfigSortModel(user_id, **data)
            try:
                config.save_to_db()
            except:
                return {"message": "An error occurred inserting sort config."}, 500

        if data['run_sorting']:
            # try:



            print('Starting Sorting ...')
            spikeMat, spikeTime = startSorting(user_id)
            # buffer = io.BytesIO()
            # np.savez_compressed(buffer, spike_mat=spikeMat, spike_time=spikeTime)
            # buffer.seek(0)
            # raw_bytes = buffer.read()
            # buffer.close()
            # detectResult = SortResultModel(user_id, raw_bytes)
            # try:
            #     detectResult.save_to_db()
            # except:
            #     return {"message": "An error occurred inserting sorting result."}, 500



            # except:
            #     return {"message": "An error occurred in sorting."}, 500

        return config.json(), 201