import os, torch, pickle
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel as TLEL,
    JITLine,
)
from sklearn.linear_model import LogisticRegression as sk_LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from imblearn.under_sampling import RandomUnderSampler
from .utils.padding import padding_data
from tqdm import tqdm
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
import numpy as np
import pandas as pd

def auc_pc(label, pred):
    lr_probs = np.array(pred)
    testy = np.array([float(l) for l in label])
    lr_precision, lr_recall, _ = precision_recall_curve(testy, lr_probs)
    lr_auc = auc(lr_recall, lr_precision)
    return lr_auc

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
    
def training_deep_learning(params, dg_cache_path):
    commit_path = f'{dg_cache_path}/dataset/{params.repo_name}/commit'
    dictionary_path = f'{commit_path}/{params.repo_name}_train_dict.pkl' if params.dictionary is None else params.dictionary
    train_set_path = f'{commit_path}/{params.model}_{params.repo_name}_train.pkl' if params.commit_train_set is None else params.commit_train_set
    val_set_path = f'{commit_path}/{params.model}_{params.repo_name}_val.pkl' if params.commit_val_set is None else params.commit_val_set
    model_save_path = f'{dg_cache_path}/save/{params.repo_name}'

    # Init model
    model = init_model(params.model, params.repo_language, params.device)
    if params.from_pretrain:
        model.initialize()
    else:
        model.initialize(dictionary=dictionary_path)

    # Load dataset
    loaded_data = pickle.load(open(train_set_path, 'rb'))
    ids, messages, commits, labels = loaded_data

    if params.model == "simcom":
        val_data = pickle.load(open(val_set_path, 'rb'))
        val_ids, val_messages, val_codes, val_labels = val_data

    dict_msg, dict_code = model.message_dictionary, model.code_dictionary

    pad_msg = padding_data(data=messages, dictionary=dict_msg, params=model.hyperparameters, type='msg')        
    pad_code = padding_data(data=commits, dictionary=dict_code, params=model.hyperparameters, type='code')

    if params.model == "simcom":
        val_pad_msg = padding_data(data=val_messages, dictionary=dict_msg, params=model.hyperparameters, type='msg')        
        val_pad_code = padding_data(data=val_codes, dictionary=dict_code, params=model.hyperparameters, type='code')

    code_dataset = CustomDataset(ids, pad_code, pad_msg, labels)
    code_dataloader = DataLoader(code_dataset, batch_size=model.hyperparameters['batch_size'])

    if params.model == "simcom":
        val_code_dataset = CustomDataset(val_ids, val_pad_code, val_pad_msg, val_labels)
        val_code_dataloader = DataLoader(val_code_dataset, batch_size=model.hyperparameters['batch_size'])

    optimizer = torch.optim.Adam(model.get_parameters(), lr=params.learning_rate)
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

        # Validate
        best_valid_score = 0
        smallest_loss = 1000000
        early_stop_count = 5

        if params.model == "simcom":
            model.com.eval()
            with torch.no_grad():
                all_predict, all_label = [], []
                for batch in tqdm(val_code_dataloader):
                    # Extract data from DataLoader
                    code = batch["code"].to(params.device)
                    message = batch["message"].to(params.device)
                    labels = batch["labels"].to(params.device)

                    # Forward
                    predict = model(message, code)
                    all_predict += predict.cpu().detach().numpy().tolist()
                    all_label += labels.cpu().detach().numpy().tolist()

            auc_score = roc_auc_score(y_true=all_label,  y_score=all_predict)
            auc_pc_score = auc_pc(all_label, all_predict)
            print('Valid data -- AUC-ROC score:', auc_score,  ' -- AUC-PC score:', auc_pc_score)

            valid_score = auc_pc_score
            if valid_score > best_valid_score:
                best_valid_score = valid_score
                print('Save a better model', best_valid_score.item())
                model.save(f'{dg_cache_path}/save/{params.repo_name}')
            else:
                print('No update of models', early_stop_count)
                if epoch > 5:
                    early_stop_count = early_stop_count - 1
                if early_stop_count < 0:
                    break
        else:
            loss_score = total_loss
            if loss_score < smallest_loss:
                smallest_loss = loss_score
                print('Save a better model', smallest_loss.item())
                model.save(model_save_path)
            else:
                print('No update of models', early_stop_count)
                if epoch > 5:
                    early_stop_count = early_stop_count - 1
                if early_stop_count < 0:
                    break

def training_machine_learning(params, dg_cache_path):
    train_df_path = f'{dg_cache_path}/dataset/{params.repo_name}/feature/{params.repo_name}_train.csv' if params.feature_train_set is None else params.feature_train_set
    train_df = pd.read_csv(train_df_path)
    model = init_model(params.model, params.repo_language, params.device)

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
    X_train = train_df.loc[:, cols]
    y_train = train_df.loc[:, "bug"]

    match model.model_name:
        case "simcom":
            X_train, y_train = RandomUnderSampler(random_state=42).fit_resample(X_train, y_train)
            model.sim = RandomForestClassifier()
            model.sim.fit(X_train, y_train)
            model.save_sim(f'{dg_cache_path}/save/{params.repo_name}')
        case "lapredict" | "lr":
            model.model = sk_LogisticRegression(class_weight='balanced', max_iter=1000)
            model.model.fit(X_train, y_train)
            model.save(f'{dg_cache_path}/save/{params.repo_name}')
        case "tlel":
            model.model.fit(X_train, y_train)
            model.save(f'{dg_cache_path}/save/{params.repo_name}')
            pass
        case _:
            raise Exception("No such model")

def training(params):
    # create save folders
    dg_cache_path = f"{params.dg_save_folder}/dg_cache"
    folders = ["save", "repo", "dataset"]
    if not os.path.exists(dg_cache_path):
        os.mkdir(dg_cache_path)
    for folder in folders:
        if not os.path.exists(os.path.join(dg_cache_path, folder)):
            os.mkdir(os.path.join(dg_cache_path, folder))

    if params.model in ["deepjit", "simcom"]:
        training_deep_learning(params, dg_cache_path)

    if params.model in ["lapredict", "lr", "tlel", "simcom"]:
        training_machine_learning(params, dg_cache_path)

    