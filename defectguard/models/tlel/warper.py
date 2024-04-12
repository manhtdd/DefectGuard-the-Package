from defectguard.models.BaseWraper import BaseWraper
import pickle, sys, os
from defectguard.utils.utils import download_folder, SRC_PATH
sys.path.append(f"{SRC_PATH}/models/tlel/model")
from .model.TLEL import TLEL

class TLELModel(BaseWraper):
    def __init__(self, language='cpp', device="cpu"):
        self.model_name = 'tlel'
        self.language = language
        self.initialized = False
        self.model = None
        self.device = device
        download_folder(self.model_name, self.language)
        
    def initialize(self):
        with open(f"{SRC_PATH}/models/metadata/{self.model_name}/{self.language}", "rb") as f:
            self.model = pickle.load(f)

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
        
        save_path = f"{save_dir}/tlel.pkl"
        pickle.dump(self.model, open(save_path, "wb"))