import os
from pathlib import Path

from flask_jwt_extended import (
    jwt_required,
)
from flask_restful import Resource, reqparse

Raw_data_path = os.path.join(Path(__file__).parent, '../ross_data/Raw_Data')
Path(Raw_data_path).mkdir(parents=True, exist_ok=True)


class Browse(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('root', type=str, required=False, default=str(Path.home()))

    @jwt_required
    def get(self):
        root = Browse.parser.parse_args()['root']
        list_of_folders = [x for x in os.listdir(root) if
                           os.path.isdir(os.path.join(root, x)) and not x.startswith('.')]
        list_of_files = [x for x in os.listdir(root) if os.path.isfile(os.path.join(root, x)) and not x.startswith('.')
                         and x.endswith(('.mat', '.csv', '.tdms'))]
        return {'folders': list_of_folders, 'files': list_of_files, 'root': root}
