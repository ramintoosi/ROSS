import io
import pickle

import flask
import numpy as np
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from models.data import RawModel, DetectResultModel, SortResultModel
from rutils.io import read_file_in_server

SESSION = dict()


class RawDataDefault(Resource):

    @jwt_required
    def get(self):
        project_id = request.json['project_id']
        raw = RawModel.find_by_project_id(project_id)

        if raw:
            if raw.mode == 0:
                response = flask.make_response(raw.data)
                response.headers.set('Content-Type', 'application/octet-stream')
                response.status_code = 210
                return response
            else:
                if request.json['start'] is None:
                    return {'message': 'SERVER MODE'}, 212
                if project_id in SESSION:
                    raw_data = SESSION[project_id]
                else:
                    with open(raw.data, 'rb') as f:
                        raw_data = pickle.load(f)
                start = request.json['start']
                stop = request.json['stop']
                limit = request.json['limit']
                stop = min(len(raw_data), stop)

                ds = int((stop - start) / limit) + 1
                visible = raw_data[start:stop:ds]

                buffer = io.BytesIO()
                np.savez_compressed(buffer, visible=visible, stop=stop, ds=ds)
                buffer.seek(0)
                data = buffer.read()
                buffer.close()
                response = flask.make_response(data)
                response.headers.set('Content-Type', 'application/octet-stream')
                response.status_code = 211
                return response
        return {'message': 'Raw Data does not exist'}, 404

    @jwt_required
    def post(self):
        raw_data = request.json['raw_data']
        user_id = get_jwt_identity()
        project_id = request.json['project_id']
        mode = request.json['mode']
        raw = RawModel.find_by_project_id(project_id)
        if mode == 0:
            raw_data_path = raw_data
        elif mode == 1:
            try:
                raw_data_path, SESSION[project_id] = read_file_in_server(request.json)
            except TypeError as e:
                return {"message": str(e)}, 400
            except ValueError as e:
                return {"message": str(e)}, 400
            except KeyError:
                return {"message": 'Provided variable name is incorrect'}, 400
        else:
            return {"message": f"Mode {mode} not supported"}, 400
        if raw:
            raw.data = raw_data_path
            raw.mode = mode
        else:
            raw = RawModel(user_id, data=raw_data_path, project_id=project_id, mode=mode)

        try:
            raw.save_to_db()
            detect_result = DetectResultModel.find_by_project_id(project_id)
            if detect_result:
                detect_result.delete_from_db()
            sort_result = SortResultModel.find_by_project_id(project_id)
            if sort_result:
                sort_result.delete_from_db()
        except Exception as e:
            return {"message": str(e)}, 500

        return "Success", 201
