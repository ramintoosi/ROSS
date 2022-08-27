from flask_restful import Resource, reqparse
import flask
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.data import RawModel
from models.project import ProjectModel
from numpy import array, array_repr
import numpy as np
import io


class RawData(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('raw', type=str, required=True, help="This field cannot be left blank!")

    @jwt_required
    def get(self, name):      
        user_id = get_jwt_identity() 
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        raw = proj.raw
        # raw = RawModel.find_by_user_id(user_id)
        if raw:
            # b = io.BytesIO()
            # b.write(raw.raw)
            # b.seek(0)

            # d = np.load(b, allow_pickle=True)
            # print(d['raw'].shape) 
            # b.close()
            # print(user_id, raw.project_id)
            return {'message': "Raw Data Exists."}, 201

        return {'message': 'Raw Data does not exist'}, 404

    @jwt_required
    def post(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        raw = proj.raw

        if raw:
            return {'message': "Raw Data already exists."}, 400
        filestr = request.data  
        # data = RawData.parser.parse_args()

        # print(eval(data['raw']).shape)
        raw = RawModel(user_id = user_id, project_id=proj.id, data = filestr)#data['raw'])

        try:
            raw.save_to_db()
        except:
            return {"message": "An error occurred inserting raw data."}, 500

        return "Success", 201

    @jwt_required
    def delete(self, name):
        user_id = get_jwt_identity()
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        raw = proj.raw
        if raw:
            raw.delete_from_db()
            return {'message': 'Raw Data deleted.'}
        return {'message': 'Raw Data does not exist.'}, 404

    @jwt_required
    def put(self, name): 
        user_id = get_jwt_identity() 
        proj = ProjectModel.find_by_project_name(user_id, name)
        if not proj:
            return {'message': 'Project does not exist'}, 404
        raw = proj.raw
        filestr = request.data 
        if raw:
            print('here')
            raw.data = filestr
            try:
                raw.save_to_db()
            except:
                return {"message": "An error occurred inserting raw data."}, 500
            return "Success", 201
        
        else:
            raw = RawModel(user_id, data=filestr, project_id=proj.id)
        try:
            raw.save_to_db()
        except:
            return {"message": "An error occurred inserting raw data."}, 500

        return "Success", 201
