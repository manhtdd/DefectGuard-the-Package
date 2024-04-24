import os, torch, pickle
from torch.utils.data import Dataset, DataLoader
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel as TLEL,
    JITLine,
)
from .utils.padding import padding_data
from .utils.logger import logger, logs
from tqdm import tqdm
import pandas as pd
from sklearn.metrics import roc_auc_score
from datetime import datetime

def init_model(model_name, language, device):
    match model_name:
        case "deepjit":
            return DeepJIT(language=language, device=device)
        case "cc2vec":
            return CC2Vec(language=language, device=device)
        case "simcom":
            return SimCom(language=language, device=device)
        case "lapredict":
            return LAPredict(language=language)
        case "tlel":
            return TLEL(language=language)
        case "jitline":
            return JITLine(language=language)
        case "lr":
            return LogisticRegression(language=language)
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
    
def evaluating_deep_learning(pretrain, params, dg_cache_path):
    # Init model
    model = init_model(params.model, params.repo_language, params.device)
    model.initialize(dictionary=f'{dg_cache_path}/dataset/{params.repo_name}/commit/dict.pkl', state_dict=f'{dg_cache_path}/save/{params.repo_name}/{pretrain}')

    # Load dataset
    loaded_data = pickle.load(open(f'{dg_cache_path}/dataset/{params.repo_name}/commit/{params.model}.pkl', 'rb'))
    ids, messages, commits, labels = loaded_data

    dictionary = pickle.load(open(f'{dg_cache_path}/dataset/{params.repo_name}/commit/dict.pkl', 'rb'))   
    dict_msg, dict_code = dictionary

    pad_msg = padding_data(data=messages, dictionary=dict_msg, params=model.hyperparameters, type='msg')        
    pad_code = padding_data(data=commits, dictionary=dict_code, params=model.hyperparameters, type='code')

    code_dataset = CustomDataset(ids, pad_code, pad_msg, labels)
    code_dataloader = DataLoader(code_dataset, batch_size=1)

    if model.model_name == "simcom":
        model.com.eval()    
    else:
        model.model.eval()
    with torch.no_grad():
        commit_hashes, all_predict, all_label = [], [], []
        for batch in tqdm(code_dataloader):
            # Extract data from DataLoader
            commit_hashes.append(batch['commit_hash'][0])
            code = batch["code"].to(params.device)
            message = batch["message"].to(params.device)
            labels = batch["labels"].to(params.device)

            # Forward
            predict = model(message, code)
            all_predict += predict.cpu().detach().numpy().tolist()
            all_label += labels.cpu().detach().numpy().tolist()

    return commit_hashes, all_predict, all_label

def evaluating_machine_learning(pretrain, params, dg_cache_path):
    test_df_path = f'{dg_cache_path}/dataset/{params.repo_name}/feature/features.csv'
    test_df = pd.read_csv(test_df_path)
    model = init_model(params.model, params.repo_language, params.device)
    model.initialize(pretrain=f'{dg_cache_path}/save/{params.repo_name}/{pretrain}')

    cols = (
        ["la"]
        if model.model_name == "lapredict"
        else [
            "ns",
            "nd",
            "nf",
            "entropy",
            "la",
            "ld",
            "lt",
            "fix",
            "ndev",
            "age",
            "nuc",
            "exp",
            "rexp",
            "sexp",
        ]
    )
    commit_hashes = test_df.loc[:, "_id"].to_list()
    X_test = test_df.loc[:, cols]
    y_test = test_df.loc[:, "bug"]

    y_proba = model.predict_proba(X_test)[:, 1]

    return commit_hashes, y_proba, y_test
        
def get_pretrain(model_name):
    match model_name:
        case "deepjit":
            return "deepjit.pt"
        case "sim":
            return "sim.pkl"
        case "com":
            return "com.pt"
        case "lapredict":
            return "lapredict.pkl"
        case "lr":
            return "lr.pkl"
        case "tlel":
            return "tlel.pkl"
        case _:
            raise Exception("No such model")
        
def average(proba_1, proba_2):
    if len(proba_1) != len(proba_2):
        raise ValueError("Both lists must be of the same length")
    return [(x + y) / 2 for x, y in zip(proba_1, proba_2)]

def evaluating(params):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    # create save folders
    dg_cache_path = f"{params.dg_save_folder}/dg_cache"
    folders = ["save", "repo", "dataset"]
    if not os.path.exists(dg_cache_path):
        os.mkdir(dg_cache_path)
    for folder in folders:
        if not os.path.exists(os.path.join(dg_cache_path, folder)):
            os.mkdir(os.path.join(dg_cache_path, folder))

    if params.model in ["deepjit", "simcom"]:
        model_name = params.model if params.model != "simcom" else "com"
        pretrain = get_pretrain(model_name)
        com_hashes, com_proba, com_ground_truth = evaluating_deep_learning(pretrain, params, dg_cache_path)
        sim_auc_score = roc_auc_score(y_true=com_ground_truth,  y_score=com_proba)

        if os.path.isdir(f'{dg_cache_path}/save/{params.repo_name}/results/') is False:
            os.makedirs(f'{dg_cache_path}/save/{params.repo_name}/results/')
        logs(f'{dg_cache_path}/save/{params.repo_name}/results/auc.csv', params.repo_name, sim_auc_score, model_name)

        df = pd.DataFrame({'commit_hash': com_hashes, 'label': com_ground_truth, 'pred': com_proba})
        if os.path.isdir(f'{dg_cache_path}/save/{params.repo_name}/predict_scores/') is False:
            os.makedirs(f'{dg_cache_path}/save/{params.repo_name}/predict_scores/')
        df.to_csv(f'{dg_cache_path}/save/{params.repo_name}/predict_scores/{model_name}.csv', index=False, sep=',')

    if params.model in ["lapredict", "lr", "tlel", "simcom"]:
        model_name = params.model if params.model != "simcom" else "sim"
        pretrain = get_pretrain(model_name)
        sim_hashes, sim_proba, sim_ground_truth = evaluating_machine_learning(pretrain, params, dg_cache_path)
        com_auc_score = roc_auc_score(y_true=sim_ground_truth,  y_score=sim_proba)

        if os.path.isdir(f'{dg_cache_path}/save/{params.repo_name}/results/') is False:
            os.makedirs(f'{dg_cache_path}/save/{params.repo_name}/results/')
        logs(f'{dg_cache_path}/save/{params.repo_name}/results/auc.csv', params.repo_name, com_auc_score, model_name)

        df = pd.DataFrame({'commit_hash': sim_hashes, 'label': sim_ground_truth, 'pred': sim_proba})
        if os.path.isdir(f'{dg_cache_path}/save/{params.repo_name}/predict_scores/') is False:
            os.makedirs(f'{dg_cache_path}/save/{params.repo_name}/predict_scores/')
        df.to_csv(f'{dg_cache_path}/save/{params.repo_name}/predict_scores/{model_name}.csv', index=False, sep=',')
    
    if params.model in ["simcom"]:
        assert com_hashes == sim_hashes
        simcom_proba = average(sim_proba, com_proba)
        auc_score = roc_auc_score(y_true=com_ground_truth,  y_score=simcom_proba)

        if os.path.isdir(f'{dg_cache_path}/save/{params.repo_name}/results/') is False:
            os.makedirs(f'{dg_cache_path}/save/{params.repo_name}/results/')
        logs(f'{dg_cache_path}/save/{params.repo_name}/results/auc.csv', params.repo_name, auc_score, params.model)