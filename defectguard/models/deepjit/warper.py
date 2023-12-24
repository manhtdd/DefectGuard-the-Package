from defectguard.models.BaseWraper import BaseWraper
import pickle, json, torch
from .model import DeepJITModel
from defectguard.utils.utils import download_folder, SRC_PATH
from .utils import *

class DeepJIT(BaseWraper):
    def __init__(self, dataset='platform', project='within', device="cpu"):
        self.model_name = 'deepjit'
        self.dataset = dataset
        self.project = project
        self.initialized = False
        self.model = None
        self.device = device
        self.message_dictionary = None
        self.code_dictionary = None
        self.hyperparameters = None
        download_folder(self.model_name, self.dataset, self.project)

    def __call__(self, message, code):
        return self.model(message, code)
    
    def get_parameters(self):
        return self.model.parameters()
    
    def set_device(self, device):
        self.device = device
    
    def initialize(self, dictionary=None, hyperparameters=None, from_pretrain=True, state_dict=None):
        # Load dictionary
        if dictionary:
            dictionary = pickle.load(open(dictionary, 'rb'))
        else:
            dictionary = pickle.load(open(f"{SRC_PATH}/models/metadata/{self.model_name}/{self.dataset}_dictionary_{self.project}", 'rb'))
        self.message_dictionary, self.code_dictionary = dictionary

        # Load parameters
        if hyperparameters:
            with open(hyperparameters, 'r') as file:
                self.hyperparameters = json.load(file)
        else:
            with open(f"{SRC_PATH}/models/metadata/{self.model_name}/hyperparameters", 'r') as file:
                self.hyperparameters = json.load(file)

        # Set up param
        self.hyperparameters["filter_sizes"] = [int(k) for k in self.hyperparameters["filter_sizes"].split(',')]
        self.hyperparameters["vocab_msg"], self.hyperparameters["vocab_code"] = len(self.message_dictionary), len(self.code_dictionary)
        self.hyperparameters["class_num"] = 1

        # Create model and Load pretrain
        self.model = DeepJITModel(self.hyperparameters).to(device=self.device)
        if from_pretrain and dictionary is None:
            self.model.load_state_dict(torch.load(f"{SRC_PATH}/models/metadata/{self.model_name}/{self.dataset}_{self.project}", map_location=self.device))
        elif state_dict:
            self.model.load_state_dict(torch.load(state_dict, map_location=self.device))

        # Set initialized to True
        self.initialized = True

    def preprocess(self, data):
        if not self.initialized:
            self.initialize()

        commit_info = data['commit_info']
        commit_hashes = []
        commit_messages = []
        codes = []

        for commit in commit_info:
            if commit:
                commit_hashes.append(commit['commit_hash'])

                # Extract commit message
                commit_message = commit['commit_message'].strip()
                commit_message = split_sentence(commit_message)
                commit_message = ' '.join(commit_message.split(' ')).lower()
                
                commit = commit['main_language_file_changes']

                code = hunks_to_code(commit)

                commit_messages.append(commit_message)
                codes.append(code)
            else:
                commit_hashes.append('Not code change')
                commit_messages.append('')
                codes.append([])

        pad_msg = padding_data(data=commit_messages, dictionary=self.message_dictionary, params=self.hyperparameters, type='msg')        
        pad_code = padding_data(data=codes, dictionary=self.code_dictionary, params=self.hyperparameters, type='code')

        # Using Pytorch Dataset and DataLoader
        code = {
            "code": pad_code.tolist(),
            "message": pad_msg.tolist()
        }
        
        return commit_hashes, code

    def inference(self, model_input):
        if not self.initialized:
            self.initialize()

        # Forward
        self.model.eval()
        with torch.no_grad():
            # Extract data from DataLoader
            code = torch.tensor(model_input["code"], device=self.device)
            message = torch.tensor(model_input["message"], device=self.device)

            # Forward
            predict = self.model(message, code)
        
        return predict

    def postprocess(self, og_commit_hashes, commit_hashes, inference_output):
        if not self.initialized:
            self.initialize()

        inference_output = inference_output.tolist()

        result = []
        for i in range(len(commit_hashes)):
            if commit_hashes[i] == 'Not code change':
                result.append({'commit_hash': og_commit_hashes[i], 'predict': -1})
            else:
                result.append({'commit_hash': commit_hashes[i], 'predict': inference_output[i]})

        return result

    def handle(self, data):
        if not self.initialized:
            self.initialize()
            
        commit_hashes, preprocessed_data = self.preprocess(data)
        model_output = self.inference(preprocessed_data)
        final_prediction = self.postprocess(data['commit_hashes'], commit_hashes, model_output)

        return final_prediction