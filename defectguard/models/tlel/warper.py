from defectguard.models.BaseWraper import BaseWraper
import pickle, sys, os
from defectguard.utils.utils import download_folder, SRC_PATH
sys.path.append(f"{SRC_PATH}/models/tlel/model")
from .model.TLEL import TLEL
import pandas as pd

class TLELModel(BaseWraper):
    def __init__(self, language):
        self.model_name = 'tlel'
        self.language = language
        self.initialized = False
        self.model = TLEL()
        #self.columns = (["ns","nd","nf","entrophy","la","ld","lt","fix","ndev","age","nuc","exp","rexp","sexp"])
        self.columns = (["la","ld","lt"])
        download_folder(self.model_name, self.language)
        
    def initialize(self, pretrain=None):
        if pretrain:
            self.model = pickle.load(open(pretrain, "rb"))
        else:
            self.model = pickle.load(open(f"{SRC_PATH}/models/metadata/{self.model_name}/{self.language}", "rb"))

        # Set initialized to True
        self.initialized = True

    def preprocess(self, data):
        if not self.initialized:
            self.initialize()
        print("Preprocessing...")

        feature_table = []
        for datapoint in data:
            for pull_number, files in datapoint.items():
                for file_name, file_content in files.items():
                    row = {}
                    row['pull_number'] = pull_number
                    row['file_name'] = file_name
                    row.update(file_content['feature'])
                    feature_table.append(row)

        df = pd.DataFrame(feature_table)
        pull_number = df.loc[:, ["pull_number", "file_name"]]
        pull_number = list(pull_number.itertuples(index=False, name=None))
        df = df.loc[:, self.columns]

        return pull_number, df

    def inference(self, model_input):
        if not self.initialized:
            self.initialize()

        output = self.model.predict_proba(model_input)[:, 1]
        return output

    def postprocess(self, pull_number, inference_output):
        if not self.initialized:
            self.initialize()

        result = []
        for pull_info, output in zip(pull_number, inference_output):
            json_obj = {'pull_number': pull_info[0], 'file_name': pull_info[1], 'predict': output}
            result.append(json_obj)

        return result

    def handle(self, data):
        if not self.initialized:
            self.initialize()

        pull_number, preprocessed_data = self.preprocess(data)
        model_output = self.inference(preprocessed_data)
        final_prediction = self.postprocess(pull_number, model_output)

        return final_prediction

    def predict_proba(self, test):
        if not self.initialized:
            self.initialize()
            
        return self.model.predict_proba(test)

    def save(self, save_dir):
        if not os.path.isdir(save_dir):       
            os.makedirs(save_dir)
        
        save_path = f"{save_dir}/tlel.pkl"
        pickle.dump(self.model, open(save_path, "wb"))