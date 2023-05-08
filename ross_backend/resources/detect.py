import pickle
import traceback
from pathlib import Path
from uuid import uuid4

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, request

from models.config import ConfigDetectionModel
from models.data import DetectResultModel
from models.data import RawModel
from resources.funcs.detection import startDetection
from resources.detection_result import SESSION


class DetectDefault(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('filter_type', type=str, required=True, choices='butterworth')
    parser.add_argument('filter_order', type=int, required=True)
    parser.add_argument('pass_freq', type=int, required=True)
    parser.add_argument('stop_freq', type=int, required=True)
    parser.add_argument('sampling_rate', type=int, required=True)
    parser.add_argument('thr_method', type=str, required=True, choices=('median', 'wavelet', 'plexon'))
    parser.add_argument('side_thr', type=str, required=True, choices=('positive', 'negative', 'two'))
    parser.add_argument('pre_thr', type=int, required=True)
    parser.add_argument('post_thr', type=int, required=True)
    parser.add_argument('dead_time', type=int, required=True)
    parser.add_argument('run_detection', type=bool, default=False)
    parser.add_argument('project_id', type=int, default=False)

    @jwt_required
    def get(self):
        project_id = request.form['project_id']
        config = ConfigDetectionModel.find_by_project_id(project_id)
        if config:
            return config.json()
        return {'message': 'Detection config does not exist'}, 404

    @jwt_required
    def post(self):
        data = DetectDefault.parser.parse_args()
        project_id = data['project_id']
        user_id = get_jwt_identity()
        config = ConfigDetectionModel.find_by_project_id(project_id)
        if config:
            config.filter_type = data['filter_type']
            config.filter_order = data['filter_order']
            config.pass_freq = data['pass_freq']
            config.stop_freq = data['stop_freq']
            config.sampling_rate = data['sampling_rate']
            config.thr_method = data['thr_method']
            config.side_thr = data['side_thr']
            config.pre_thr = data['pre_thr']
            config.post_thr = data['post_thr']
            config.dead_time = data['dead_time']
            config.run_detection = data['run_detection']
            try:
                config.save_to_db()
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting detection config."}, 500

        else:
            config = ConfigDetectionModel(user_id, **data)
            try:
                config.save_to_db()
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting detection config."}, 500
        # if data['run_detection']:
        try:

            spikeMat, spikeTime, pca_spikes, inds = startDetection(project_id)

            data_file = {'spikeMat': spikeMat, 'spikeTime': spikeTime,
                         'config': config.json(), 'pca_spikes': pca_spikes,
                         'inds': inds}
            # -------------------------------------------------------
            print("inserting detection result to database")

            detection_result_path = str(Path(RawModel.find_by_project_id(project_id).data).parent /
                                        (str(uuid4()) + '.pkl'))

            with open(detection_result_path, 'wb') as f:
                pickle.dump(data_file, f)

            detectResult = DetectResultModel.find_by_project_id(project_id)

            if detectResult:
                detectResult.data = detection_result_path
            else:
                detectResult = DetectResultModel(user_id, detection_result_path, project_id)

            try:
                detectResult.save_to_db()
                SESSION[project_id] = data_file
            except:
                print(traceback.format_exc())
                return {"message": "An error occurred inserting detection result."}, 500

        except:
            print(traceback.format_exc())
            return {"message": "An error occurred in detection."}, 500

        return "Success", 201
