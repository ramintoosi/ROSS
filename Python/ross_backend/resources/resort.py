from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from resources.funcs.sorting import startResorting
import io
import numpy as np


class Resort(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)

    parser.add_argument('selected_clusters', type=str, required=True)

    def put(self):
        print('here in put resort')
        data = Resort.parser.parse_args()
        print('data : ', type(data))
        buffer = io.BytesIO()
        np.savez_compressed(buffer, sel_clusters=data)
        buffer.seek(0)
        raw_bytes = buffer.read()
        buffer.close()
        user_id = get_jwt_identity()
        try:
            print('Start Resorting ...')
            clusters_index = startResorting(user_id, raw_bytes)
            print('cluster index = ', clusters_index)

        except:
            print('An error occurred while resorting')

        return {'data': clusters_index}, 201