'''
INCOMPLETED
Need extract features
'''

from .utils import *
from .Extractor import Extractor
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
        self.diff = None
        self.features = None
        self.extractor = Extractor()

    def set_access_token(self, token):
        self.access_token = token

    def get_headers(self):
        if self.access_token is None:
            print(f"Failed to create headers with access_token: {self.access_token}")
            return None
        headers = {
            'Authorization': f'token {self.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        return headers

    def set_repo(self, owner, repo):
        if owner is None or repo is None:
            print(f"Failed to set repository with owner: {owner} - repository: {repo}")
            return None
        self.owner = owner
        self.repo = repo

    def get_pull_requests_diff(self):
        headers = self.get_headers()
        if headers is None:
            return None

        response = requests.get(f'https://api.github.com/repos/{self.owner}/{self.repo}/pulls', headers=headers)
        if response.status_code == 200:
            pull_requests = response.json()
            if pull_requests:
                diff_response = []
                self.diff = {}
                for pr in pull_requests:
                    diff_response.append(requests.get(pr['diff_url'], headers=headers))
                
                    if diff_response[-1].status_code == 200:
                        self.diff[pr['number']] = diff_response[-1].text
                    else:
                        print(f"Failed to fetch diff for PR #{pr['number']}: {diff_response[-1].status_code}")

                return self.diff
            else:
                print("No pull requests found.")
        else:
            print(f"Failed to fetch pull requests: {response.status_code}")
        return None
    
    def get_pull_requests_feature(self):
        self.features = {}
        la, ld, lt = calu_modified_lines()
    
    def get_pull_requests(self):
        self.get_pull_requests_diff()
        commit = []
        for diff in self.diff.items():
            commit.append(self.extractor.extract_one_commit_diff(commit_id='', languages='JavaScript', diff_log=diff))
        return commit
    
    def test(self):
        
        diff = diff[0].split('\n')
        if len(diff[-1]) == 0:
             diff.pop()
        t = self.extractor.extract_one_commit_diff(commit_id='', languages=['JavaScript'], diff_log=diff)
        import json
        with open('test/test.txt', 'w') as f:
            json.dump(t, f, indent=4)
        print(t)
    