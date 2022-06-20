from flask_restful import Resource, reqparse
import flask
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.data import SortResultModel


class SortingResultDefault(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('cluster', type=str, required=True, help="This field cannot be left blank!")

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        sort_result = SortResultModel.find_by_user_id(user_id)
        if sort_result:
            # b = io.BytesIO()
            # b.write(raw.raw)
            # b.seek(0)
            # d = np.load(b, allow_pickle=True)
            # print(d['raw'].shape)
            # b.close()
            # print(raw.user_id, raw.project_id)
            if sort_result.data:
                response = flask.make_response(sort_result.data)
                response.headers.set('Content-Type', 'application/octet-stream')
                return response

        return {'message': 'Sort Result Data does not exist'}, 404

    @jwt_required
    def post(self):
        filestr = request.data
        user_id = get_jwt_identity()
        if SortResultModel.find_by_user_id(user_id):
            return {'message': "Detection Result already exists."}, 400

        # data = RawData.parser.parse_args()

        # print(eval(data['raw']).shape)
        data = SortResultModel(user_id=user_id, data=filestr)  # data['raw'])

        try:
            data.save_to_db()
        except:
            return {"message": "An error occurred inserting sort result data."}, 500

        return "Success", 201

    @jwt_required
    def delete(self):
        user_id = get_jwt_identity()
        data = SortResultModel.find_by_user_id(user_id)
        if data:
            data.delete_from_db()
            return {'message': 'Sort Result Data deleted.'}
        return {'message': 'Sort Result Data does not exist.'}, 404

    @jwt_required
    def put(self):
        filestr = request.data
        user_id = get_jwt_identity()
        data = SortResultModel.find_by_user_id(user_id)
        if data:
            data.data = filestr
            try:
                data.save_to_db()
            except:
                return {"message": "An error occurred inserting sort result data."}, 500
            return "Success", 201

        else:
            data = SortResultModel(user_id, data=filestr)
        try:
            data.save_to_db()
        except:
            return {"message": "An error occurred inserting sort result data."}, 500

        return "Success", 201