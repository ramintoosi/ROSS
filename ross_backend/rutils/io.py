import os
import pickle
from pathlib import Path
from uuid import uuid4

from scipy.io import loadmat

Raw_data_path = os.path.join(Path(__file__).parent, '../ross_data/Raw_Data')
Path(Raw_data_path).mkdir(parents=True, exist_ok=True)


def read_file_in_server(request_data: dict):
    print(request_data)
    if 'raw_data' in request_data and 'project_id' in request_data:
        filename = request_data['raw_data']
        file_extension = os.path.splitext(filename)[-1]
        if file_extension == '.mat':
            file_raw = loadmat(filename)
            variables = list(file_raw.keys())
            if '__version__' in variables: variables.remove('__version__')
            if '__header__' in variables: variables.remove('__header__')
            if '__globals__' in variables: variables.remove('__globals__')

            if len(variables) > 1:
                if 'varname' in request_data:
                    variable = request_data['varname']
                else:
                    raise ValueError("More than one variable exists ")
            else:
                variable = variables[0]

            temp = file_raw[variable].flatten()

            # ------------------ save raw data as pkl file in data_set folder -----------------------
            address = os.path.join(Raw_data_path, str(uuid4()) + '.pkl')

            with open(address, 'wb') as f:
                pickle.dump(temp, f)
            # ----------------------------------------------------------------------------------------
            return address, temp
        else:
            raise TypeError("File not supported")
    else:
        raise ValueError("request data is incorrect")
