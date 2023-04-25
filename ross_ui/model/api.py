import io

import numpy as np
import requests


class API():
    def __init__(self, url):
        self.url = url
        self.refresh_token = None
        self.access_token = None
        self.project_id = None

    def refresh_jwt_token(self):
        response = requests.post(self.url + '/refresh',
                                 headers={'Authorization': 'Bearer ' + self.refresh_token})

        # response = requests.post(self.url + '/refresh',
        #                          headers={'Authorization': 'Bearer ' + self.refresh_token},
        #                          data={'project_id': self.project_id})

        if response.ok:
            self.access_token = response.json()["access_token"]
            return True
        else:
            return False

    def sign_up(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(self.url + '/register', json=data)
        if response.ok:
            return {'stat': True, 'message': response.json()["message"]}
        else:
            return {'stat': False, 'message': response.json()["message"]}

    def sign_in(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(self.url + '/login', json=data)
        if response.ok:
            self.access_token = response.json()["access_token"]
            self.refresh_token = response.json()["refresh_token"]
            self.project_id = response.json()["project_id"]

            return {'stat': True, 'message': 'success'}
        else:
            return {'stat': False, 'message': response.json()["message"]}

    def sign_out(self):
        response = requests.post(self.url + '/logout', headers={'Authorization': 'Bearer ' + self.access_token})
        if response.json()["message"] == 'The token has expired.':
            self.refresh_jwt_token()
            response = requests.post(self.url + '/logout', headers={'Authorization': 'Bearer ' + self.access_token})
        if response.ok:
            self.access_token = None
            self.refresh_token = None
            self.project_id = None

            return {'stat': True, 'message': 'sucess'}
        else:
            return {'stat': False, 'message': response.json()["message"]}

    def post_raw_data(self, raw_data_path, mode=0, varname=''):
        if self.access_token is not None:

            # buffer = io.BytesIO()
            # np.savez_compressed(buffer, raw=raw_data)
            # buffer.seek(0)
            # raw_bytes = buffer.read()
            # buffer.close()

            response = requests.post(self.url + '/raw', headers={'Authorization': 'Bearer ' + self.access_token},
                                     json={"raw_data": raw_data_path,
                                           "project_id": self.project_id,
                                           "mode": mode,
                                           "varname": varname})

            if response.ok:
                return {'stat': True, 'message': 'success'}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.post(self.url + '/raw', headers={'Authorization': 'Bearer ' + self.access_token},
                                         json={"raw_data": raw_data_path,
                                               "project_id": self.project_id,
                                               "mode": mode,
                                               "varname": varname})
                if response.ok:
                    return {'stat': True, 'message': 'success'}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def get_raw_data(self, start=None, stop=None, limit=None):
        if not (self.access_token is None):
            response = requests.get(self.url + '/raw',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    json={'project_id': self.project_id,
                                          'start': start,
                                          'stop': stop,
                                          'limit': limit})

            if response.ok:
                if response.status_code == 210:
                    return {'stat': True, 'raw': response.content}
                elif response.status_code == 211:
                    iob = io.BytesIO()
                    iob.write(response.content)
                    iob.seek(0)
                    raw_data = np.load(iob, allow_pickle=True)
                    return {'stat': True,
                            'visible': raw_data['visible'].flatten(),
                            'stop': raw_data['stop'].flatten(),
                            'ds': raw_data['ds'].flatten()}
                elif response.status_code == 212:
                    return {'stat': True, 'message': 'SERVER MODE'}
                else:
                    return {'stat': False, 'message': 'Status code not supported!'}

            elif response.status_code == 401:
                ret = self.refresh_jwt_token()
                if ret:
                    self.get_raw_data(start, stop, limit)
            return {'stat': False, 'message': response.json()['message']}
        return {'stat': False, 'message': 'Not Logged In!'}

    def get_detection_result(self):
        if not (self.access_token is None):
            response = requests.get(self.url + '/detection_result',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    data={'project_id': self.project_id})

            if response.ok:
                b = io.BytesIO()
                b.write(response.content)
                b.seek(0)
                d = np.load(b, allow_pickle=True)
                return {'stat': True, 'spike_mat': d['spike_mat'], 'spike_time': d['spike_time']}

            elif response.status_code == 401:
                self.refresh_jwt_token()
                response = requests.get(self.url + '/detection_result',
                                        headers={'Authorization': 'Bearer ' + self.access_token},
                                        data={'project_id': self.project_id})
                if response.ok:
                    b = io.BytesIO()
                    b.write(response.content)
                    b.seek(0)
                    d = np.load(b, allow_pickle=True)
                    return {'stat': True, 'spike_mat': d['spike_mat'], 'spike_time': d['spike_time']}
            return {'stat': False, 'message': response.json()['message']}
        return {'stat': False, 'message': 'Not Logged In!'}

    def get_sorting_result(self):
        if not (self.access_token is None):
            response = requests.get(self.url + '/sorting_result',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    data={'project_id': self.project_id})
            if response.ok:
                b = io.BytesIO()
                b.write(response.content)
                b.seek(0)

                d = np.load(b, allow_pickle=True)
                return {'stat': True, 'clusters': d['clusters']}
            elif response.status_code == 401:
                self.refresh_jwt_token()
                response = requests.get(self.url + '/sorting_result',
                                        headers={'Authorization': 'Bearer ' + self.access_token},
                                        data={'project_id': self.project_id})
                if response.ok:
                    b = io.BytesIO()
                    b.write(response.content)
                    b.seek(0)
                    d = np.load(b, allow_pickle=True)
                    print("d", d)
                    return {'stat': True, 'clusters': d['clusters']}
            return {'stat': False, 'message': response.json()['message']}
        return {'stat': False, 'message': 'Not Logged In!'}

    def get_config_detect(self):
        if not (self.access_token is None):
            response = requests.get(self.url + '/detect',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    data={'project_id': self.project_id})
            if response.ok:
                return {'stat': True, 'config': response.json()}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.get(self.url + '/detect',
                                        headers={'Authorization': 'Bearer ' + self.access_token},
                                        data={'project_id': self.project_id})
                if response.ok:
                    return {'stat': True, 'config': response.json()}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def get_config_sort(self):
        if not (self.access_token is None):
            response = requests.get(self.url + '/sort',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    data={'project_id': self.project_id})
            if response.ok:
                return {'stat': True, 'config': response.json()}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.get(self.url + '/sort',
                                        headers={'Authorization': 'Bearer ' + self.access_token},
                                        data={'project_id': self.project_id})
                if response.ok:
                    return {'stat': True, 'config': response.json()}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    # def save_project_as(self, name):
    #     if not (self.access_token is None):
    #         response = requests.post(self.url + '/project/' + name,
    #                                  headers={'Authorization': 'Bearer ' + self.access_token},
    #                                  data = {'project_id': self.project_id})
    #         if response.ok:
    #             return {'stat': True, 'message': 'success'}
    #
    #         elif response.json()["message"] == 'The token has expired.':
    #             self.refresh_jwt_token()
    #             response = requests.post(self.url + '/project/' + name,
    #                                      headers={'Authorization': 'Bearer ' + self.access_token},
    #                                      data = {'project_id': self.project_id})
    #             if response.ok:
    #                 return {'stat': True, 'message': 'success'}
    #         return {'stat': False, 'message': response.json()["message"]}
    #     return {'stat': False, 'message': 'Not Logged In!'}

    # def save_project(self, name):
    #     if not (self.access_token is None):
    #         response = requests.put(self.url + '/project/' + name,
    #                                 headers={'Authorization': 'Bearer ' + self.access_token})
    #         if response.ok:
    #             return {'stat': True, 'message': 'success'}
    #
    #         elif response.json()["message"] == 'The token has expired.':
    #             self.refresh_jwt_token()
    #             response = requests.post(self.url + '/project/' + name,
    #                                      headers={'Authorization': 'Bearer ' + self.access_token})
    #             if response.ok:
    #                 return {'stat': True, 'message': 'success'}
    #         return {'stat': False, 'message': response.json()["message"]}
    #     return {'stat': False, 'message': 'Not Logged In!'}
    #
    # def delete_project(self, name):
    #     if not (self.access_token is None):
    #         response = requests.delete(self.url + '/project/' + name,
    #                                    headers={'Authorization': 'Bearer ' + self.access_token})
    #         if response.ok:
    #             return {'stat': True, 'message': 'success'}
    #
    #         elif response.json()["message"] == 'The token has expired.':
    #             self.refresh_jwt_token()
    #             response = requests.delete(self.url + '/project/' + name,
    #                                        headers={'Authorization': 'Bearer ' + self.access_token})
    #             if response.ok:
    #                 return {'stat': True, 'message': 'success'}
    #         return {'stat': False, 'message': response.json()["message"]}
    #     return {'stat': False, 'message': 'Not Logged In!'}

    def start_detection(self, config):
        data = config
        data['run_detection'] = True
        data['project_id'] = self.project_id
        if not (self.access_token is None):
            response = requests.put(self.url + '/detect',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    json=data)
            if response.ok:
                return {'stat': True, 'message': 'success'}

            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.put(self.url + '/detect',
                                        headers={'Authorization': 'Bearer ' + self.access_token},
                                        json=data)
                if response.ok:
                    return {'stat': True, 'message': 'success'}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def start_sorting(self, config):
        data = config
        data['run_sorting'] = True
        data['project_id'] = self.project_id
        if not (self.access_token is None):
            response = requests.put(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token},
                                    json=data)
            if response.ok:
                return {'stat': True, 'message': 'success'}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.put(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token},
                                        json=data)
                if response.ok:
                    return {'stat': True, 'message': 'success'}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def start_Resorting(self, config, clusters, selected_clusters):
        data = config
        data['clusters'] = [clusters.tolist()]
        data['selected_clusters'] = [selected_clusters]
        data['run_sorting'] = True
        data['project_id'] = self.project_id
        if not (self.access_token is None):
            response = requests.put(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token},
                                    json=data)
            if response.ok:
                return {'stat': True, 'message': 'success', 'clusters': response.json()["clusters"]}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()
                response = requests.put(self.url + '/sort', headers={'Authorization': 'Bearer ' + self.access_token},
                                        json=data)
                if response.ok:
                    return {'stat': True, 'message': 'success', 'clusters': response.json()["clusters"]}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def save_sort_results(self, clusters):
        if not (self.access_token is None):

            buffer = io.BytesIO()
            np.savez_compressed(buffer, clusters=clusters, project_id=self.project_id)
            buffer.seek(0)
            clusters_bytes = buffer.read()
            buffer.close()
            response = requests.put(self.url + '/sorting_result',
                                    headers={'Authorization': 'Bearer ' + self.access_token},
                                    data=clusters_bytes)

            if response.ok:
                return {'stat': True, 'message': 'success'}
            elif response.json()["message"] == 'The token has expired.':
                self.refresh_jwt_token()

                response = requests.put(self.url + '/sorting_result',
                                        headers={'Authorization': 'Bearer ' + self.access_token},
                                        data=clusters_bytes)

                if response.ok:
                    return {'stat': True, 'message': 'success'}
            return {'stat': False, 'message': response.json()["message"]}
        return {'stat': False, 'message': 'Not Logged In!'}

    def browse(self, root: str):
        if root is None:
            response = requests.get(self.url + '/browse', headers={'Authorization': 'Bearer ' + self.access_token})
        else:
            response = requests.get(self.url + '/browse', headers={'Authorization': 'Bearer ' + self.access_token},
                                    json={'root': root})
        if response.ok:
            return response.json()
        else:
            return None

    def browse_send_filename(self, filename, varname):
        response = requests.get(self.url + '/browse', headers={'Authorization': 'Bearer ' + self.access_token},
                                json={'filename': filename, 'varname': varname, 'project_id': self.project_id})
        if response.ok:
            return response
