import requests
import io
import numpy as np


class UserAccount():
    def __init__(self, url):
        self.url = url
        self.refresh_token = None
        self.access_token = None

    def refresh_jwt_token(self):
        response = requests.post(self.url + '/refresh', headers={'Authorization': 'Bearer ' + self.refresh_token})
        if response.ok:
            self.access_token = response.json()["access_token"]
    
    def sign_up(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(self.url + '/register', json=data)
        if response.ok:
            return {'stat': True, 'message':response.json()["message"]}
        else:
            return {'stat': False, 'message':response.json()["message"]}

    def sign_in(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(self.url + '/login', json=data)
        if response.ok:
            self.access_token = response.json()["access_token"]
            self.refresh_token = response.json()["refresh_token"]

            return {'stat':True, 'message':'success'}
        else:
            return{'stat':False, 'message':response.json()["message"]}

    def sign_out(self):
        response = requests.post(self.url + '/logout', headers={'Authorization': 'Bearer ' + self.access_token})
        if response.json()["message"] == 'The token has expired.':
            self.refresh_jwt_token()
            response = requests.post(self.url + '/logout', headers={'Authorization': 'Bearer ' + self.access_token})        
        if response.ok:
            self.access_token = None
            self.refresh_token = None
            return {'stat':True, 'message':'sucess'}
        else:
            return {'stat':False, 'message':response.json()["message"]}

    def post_raw_data(self, raw_data):
        if not (self.access_token == None):

            # raw_bytes = self.raw.tobytes()
            # # d = np.frombuffer(raw_bytes)
            # # print(d.shape)
            # response = requests.put(self.url + 'raw', headers={'Authorization': 'Bearer ' + self.access_token}, data=raw_bytes)
            
            buffer = io.BytesIO()
            np.savez_compressed(buffer, raw=raw_data)
            buffer.seek(0)
            raw_bytes = buffer.read()
            buffer.close()
            response = requests.put(self.url + 'raw', headers={'Authorization': 'Bearer ' + self.access_token}, data=raw_bytes)

            # b2 = io.BytesIO()
            # b2.write(r)
            # b2.seek(0)

            # d2 = np.load(b2, allow_pickle=True)
            # print(d2['raw'].shape)

            if response.ok:
                return {'stat': True, 'message': 'success'}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.put(self.url + 'raw', headers={'Authorization': 'Bearer ' + self.access_token}, data=raw_bytes)
                if response.ok:
                    return {'stat':True, 'message': 'success'}
            return {'stat':False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}
    

    def load_project(self, project_name):
        if not (self.access_token == None):
            response = requests.get(self.url + '/project/' + project_name, headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat':True} 
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.get(self.url + '/project/' + project_name, headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat':True}
            return {'stat':False, 'message':response.json()["message"]}
        return {'stat':False, 'message': 'Not Logged In!'}


    def get_projects(self):
        if not (self.access_token == None):
            response = requests.get(self.url + '/projects' , headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat':True, 'projects':response.json()['projects']} 
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.get(self.url + '/projects' , headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat':True, 'projects':response.json()["projects"]}
            return {'stat':False, 'message':response.json()["message"]}
        return {'stat':False, 'message': 'Not Logged In!'}


    def get_raw_data(self):
        if not (self.access_token == None):
            response = requests.get(self.url + '/raw' , headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                b = io.BytesIO()
                # print(response.type())
                b.write(response.content)
                b.seek(0)

                d = np.load(b, allow_pickle=True)
                # b.close()
                return {'stat':True, 'raw':d['raw'].flatten()} 
            # elif response.content['message'] == 'The token has expired.':
            elif response.status_code == 401:
                self.refresh_jwt_token()
                response = requests.get(self.url + '/raw', headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    b = io.BytesIO()
                    # print(response.type())
                    b.write(response.content)
                    b.seek(0)

                    d = np.load(b, allow_pickle=True)
                    # b.close()
                    return {'stat':True, 'raw':d['raw'].flatten()} 
            return {'stat':False, 'message':response.json()['message']}
        return {'stat':False, 'message': 'Not Logged In!'}


    def get_detection_result(self):
        if not (self.access_token == None):
            response = requests.get(self.url + '/detection_result', headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                b = io.BytesIO()
                # print(response.type())
                b.write(response.content)
                b.seek(0)

                d = np.load(b, allow_pickle=True)
                # b.close()
                return {'stat': True, 'spike_mat': d['spike_mat'], 'spike_time': d['spike_time']}
            # elif response.content['message'] == 'The token has expired.':
            elif response.status_code == 401:
                self.refresh_jwt_token()
                response = requests.get(self.url + '/detection_result', headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    b = io.BytesIO()
                    # print(response.type())
                    b.write(response.content)
                    b.seek(0)

                    d = np.load(b, allow_pickle=True)
                    # b.close()
                    return {'stat': True, 'spike_mat': d['spike_mat'], 'spike_time': d['spike_time']}
            return {'stat': False, 'message': response.json()['message']}
        return {'stat': False, 'message': 'Not Logged In!'}

    def get_config_detect(self):
        if not (self.access_token == None):
            response = requests.get(self.url + '/detect', headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat':True, 'config':response.json()}
                print('here')
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.get(self.url + '/detect', headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat':True, 'config':response.json()} 
            return {'stat':False, 'message':response.json()["message"]}
        return {'stat':False, 'message': 'Not Logged In!'}

    def get_config_sort(self):
        if not (self.access_token == None):
            response = requests.get(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat': True, 'config': response.json()}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.get(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat': True, 'config': response.json()}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def save_project_as(self, name):
        if not (self.access_token == None):
            response = requests.post(self.url + '/project/' + name, headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat':True, 'message':'success'}

            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.post(self.url + '/project/' + name, headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat':True, 'message':'success'}
            return {'stat':False, 'message':response.json()["message"]}
        return {'stat':False, 'message': 'Not Logged In!'}


    def save_project(self, name):
        if not (self.access_token == None):
            response = requests.put(self.url + '/project/' + name, headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat':True, 'message':'success'}

            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.post(self.url + '/project/' + name, headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat':True, 'message':'success'}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def delete_project(self, name):
        if not (self.access_token == None):
            response = requests.delete(self.url + '/project/' + name, headers={'Authorization': 'Bearer ' + self.access_token})
            if response.ok:
                return {'stat':True, 'message':'success'}

            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.delete(self.url + '/project/' + name, headers={'Authorization': 'Bearer ' + self.access_token})
                if response.ok:
                    return {'stat':True, 'message':'success'}
            return {'stat':False, 'message':response.json()["message"]}
        return {'stat':False, 'message': 'Not Logged In!'}

    def start_detection(self, config):
        data = config
        data['run_detection'] = True
        if not (self.access_token == None):
            response = requests.put(self.url + 'detect', headers={'Authorization': 'Bearer ' + self.access_token}, json=data)
            if response.ok:
                return {'stat':True, 'message':'success'}

            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.put(self.url + 'detect', headers={'Authorization': 'Bearer ' + self.access_token}, json=data)
                if response.ok:
                    return {'stat':True, 'message':'success'}
            return {'stat':False, 'message':response.json()["message"]}
        return {'stat':False, 'message': 'Not Logged In!'}

    def start_sorting(self, config):
        data = config
        data['run_sorting'] = True
        if not (self.access_token == None):
            response = requests.put(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token}, json=data)
            if response.ok:
                return {'stat': True, 'message': 'success'}

            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.put(self.url + 'sort', headers={'Authorization': 'Bearer ' + self.access_token}, json=data)
                if response.ok:
                    return {'stat': True, 'message': 'success'}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}