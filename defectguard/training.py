import os, torch
from torch.utils.data import Dataset, DataLoader
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel,
    JITLine,
)

def init_model(model_name, device):
    match model_name:
        case "deepjit":
            return DeepJIT(device=device)
        case "cc2vec":
            return CC2Vec(device=device)
        case "simcom":
            return SimCom(device=device)
        case "lapredict":
            return LAPredict(device=device)
        case "tlel":
            return TLELModel(device=device)
        case "jitline":
            return JITLine(device=device)
        case "la":
            return LAPredict(device=device)
        case "lr":
            return LogisticRegression(device=device)
        case _:
            raise Exception("No such model")

class CustomDataset(Dataset):
    def __init__(self, ids, code, message, labels):
        self.ids = ids
        self.code = code
        self.message = message
        self.labels = labels
    
    def __len__(self):
        return len(self.code)
    
    def __getitem__(self, idx):
        commit_hash = self.ids[idx]
        labels = torch.tensor(self.labels[idx], dtype=torch.float32)
        code = self.code[idx]
        message = self.message[idx]
        code = torch.tensor(code)
        message = torch.tensor(message)

        return {
            'commit_hash': commit_hash,
            'code': code,
            'message': message,
            'labels': labels
        }

def training(params):
    # create save folders
    dg_cache_path = f"{params.dg_save_folder}/dg_cache"
    folders = ["save", "repo", "dataset"]
    if not os.path.exists(dg_cache_path):
        os.mkdir(dg_cache_path)
    for folder in folders:
        if not os.path.exists(os.path.join(dg_cache_path, folder)):
            os.mkdir(os.path.join(dg_cache_path, folder))

    # Init model
    model = init_model(params.model, params.device)
    print(model)