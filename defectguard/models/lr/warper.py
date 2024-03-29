from defectguard.models.BaseWraper import BaseWraper
import pickle
from defectguard.utils.utils import download_folder, SRC_PATH
from defectguard.utils.logger import logger
import pandas as pd

class LogisticRegression(BaseWraper):
    def __init__(self, dataset='platform', project='within', device="cpu"):
        self.model_name = 'lr'
        self.dataset = dataset
        self.project = project
        self.initialized = False
        self.model = None
        self.device = device
        self.columns = (["ns","nd","nf","entrophy","la","ld","lt","fix","ndev","age","nuc","exp","rexp","sexp"])
        download_folder(self.model_name, self.dataset, self.project)
        
    def initialize(self):
        with open(f"{SRC_PATH}/models/metadata/{self.model_name}/{self.dataset}", "rb") as f:
            self.model = pickle.load(f)

        # Set initialized to True
        self.initialized = True

    def preprocess(self, data):
        if not self.initialized:
            self.initialize()
        print("Preprocessing...")

        df = pd.DataFrame(data['features'])
        commit_ids = df["_id"].to_list()
        df = df.loc[:, self.columns]

        return commit_ids, df

    def inference(self, model_input):
        if not self.initialized:
            self.initialize()

        output = self.model.predict_proba(model_input)[:, 1]
        return output

    def postprocess(self, commit_ids, inference_output):
        if not self.initialized:
            self.initialize()

        result = []
        for commit_id, output in zip(commit_ids, inference_output):
            json_obj = {'commit_hash': commit_id, 'predict': output}
            result.append(json_obj)

        return result

    def handle(self, data):
        if not self.initialized:
            self.initialize()

        commit_ids, preprocessed_data = self.preprocess(data)
        model_output = self.inference(preprocessed_data)
        final_prediction = self.postprocess(commit_ids, model_output)

        return final_prediction