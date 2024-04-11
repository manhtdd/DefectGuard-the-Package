import os, torch, pickle
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel,
    JITLine,
)
from .utils.padding import padding_data

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
    model.initialize(dictionary=f'{dg_cache_path}/dataset/{params.repo_name}/commit/dict.pkl')

    # Load dataset
    loaded_data = pickle.load(open(f'{dg_cache_path}/dataset/{params.repo_name}/commit/{params.model}.pkl', 'rb'))
    ids, messages, commits, labels = loaded_data

    dictionary = pickle.load(open(f'{dg_cache_path}/dataset/{params.repo_name}/commit/dict.pkl', 'rb'))   
    dict_msg, dict_code = dictionary

    pad_msg = padding_data(data=messages, dictionary=dict_msg, params=model.hyperparameters, type='msg')        
    pad_code = padding_data(data=commits, dictionary=dict_code, params=model.hyperparameters, type='code')

    code_dataset = CustomDataset(ids, pad_code, pad_msg, labels)
    code_dataloader = DataLoader(code_dataset, batch_size=model.hyperparameters['batch_size'])

    optimizer = torch.optim.Adam(model.get_parameters(), lr=5e-5)
    criterion = nn.BCELoss()

    for epoch in range(1, params.epochs + 1):
        total_loss = 0
        for batch in code_dataloader:
            # Extract data from DataLoader
            code = batch["code"].to(model.device)
            message = batch["message"].to(model.device)
            labels = batch["labels"].to(model.device)

            optimizer.zero_grad()

            # ---------------------- DefectGuard -------------------------------
            predict = model(message, code)
            # ------------------------------------------------------------------
            
            loss = criterion(predict, labels)
            loss.backward()
            total_loss += loss
            optimizer.step()

        print(f'Training: Epoch {epoch} / {params.epochs} -- Total loss: {total_loss}')