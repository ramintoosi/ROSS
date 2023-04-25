import io
import pickle

import flask
import numpy as np
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from models.data import RawModel
from rutils.io import read_file_in_server

# class RawData(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument('raw', type=str, required=True, help="This field cannot be left blank!")
#
#     @jwt_required
#     def get(self, name):
#         user_id = get_jwt_identity()
#         proj = ProjectModel.find_by_project_name(user_id, name)
#         if not proj:
#             return {'message': 'Project does not exist'}, 404
#         raw = proj.raw
#
#         # raw = RawModel.find_by_user_id(user_id)
#         if raw:
#             # b = io.BytesIO()
#             # b.write(raw.raw)
#             # b.seek(0)
#
#             # d = np.load(b, allow_pickle=True)
#             # print(d['raw'].shape)
#             # b.close()
#             # print(user_id, raw.project_id)
#             return {'message': "Raw Data Exists."}, 201
#
#         return {'message': 'Raw Data does not exist'}, 404
#
#     @jwt_required
#     def post(self, name):
#         user_id = get_jwt_identity()
#         proj = ProjectModel.find_by_project_name(user_id, name)
#         if not proj:
#             return {'message': 'Project does not exist'}, 404
#         raw = proj.raw
#
#         if raw:
#             return {'message': "Raw Data already exists."}, 400
#         filestr = request.data
#         # data = RawData.parser.parse_args()
#
#         # print(eval(data['raw']).shape)
#         raw = RawModel(user_id=user_id, project_id=proj.id, data=filestr)  # data['raw'])
#
#         try:
#             raw.save_to_db()
#         except:
#             return {"message": "An error occurred inserting raw data."}, 500
#
#         return "Success", 201
#
#     @jwt_required
#     def delete(self, name):
#         user_id = get_jwt_identity()
#         proj = ProjectModel.find_by_project_name(user_id, name)
#         if not proj:
#             return {'message': 'Project does not exist'}, 404
#         raw = proj.raw
#         if raw:
#             raw.delete_from_db()
#             return {'message': 'Raw Data deleted.'}
#         return {'message': 'Raw Data does not exist.'}, 404
#
#     @jwt_required
#     def put(self, name):
#         user_id = get_jwt_identity()
#         proj = ProjectModel.find_by_project_name(user_id, name)
#         if not proj:
#             return {'message': 'Project does not exist'}, 404
#         raw = proj.raw
#         filestr = request.data
#         if raw:
#             print('here')
#             raw.data = filestr
#             try:
#                 raw.save_to_db()
#             except:
#                 return {"message": "An error occurred inserting raw data."}, 500
#             return "Success", 201
#
#         else:
#             raw = RawModel(user_id, data=filestr, project_id=proj.id)
#         try:
#             print('now here')
#             raw.save_to_db()
#         except:
#             return {"message": "An error occurred inserting raw data."}, 500
#
#         return "Success", 201


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
                return response, 210
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
            try:
                raw.save_to_db()
            except:
                return {"message": "An error occurred inserting raw data."}, 500
            return "Success", 201
        else:
            raw = RawModel(user_id, data=raw_data_path, project_id=project_id, mode=mode)

        try:
            raw.save_to_db()
        except:
            return {"message": "An error occurred inserting raw data."}, 500

        return "Success", 201
