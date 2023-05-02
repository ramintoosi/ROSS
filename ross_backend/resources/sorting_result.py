import io
import os.path
import pickle
from uuid import uuid4

import flask
import numpy as np
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from models.data import SortResultModel

SESSION = dict()


class SortingResultDefault(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('cluster', type=str, required=True, help="This field cannot be left blank!")

    @jwt_required
    def get(self):
        project_id = request.form["project_id"]
        sort_dict = None
        if project_id in SESSION:
            sort_dict = SESSION[project_id]
        else:

            sort_result = SortResultModel.find_by_project_id(project_id)

            if sort_result:
                with open(sort_result.data, 'rb') as f:
                    sort_dict = pickle.load(f)
        if sort_dict is not None:
            buffer = io.BytesIO()
            np.savez_compressed(buffer, clusters=sort_dict['clusters'], cluster_time_vec=sort_dict["cluster_time_vec"])
            buffer.seek(0)
            raw_bytes = buffer.read()
            buffer.close()

            response = flask.make_response(raw_bytes)
            response.headers.set('Content-Type', 'application/octet-stream')
            return response

        return {'message': 'Sort Result Data does not exist'}, 404

    # @jwt_required
    # def post(self):
    #     filestr = request.data
    #     user_id = get_jwt_identity()
    #     project_id = request.form["project_id"]
    #     if SortResultModel.find_by_project_id(project_id):
    #         return {'message': "Detection Result already exists."}, 400
    #
    #     # data = RawData.parser.parse_args()
    #
    #     # print(eval(data['raw']).shape)
    #     data = SortResultModel(user_id=user_id, data=filestr, project_id=project_id)  # data['raw'])
    #
    #     try:
    #         data.save_to_db()
    #     except:
    #         return {"message": "An error occurred inserting sort result data."}, 500
    #
    #     return "Success", 201

    # @jwt_required
    # def delete(self):
    #     user_id = get_jwt_identity()
    #     project_id = request.form["project_id"]
    #     data = SortResultModel.find_by_project_id(project_id)
    #     if data:
    #         data.delete_from_db()
    #         return {'message': 'Sort Result Data deleted.'}
    #     return {'message': 'Sort Result Data does not exist.'}, 404

    @jwt_required
    def put(self):
        # TODO : changes must be applied to cluster_time_vec
        # filestr = request.data
        user_id = get_jwt_identity()

        b = io.BytesIO()
        b.write(request.data)
        b.seek(0)
        d = np.load(b, allow_pickle=True)

        project_id = d["project_id"]
        clusters = d["clusters"]
        b.close()

        save_sort_result_path = '../ross_data/Sort_Result/' + str(uuid4()) + '.pkl'
        with open(save_sort_result_path, 'wb') as f:
            pickle.dump({"clusters": clusters}, f)
        data = SortResultModel.find_by_project_id(int(project_id))
        if data:
            if os.path.isfile(data.data):
                os.remove(data.data)
            data.data = save_sort_result_path
            try:
                data.save_to_db()
            except:
                return {"message": "An error occurred inserting sort result data."}, 500
            return "Success", 201

        else:
            data = SortResultModel(user_id=user_id, data=save_sort_result_path, project_id=project_id)
        try:
            data.save_to_db()
        except:
            return {"message": "An error occurred inserting sort result data."}, 500

        return "Success", 201
