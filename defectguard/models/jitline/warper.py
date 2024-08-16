from defectguard.models.BaseWraper import BaseWraper
from .model import JITLineModel
from defectguard.utils.utils import download_folder, SRC_PATH
import os, pickle

class JITLine(BaseWraper):
    def __init__(self, language):
        self.model_name = 'jitline'
        self.language = language
        self.initialized = False
        self.model = None
        download_folder(self.model_name, self.language)
        
    def initialize(self):
        self.model = JITLineModel(load_path=f"{SRC_PATH}/models/metadata/{self.model_name}/{self.language}_{self.project}")

        # Set initialized to True
        self.initialized = True

    def preprocess(self, data):
        if not self.initialized:
            self.initialize()
        print("Preprocessing...")

    def inference(self, model_input):
        if not self.initialized:
            self.initialize()
        print("Inferencing...")

    def postprocess(self, inference_output):
        if not self.initialized:
            self.initialize()
        print("Postprocessing...")

    def handle(self, data):
        if not self.initialized:
            self.initialize()
        print("Handling...")
        preprocessed_data = self.preprocess(data)
        model_output = self.inference(preprocessed_data)
        final_prediction = self.postprocess(model_output)

    def save(self, save_dir):
        if not os.path.isdir(save_dir):       
            os.makedirs(save_dir)
        
        save_path = f"{save_dir}/jitline.pkl"
        pickle.dump(self.model, open(save_path, "wb"))