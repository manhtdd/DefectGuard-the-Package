from .Repository import Repository
from .Dict import create_dict
from .utils import save_pkl, split_sentence, save_json, save_jsonl
from datetime import datetime
from operator import itemgetter
import time
import pandas as pd
import numpy as np
import os


class Processor:
    def __init__(self, save_path: str, save: bool = True):
        assert os.path.exists(save_path), f"Invalid save path: {save_path}"
        self.path = os.path.abspath(save_path)
        self.save = save

    def set_repo(self, repo: Repository):
        self.repo = repo
        self.repo_save_path = os.path.join(self.path, self.repo.owner, self.repo.name)
        self.feature_path = os.path.join(self.repo_save_path, "feature")
        self.commit_path = os.path.join(self.repo_save_path, "commit")
        self.df = None
        self.ids = None
        self.messages = None
        self.cc2vec_codes = None
        self.deepjit_codes = None
        self.simcom_codes = None
        self.labels = None

    def run(self, szz_output, extracted_date):
        self.create_dirs()
        szz_bug_ids_file_paths, szz_bug_ids_fix_commit_hashs = self.process_szz_output(szz_output)
        time_upper_limit = 0
        if szz_bug_ids_file_paths and szz_bug_ids_fix_commit_hashs:
            date_df = self.process_features(szz_bug_ids_file_paths, cols=["_id", "date"])
            time_median = self.cal_median_fix_time(szz_bug_ids_fix_commit_hashs, date_df)
            time_upper_limit = (
                datetime.strptime(extracted_date, "%Y-%m-%d").timestamp()
                if extracted_date
                else int(time.time())
            ) - time_median

        self.df = self.process_features(
            bug_ids=szz_bug_ids_file_paths, cols=[], time_upper_limit=time_upper_limit
        )
        self.process_diffs(szz_bug_ids_file_paths)
        if self.save:
            self.to_dataset()

    def create_dirs(self):
        """
        Create directories for storing data
        """
        if not os.path.exists(self.repo_save_path):
            os.makedirs(self.repo_save_path)
        if not os.path.exists(self.feature_path):
            os.mkdir(self.feature_path)
        if not os.path.exists(self.commit_path):
            os.mkdir(self.commit_path)

    def process_szz_output(self, szz_output):
        """
        Process szz output to get bug ids
        """
        szz_bug_ids_file_paths = {}
        szz_bug_ids_fix_commit_hashs = {}
        if szz_output:
            repo_name = szz_output[0]["repo_name"]
            assert repo_name == self.repo.name 
            f"Unmatch szz output vs repo's info: got {repo_name} and {self.repo.name}"
            for out in szz_output:
                if out["inducing_commit_hash"]:
                    for id in out["inducing_commit_hash"]:
                        if id['commit'] not in szz_bug_ids_file_paths:
                            szz_bug_ids_file_paths[id['commit']] = []
                        if id['commit'] not in szz_bug_ids_fix_commit_hashs:
                            szz_bug_ids_fix_commit_hashs[id['commit']] = []
                        szz_bug_ids_file_paths[id['commit']].append(id["file_path"])
                        szz_bug_ids_fix_commit_hashs[id['commit']].append(out["fix_commit_hash"])
        return szz_bug_ids_file_paths, szz_bug_ids_fix_commit_hashs

    def process_features(self, bug_ids, cols=[], time_upper_limit=None):
        """
        Convert features to dataframe, and add bug label
        """
        self.repo.load_features()        
        self.repo.features = sorted(self.repo.features, key=itemgetter('date'))

        if not cols:
            cols = [
                "_id",
                "date",
                "bug",
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
        data = {key: [] for key in cols}
        for feature in self.repo.features:
            if time_upper_limit and feature["date"] > time_upper_limit:
                continue
            for key in cols:
                if key == "bug":
                    data[key].append(1 if feature["_id"] in bug_ids else 0)
                else:
                    data[key].append(feature[key])
        self.repo.features = {}
        return pd.DataFrame(data)

    def cal_median_fix_time(self, bug_ids, date_df):
        """
        Calculate median fix time for each bug
        """
        fix_times = []
        for bug_id, metadata in bug_ids.items():
            if bug_id in date_df["_id"].values:
                bug_date = date_df[date_df["_id"] == bug_id]["date"].values[0]
                fix_dates = date_df[date_df["_id"].isin(metadata)]["date"].values
                for fix_date in fix_dates:
                    fix_time = fix_date - bug_date
                    fix_time = fix_time / 86400
                    fix_times.append(fix_time)
        time_median = np.median(fix_times)
        return time_median

    def process_diffs(self, bug_ids):
        """
        Process diffs to get format [ids, messages, codes, and labels]
        """
        cfg = self.repo.get_last_config()
        num_files = cfg["num_files"]

        self.ids = []
        self.date = []
        self.messages = []
        self.cc2vec_codes = []
        self.deepjit_codes = []
        self.simcom_codes = []
        self.labels = []
        self.change_labels = []
        self.change_files = []
        self.change_codes = {
            "_id": [], "date": [], "file_name": [], "added_code": [], "removed_code": [], "deepjit": [], "simcom": [], "bug": []
        }
        self.change_features = {
            "_id": [], "date": [], "file_name": [], "la": [], "ld": [], "lt": [], "bug": []
        }

        df_ids = self.df["_id"].values

        for i in range(num_files):
            self.repo.load_commits(i)
            for commit in self.repo.commits:
                if commit["commit_id"] not in df_ids:
                    continue
                (
                    id,
                    mes,
                    cc2vec_commit,
                    deepjit_commit,
                    simcom_commit,
                    change_files,
                ) = self.process_one_commit(commit)

                change_commit = self.process_one_change_commit(commit)
                date = self.df.loc[self.df['_id'] == id, 'date'].values[0]

                label = 1 if id in bug_ids else 0
                if id in bug_ids:
                    change_labels = []
                    for file in change_commit["change_features"]:
                        if file["file_name"] in bug_ids[id]:
                            change_labels.append(1)
                        else:
                            change_labels.append(0)
                else:
                    change_labels = [0 for _ in range(change_files)]
                self.ids.append(id)
                self.date.append(date)
                self.messages.append(mes)
                self.cc2vec_codes.append(cc2vec_commit)
                self.deepjit_codes.append(deepjit_commit)
                self.simcom_codes.append(simcom_commit)
                self.labels.append(label)
                self.change_labels.append(change_labels)
                self.change_files.append(change_files)

                for feature, code, _label in zip(change_commit["change_features"], change_commit["change_codes"], change_labels):
                    self.change_codes["_id"].append(id)
                    self.change_codes["date"].append(date)
                    self.change_features["_id"].append(id)
                    self.change_features["date"].append(date)
                    self.change_features["bug"].append(_label)
                    self.change_codes["bug"].append(_label)
                    for key, _ in code.items():
                        self.change_codes[key].append(code[key])
                    for key, _ in feature.items():
                        self.change_features[key].append(feature[key])
                
                del commit, id, mes, cc2vec_commit, deepjit_commit, simcom_commit, label, change_commit
        self.code_dict = create_dict(self.messages, self.deepjit_codes)
        

    def process_one_commit(self, commit):
        id = commit["commit_id"]
        mes = commit["message"].strip()
        mes = split_sentence(mes)
        mes = " ".join(mes.split(" ")).lower()
        cc2vec_commit = []
        deepjit_commit = []
        simcom_commit = []
        change_files = len(commit["files"])
        for file in commit["files"]:
            
            cc2vec_file = {"file_name": file, "added_code": [], "removed_code": []}
            for hunk in commit["diff"][file]["content"]:
                if "ab" in hunk:
                    continue
                if "a" in hunk:
                    for line in hunk["a"]:
                        line = line.strip()
                        line = split_sentence(line)
                        line = " ".join(line.split(" ")).lower()
                        if len(cc2vec_file["removed_code"]) <= 10:
                            cc2vec_file["removed_code"].append(line)
                        deepjit_commit.append(line)
                if "b" in hunk:
                    for line in hunk["b"]:
                        line = line.strip()
                        line = split_sentence(line)
                        line = " ".join(line.split(" ")).lower()
                        if len(cc2vec_file["added_code"]) <= 10:
                            cc2vec_file["added_code"].append(line)
                        deepjit_commit.append(line)
            deepjit_commit = deepjit_commit[:10]
            if len(cc2vec_commit) == 10:
                continue

            cc2vec_commit.append(cc2vec_file)
            added_code = " ".join(cc2vec_file["added_code"])
            removed_code = " ".join(cc2vec_file["removed_code"])
            simcom_commit.append(f"{added_code} {removed_code}")

        return id, mes, cc2vec_commit, deepjit_commit, simcom_commit, change_files

    def process_one_change_commit(self, commit):
        id = commit["commit_id"]
        change_commit = {"change_codes": [], "change_features": []}
        for file in commit["files"]:
            
            change_code = {
                "file_name": file, 
                "added_code": [], 
                "removed_code": [], 
                "deepjit": [],
                "simcom": []
            }

            change_feature = {
                "file_name": file,
                "la": 0, 
                "ld": 0,
                "lt": 0
            }

            change_feature["lt"] = commit["diff"][file]["meta_a"]["lines"]
            for hunk in commit["diff"][file]["content"]:
                if "ab" in hunk:
                    continue
                if "a" in hunk:
                    change_feature["ld"] += len(hunk["a"])
                    for line in hunk["a"]:
                        line = line.strip()
                        line = split_sentence(line)
                        line = " ".join(line.split(" ")).lower()
                        change_code["removed_code"].append(line)
                        change_code["deepjit"].append(line)
                if "b" in hunk:
                    change_feature["la"] += len(hunk["b"])
                    for line in hunk["b"]:
                        line = line.strip()
                        line = split_sentence(line)
                        line = " ".join(line.split(" ")).lower()
                        change_code["added_code"].append(line)
                        change_code["deepjit"].append(line)
                               
            added_code = " ".join(change_code["added_code"])
            removed_code = " ".join(change_code["removed_code"])
            change_code["simcom"].append(f"{added_code} {removed_code}")

            change_commit["change_codes"].append(change_code)
            change_commit["change_features"].append(change_feature)

        return change_commit

    def to_dataset(self):
        """
        Save processed data to dataset
        """
        self.df.to_csv(
            os.path.join(self.feature_path, "features.csv"),
            index=False,
        )

        dataframe = pd.DataFrame(self.change_features)
        dataframe.to_csv(
            os.path.join(self.feature_path, "change_features.csv"),
            index=False,
        )

        code_msg_dict = create_dict(self.messages, self.deepjit_codes)
        save_json(code_msg_dict, os.path.join(self.commit_path, "dict.json"))

        cc2vec_dict = [{
            "commit_id": self.ids[i],
            "messages": self.messages[i],
            "code_change": self.cc2vec_codes[i],
            "label": self.labels[i]
        } for i in range(len(self.ids))]
        save_jsonl(cc2vec_dict, os.path.join(self.commit_path, "cc2vec.jsonl"))
        
        deepjit_dict = [{
            "commit_id": self.ids[i],
            "messages": self.messages[i],
            "code_change": self.deepjit_codes[i],
            "label": self.labels[i]
        } for i in range(len(self.ids))]
        save_jsonl(deepjit_dict, os.path.join(self.commit_path, "deepjit.jsonl"))

        simcom_dict = [{
            "commit_id": self.ids[i],
            "messages": self.messages[i],
            "code_change": self.simcom_codes[i],
            "label": self.labels[i]
        } for i in range(len(self.ids))]
        save_jsonl(simcom_dict, os.path.join(self.commit_path, "simcom.jsonl"))
        
        change_deepjit_dict = [{
            "commit_id": self.change_codes["_id"][i],
            "file_path": self.change_codes["file_name"][i],
            "code_change": self.change_codes["deepjit"][i],
            "label": self.change_codes["bug"][i]
        } for i in range(len(self.ids))]
        save_jsonl(change_deepjit_dict, os.path.join(self.commit_path, "change_deepjit.jsonl"))

        change_simcom_dict = [{
            "commit_id": self.change_codes["_id"][i],
            "file_path": self.change_codes["file_name"][i],
            "code_change": self.change_codes["simcom"][i],
            "label": self.change_codes["bug"][i]
        } for i in range(len(self.ids))]
        save_jsonl(change_simcom_dict, os.path.join(self.commit_path, "change_simcom.jsonl"))
