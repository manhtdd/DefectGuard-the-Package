from .core import Repository, Extractor, Processor, PySZZ, Splitter
from .core.utils import clone_repo
import os


class BasicPipeline:
    def __init__(self, cfg):
        # init extractor
        self.create_dataset = False
        self.extractor = Extractor(
            num_commits_per_file=0,
            language=cfg.repo_language,
            save=cfg.extractor_save,
            check_uncommit=cfg.extractor_check_uncommit,
            force_reextract=cfg.extractor_reextract,
        )

        if cfg.create_dataset:
            self.create_dataset = True
            # init pyszz
            self.pyszz = PySZZ(
                pyszz_path=cfg.pyszz_path,
                keep_output=20,
                pyszz_conf="bszz",
            )

            # init processor
            self.processor = Processor(
                save_path=cfg.dataset_save_path,
                save=cfg.processor_save,
            )
            
            self.splitter = Splitter(save_path=cfg.dataset_save_path)
        else:
            self.create_dataset = False

    def set_repo(self, cfg):
        assert cfg.mode in ["local", "remote"], "[Pipeline] Invalid mode: {}".format(cfg.mode)
        if cfg.mode == "local":
            self.repo = self.local_repo(cfg)
        else:
            self.repo = self.remote_repo(cfg)

    def local_repo(self, cfg):
        repo = Repository(
            cfg.repo_owner,
            cfg.repo_name,
            cfg.repo_save_path,
            cfg.repo_path,
            cfg.repo_language,
        )
        return repo

    def remote_repo(self, cfg):
        clone_repo(
            cfg.repo_clone_path,
            cfg.repo_owner,
            cfg.repo_name,
            cfg.repo_clone_url,
        )
        repo = Repository(
            cfg.repo_owner,
            cfg.repo_name,
            cfg.repo_save_path,
            cfg.repo_clone_path,
            cfg.repo_language,
        )
        return repo

    def run(self):
        print(
            "Running on repository: {}\n\tat: {}".format(
                os.path.join(self.repo.owner, self.repo.name), self.repo.get_repo_path()
            )
        )
        # extract repo
        self.extractor.set_repo(self.repo)
        self.extractor.run()

        if self.create_dataset:
            # run pyszz
            self.pyszz.run(
                bug_fix_path=self.repo.get_bug_fix_path(),
                szz_conf_path=self.repo.get_pyszz_conf_path(),
                repo_path=self.repo.get_repo_path(),
                repo_language=self.repo.get_language(),
            )
            szz_output = self.pyszz.get_lastest_output(
                repo_owner=self.repo.owner,
                repo_name=self.repo.name,
            )

            # process dataset
            self.processor.set_repo(repo=self.repo)
            self.processor.run(
                szz_output=szz_output,
                extracted_date=self.extractor.end,
            )
            
            # split processed dataset into train, val, test set
            self.splitter.set_processor(self.processor)
            self.splitter.run()
