import io
import pickle

import flask
import numpy as np
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from models.data import DetectResultModel


class DetectionResultDefault(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('raw', type=str, required=True, help="This field cannot be left blank!")

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        # user = UserModel.find_by_id(user_id)
        project_id = request.form["project_id"]
        detect_result_model = DetectResultModel.find_by_project_id(project_id)

        if detect_result_model:
            with open(detect_result_model.data, 'rb') as f:
                detect_result = pickle.load(f)

            buffer = io.BytesIO()
            np.savez_compressed(buffer, spike_mat=detect_result['spikeMat'], spike_time=detect_result['spikeTime'])
            buffer.seek(0)
            raw_bytes = buffer.read()
            buffer.close()

            response = flask.make_response(raw_bytes)
            response.headers.set('Content-Type', 'application/octet-stream')
            return response

        return {'message': 'Detection Result Data does not exist'}, 404

    @jwt_required
    def post(self):
        filestr = request.data
        user_id = get_jwt_identity()
        if DetectResultModel.find_by_user_id(user_id):
            return {'message': "Detection Result already exists."}, 400
        # data = RawData.parser.parse_args()
        # print(eval(data['raw']).shape)
        data = DetectResultModel(user_id=user_id, data=filestr)  # data['raw'])

        try:
            data.save_to_db()
        except:
            return {"message": "An error occurred inserting sort result data."}, 500

        return "Success", 201

    @jwt_required
    def delete(self):
        user_id = get_jwt_identity()
        data = DetectResultModel.find_by_user_id(user_id)
        if data:
            data.delete_from_db()
            return {'message': 'Detection Result Data deleted.'}
        return {'message': 'Detection Result Data does not exist.'}, 404

    @jwt_required
    def put(self):
        filestr = request.data
        user_id = get_jwt_identity()
        data = DetectResultModel.find_by_user_id(user_id)
        if data:
            data.data = filestr
            try:
                data.save_to_db()

            except:
                return {"message": "An error occurred inserting sort result data."}, 500
            return "Success", 201

        else:
            data = DetectResultModel(user_id, data=filestr)

        try:
            data.save_to_db()
        except:
            return {"message": "An error occurred inserting sort result data."}, 500

        return "Success", 201
