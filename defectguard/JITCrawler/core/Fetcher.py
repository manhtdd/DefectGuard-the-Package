'''
INCOMPLETED
Need extract features
'''
from .utils import calu_modified_lines
from .Extractor import Extractor
from .Processor import Processor
import requests
import base64

class Fetcher:
    def __init__(
        self,
        access_token = None,
        owner = None,
        repo = None
    ):
        self.set_access_token(access_token)
        self.set_repo(owner, repo)
        self.extractor = Extractor()
        self.processor = Processor("dg_cache")

    def set_access_token(self, token):
        self.access_token = token

    def get_headers(self):
        if self.access_token is None:
            return None
        else:
            return 
            {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }

    def set_repo(self, owner, repo):
        if owner is None or repo is None:
            print(f"Failed to set repository with owner: {owner} - repository: {repo}")
            return None
        self.owner = owner
        self.repo = repo

    def get_one_pull_requests_diff(self, pull_request_number):
        headers = self.get_headers()
        response = requests.get(f'https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pull_request_number}', headers=headers)
        if response.status_code == 200:
            pull_request = response.json()
            if pull_request:
                base = pull_request["base"]["sha"]
                diff_response = requests.get(pull_request['diff_url'], headers=headers)
            
                if diff_response.status_code == 200:
                    diff = diff_response.text.split('\n')
                    if len(diff[-1]) == 0:
                        diff.pop()
                    return base, diff
                else:
                    print(f"Failed to fetch diff for PR #{pull_request_number}: {diff_response.status_code}")
            else:
                print("No pull requests found.")
        else:
            print(f"Failed to fetch pull requests: {response.status_code}")

    def get_pull_request_data(self, pull_request_numbers):
        pull_diffs = []
        data = {}
        for i in pull_request_numbers:
            base, pull_log = self.get_one_pull_requests_diff(i)
            pull = self.extractor.extract_one_commit_diff(commit_id='', pull_log=pull_log)
            pull['commit_id'] = base
            data[i]={}
            output = self.processor.process_one_change_commit(pull)
            for codes, features in zip(output['change_codes'], output['change_features']):
                data[i][codes['file_name']] = {
                    'added_code': codes['added_code'],
                    'removed_code': codes['removed_code'],
                    'deepjit': codes['deepjit'],
                    'simcom': codes['simcom'],
                    'la': features['la'],
                    'ld': features['ld'],
                    'lt': features['lt']
                }
        return data
    