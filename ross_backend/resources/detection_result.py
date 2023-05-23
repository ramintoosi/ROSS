import io
import pickle

import flask
import numpy as np
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from models.data import DetectResultModel

SESSION = dict()
DATA_NUM_TO_SEND = 1000


class DetectionResult(Resource):

    @jwt_required
    def get(self):
        project_id = int(request.form["project_id"])
        detect_result = None
        if project_id in SESSION:
            detect_result = SESSION[project_id]
        else:
            detect_result_model = DetectResultModel.find_by_project_id(project_id)
            if detect_result_model:
                with open(detect_result_model.data, 'rb') as f:
                    detect_result = pickle.load(f)
            SESSION[project_id] = detect_result

        if detect_result is not None:
            inds = detect_result['inds']
            buffer = io.BytesIO()
            np.savez_compressed(buffer,
                                spike_mat=detect_result['spikeMat'][inds[:DATA_NUM_TO_SEND], :],
                                spike_time=detect_result['spikeTime'],
                                config=detect_result['config'],
                                pca_spikes=detect_result['pca_spikes'],
                                inds=inds[:DATA_NUM_TO_SEND])
            buffer.seek(0)
            raw_bytes = buffer.read()
            buffer.close()

            response = flask.make_response(raw_bytes)
            response.headers.set('Content-Type', 'application/octet-stream')
            return response

        return {'message': 'Detection Result Data does not exist'}, 404


class DetectionResultSpikeMat(Resource):

    @jwt_required
    def get(self):
        project_id = int(request.json["project_id"])
        detect_result = None
        if project_id in SESSION:
            detect_result = SESSION[project_id]
        else:
            detect_result_model = DetectResultModel.find_by_project_id(project_id)
            if detect_result_model:
                with open(detect_result_model.data, 'rb') as f:
                    detect_result = pickle.load(f)
            SESSION[project_id] = detect_result

        if detect_result is not None:
            buffer = io.BytesIO()
            np.savez_compressed(buffer, spike_mat=detect_result['spikeMat'])
            buffer.seek(0)
            raw_bytes = buffer.read()
            buffer.close()

            response = flask.make_response(raw_bytes)
            response.headers.set('Content-Type', 'application/octet-stream')
            return response

        return {'message': 'Detection Result Data does not exist'}, 404
