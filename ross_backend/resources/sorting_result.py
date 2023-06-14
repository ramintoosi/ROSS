import io
import os.path
import pickle
from pathlib import Path
from uuid import uuid4

import flask
import numpy as np
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from models.data import SortResultModel, RawModel, DetectResultModel
from resources.detection_result import SESSION as DET_SESSION
from resources.funcs.sorting import create_cluster_time_vec

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

    @jwt_required
    def put(self):
        # filestr = request.data
        user_id = get_jwt_identity()

        b = io.BytesIO()
        b.write(request.data)
        b.seek(0)
        d = np.load(b, allow_pickle=True)

        project_id = int(d["project_id"])
        clusters = d["clusters"]
        b.close()

        detect_result = None
        if project_id in DET_SESSION:
            detect_result = DET_SESSION[project_id]
        else:
            detect_result_model = DetectResultModel.find_by_project_id(project_id)
            if detect_result_model:
                with open(detect_result_model.data, 'rb') as f:
                    detect_result = pickle.load(f)
            DET_SESSION[project_id] = detect_result
        if detect_result is None:
            return {"message": "No Detection"}, 400

        save_sort_result_path = str(Path(RawModel.find_by_project_id(project_id).data).parent /
                                    (str(uuid4()) + '.pkl'))

        cluster_time_vec = create_cluster_time_vec(detect_result['spikeTime'], clusters, detect_result['config'])

        with open(save_sort_result_path, 'wb') as f:
            pickle.dump({"clusters": clusters, "cluster_time_vec": cluster_time_vec}, f)
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
