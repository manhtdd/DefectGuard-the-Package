from .Processor import Processor
from .Dict import create_dict
from .utils import save_pkl
from defectguard.utils.logger import logger
import numpy as np
import pandas as pd
import os, sys


class Splitter:
    def __init__(self, save_path: str):
        self.path = os.path.abspath(save_path)

    def set_processor(self, processor: Processor):
        self.processor = processor

    def run(self):
        train_test_ratio = 4/1
        val_train_ratio = 5/75
        self.split_data(train_test_ratio, val_train_ratio)

    def split_train_test_indexes(self, size, train_test_ratio):
        """
        Split a numpy array of indexes from 0 to `size`-1 into train and test indexes
        based on the ratio `train_test_ratio`=train_size/test_size
        """
        indexes = np.arange(size)
        partition = int(size * train_test_ratio / (train_test_ratio + 1))
        train_indexes = indexes[:partition]
        assert (
            train_indexes == np.sort(train_indexes)
        ).all(), "Train indexes are not sorted"
        test_indexes = indexes[partition:]
        assert (
            test_indexes == np.sort(test_indexes)
        ).all(), "Test indexes are not sorted"
        return {
            "train": train_indexes,
            "test": test_indexes,
        }

    def split_train_val_indexes(self, indexes, val_train_ratio=5 / 75):
        """
        Randomly split train indexes into train and val indexes 
        based on the ratio `val_train_ratio`=val_size/train_size
        """
        val_indexes = np.random.choice(
            indexes["train"],
            int(len(indexes["train"]) * val_train_ratio),
            replace=False,
        )
        val_indexes = np.sort(val_indexes)
        train_indexes = np.setdiff1d(indexes["train"], val_indexes)
        assert (
            train_indexes == np.sort(train_indexes)
        ).all(), "Train indexes are not sorted"
        indexes["val"] = val_indexes
        indexes["train"] = train_indexes
        return indexes
    

    def get_values(self, arr, indexes):
        return [arr[i] for i in indexes]

    def split_data(self, train_test_ratio, val_train_ratio):
        """
        Split the processed dataset into train, val, and test sets
        based on the `train_test_ratio` and `val_train_ratio`
        """
        name = self.processor.repo.name
        indexes = self.split_train_test_indexes(len(self.processor.df), train_test_ratio)
        
        # split features
        for key in indexes:
            splitted_df = self.processor.df.iloc[indexes[key]]
            splitted_df.to_csv(
                os.path.join(self.processor.feature_path, f"{name}_{key}.csv"),
                index=False,
            )
            del splitted_df
        if val_train_ratio:
            indexes = self.split_train_val_indexes(indexes, val_train_ratio)
        # split cc2vec and deepjit codes
        for key in indexes:
            save_part = f"{name}_{key}"
            ids = self.get_values(self.processor.ids, indexes[key])
            messages = self.get_values(self.processor.messages, indexes[key])
            cc2vec_codes = self.get_values(self.processor.cc2vec_codes, indexes[key])
            deepjit_codes = self.get_values(self.processor.deepjit_codes, indexes[key])
            simcom_codes = self.get_values(self.processor.simcom_codes, indexes[key])
            labels = self.get_values(self.processor.labels, indexes[key])
            if key == "train":
                train_dict = create_dict(messages, deepjit_codes)
                save_pkl(
                    train_dict,
                    os.path.join(self.processor.commit_path, f"{save_part}_dict.pkl"),
                )
            save_pkl(
                [ids, messages, cc2vec_codes, labels],
                os.path.join(self.processor.commit_path, f"cc2vec_{save_part}.pkl"),
            )
            save_pkl(
                [ids, messages, deepjit_codes, labels],
                os.path.join(self.processor.commit_path, f"deepjit_{save_part}.pkl"),
            )
            save_pkl(
                [ids, messages, simcom_codes, labels],
                os.path.join(self.processor.commit_path, f"simcom_{save_part}.pkl"),
            )
        
        def get_change_indexes(commit_size, files_size, train_test_ratio, val_train_ratio):
            train_all_ratio = 1 / (1 + val_train_ratio + 1 / train_test_ratio)
            val_all_ratio = 1 / (1 + 1 / val_train_ratio + 1 / (val_train_ratio * train_test_ratio))
            test_all_ratio = 1 - train_all_ratio - val_all_ratio
            commit_ids = np.arange(commit_size)
            sizes = {
                "train": round(files_size * train_all_ratio),
                "val": round(files_size * val_all_ratio),
                "test": round(files_size * test_all_ratio)
            }
            indexes = {
                "train": [],
                "val": [],
                "test": []
            }
            
            for key in ["train", "val", "test"]:
                index = indexes[key]
                file_count = 0
                for id in commit_ids:
                    index.append(id)
                    file_count += self.processor.change_files[id]
                    if file_count >= sizes[key]:
                        commit_ids = commit_ids[id+1:]
                        break
            return indexes

        #split change data by id:commit:
        def change_level_split(indexes, prefix):
            for key in indexes:
                save_part = f"{prefix}_{name}_{key}"
                ids = self.get_values(self.processor.ids, indexes[key])
                date = self.get_values(self.processor.date, indexes[key])
                labels = self.get_values(self.processor.labels, indexes[key])

                change_codes = {
                    "_id": [], "date": [], "file_name": [], "added_code": [], "removed_code": [], "deepjit": [], "simcom": [], "bug": []
                }
                change_features = {
                    "_id": [], "date": [], "file_name": [], "la": [], "ld": [], "lt": [], "bug": []
                }

                for index, id in enumerate(self.processor.change_codes["_id"]):
                    if id in ids:
                        for key in self.processor.change_codes:
                            change_codes[key].append(self.processor.change_codes[key][index])

                for index, id in enumerate(self.processor.change_features["_id"]):
                    if id in ids:
                        for key in self.processor.change_features:
                            change_features[key].append(self.processor.change_features[key][index])
                
                df1 = pd.DataFrame(
                    {
                        "_id": ids,
                        "date": date,
                        "bug": labels
                    } 
                )
                df1.to_csv(
                    os.path.join(self.processor.feature_path, f"labels_{save_part}.csv"),
                    index=False
                )

                df2 = pd.DataFrame(
                    change_features
                )
                # df2 = pd.merge(df2, df1, on=["_id", "date"], how="outer")
                df2.to_csv(
                    os.path.join(self.processor.feature_path, f"change_features_{save_part}.csv"),
                    index=False
                )
                del df1, df2

                save_pkl(
                    [
                        change_codes["_id"], 
                        change_codes["file_name"], 
                        change_codes["deepjit"],
                        change_codes["bug"]
                    ],
                    os.path.join(self.processor.commit_path, f"change_codes_deepjit_{save_part}.pkl")
                )

                save_pkl(
                    [
                        change_codes["_id"], 
                        change_codes["file_name"], 
                        change_codes["simcom"],
                        change_codes["bug"]
                    ],
                    os.path.join(self.processor.commit_path, f"change_codes_simcom{save_part}.pkl")
                )
        indexes = get_change_indexes(len(self.processor.ids), len(self.processor.labels), train_test_ratio, val_train_ratio)
        change_level_split(indexes, "")
        
        #split by files:
        # indexes = self.split_train_test_indexes(len(self.processor.labels), train_test_ratio)
        # if val_train_ratio:
        #     indexes = self.split_train_val_indexes(indexes, val_train_ratio)
        # change_level_split(indexes, "files")
                
