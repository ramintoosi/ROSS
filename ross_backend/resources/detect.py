import pickle
import traceback
from uuid import uuid4

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, request
from models.config import ConfigDetectionModel
from models.data import DetectResultModel
from models.project import ProjectModel
from resources.funcs.detection import startDetection


class Detect(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('filter_type', type=str, required=True, choices=('butter'))
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

        data = Detect.parser.parse_args()

        config = ConfigDetectionModel(user_id, **data, project_id=proj.id)

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
        data = Detect.parser.parse_args()
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
                return {"message": "An error occurred inserting detection config."}, 500

            return config.json(), 201

        else:
            config = ConfigDetectionModel(user_id, **data, project_id=proj.id)

            try:
                config.save_to_db()
            except:
                return {"message": "An error occurred inserting detection config."}, 500

            return config.json(), 201


class DetectDefault(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('filter_type', type=str, required=True, choices=('butterworth'))
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
    # --------------------------------------------
    parser.add_argument('project_id', type=int, default=False)

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        # user = UserModel.find_by_id(user_id)
        project_id = request.form['project_id']
        config = ConfigDetectionModel.find_by_project_id(project_id)
        if config:
            return config.json()
        return {'message': 'Detection config does not exist'}, 404

    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        if ConfigDetectionModel.find_by_user_id(user_id):
            return {'message': "Detection config already exists."}, 400

        data = Detect.parser.parse_args()
        config = ConfigDetectionModel(user_id, **data)

        try:
            config.save_to_db()
        except:
            return {"message": "An error occurred inserting detection config."}, 500

        if data['run_detection']:
            try:
                print('starting Detection ...')
                startDetection(user_id)
            except:
                return {"message": "An error occurred in detection."}, 500

        return config.json(), 201

    @jwt_required
    def delete(self):
        user_id = get_jwt_identity()
        config = ConfigDetectionModel.find_by_user_id(user_id)
        if config:
            config.delete_from_db()
            return {'message': 'Detection config deleted.'}
        return {'message': 'Detection config does not exist.'}, 404

    @jwt_required
    def put(self):
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
        if data['run_detection']:
            try:
                spikeMat, spikeTime = startDetection(project_id)
                data_file = {'spikeMat': spikeMat, 'spikeTime': spikeTime}
                # -------------------------------------------------------
                print("inserting detection result to database")

                detection_result_path = '../ross_data/Detection_Result/' + str(uuid4()) + '.pkl'

                with open(detection_result_path, 'wb') as f:
                    pickle.dump(data_file, f)

                detectResult = DetectResultModel.find_by_project_id(project_id)

                if detectResult:
                    detectResult.data = detection_result_path
                else:
                    detectResult = DetectResultModel(user_id, detection_result_path, project_id)

                try:
                    detectResult.save_to_db()
                except:
                    print(traceback.format_exc())
                    return {"message": "An error occurred inserting detection result."}, 500

            except:
                print(traceback.format_exc())
                return {"message": "An error occurred in detection."}, 500

        return config.json(), 201
