import logging
import os
import yaml
from .utils import exec_cmd, load_json, load_jsonl, LANG2EXT


class PySZZ:
    def __init__(
        self,
        pyszz_path: str,
        # log_path: str = "log",
        pyszz_conf: str = "bszz",
        workers: int = 1,
    ):
        """
        Wrapper for PySZZ from https://github.com/grosa1/pyszz_v2
        """
        assert os.path.exists(pyszz_path), "PySZZ: Path not found: {}".format(
            pyszz_path
        )
        self.path = os.path.abspath(pyszz_path)
        # self.log_path = os.path.abspath(log_path)
        self.set_conf(pyszz_conf)
        self.pyszz_conf = pyszz_conf
        self.workers = workers

    def set_conf(self, conf="bszz"):
        valid_conf = list(
            map(lambda x: x[:-4], os.listdir(os.path.join(self.path, "conf")))
        )
        assert conf in valid_conf, "PySZZ: Invalid type: {}".format(valid_conf)
        self.conf = conf
        with open(os.path.join(self.path, "conf", conf + ".yml"), "r") as f:
            self.base_conf = yaml.load(f, Loader=yaml.FullLoader)

    def run(self, bug_fix_path, szz_conf_path, repo_path, repo_language):
        # logging.basicConfig(
        #     filename=os.path.join(self.log_path, "pyszz_log.log"),
        #     level=logging.DEBUG,
        #     format="%(asctime)s %(message)s",
        #     filemode="w",
        # )
        cur_dir = os.getcwd()
        os.chdir(self.path)

        # modify config file
        conf = self.base_conf
        if repo_language:
            conf["file_ext_to_parse"] = list(
                map(lambda x: LANG2EXT[x][1:], repo_language)
            )

        with open(szz_conf_path, "w") as f:
            yaml.dump(conf, f)

        # run pyszz
        cmd = "python3 main.py {} {} {} {}".format(bug_fix_path, szz_conf_path, repo_path, self.workers)
        out = exec_cmd(cmd)
        # print(cmd)
        ## debug
        # print(out)
        
        os.chdir(cur_dir)

    def get_output(self, repo_name):
        out_file = os.path.join(self.path, "out", f"bic_{self.pyszz_conf}_{repo_name}.jsonl")
        data = load_jsonl(out_file)
        if data[0]["repo_name"] == repo_name:
            return data
        raise FileNotFoundError("PySZZ: No output found for {}/{}".format(repo_owner, repo_name))
