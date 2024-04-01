from .core import Repository, Extractor, Processor, PySZZ
from .core.utils import clone_repo


class BasicPipeline:
    def __init__(self, cfg):
        # init extractor
        self.create_dataset = False
        self.extractor = Extractor(
            num_commits_per_file=0,
            language=cfg.repo_language,
            save=cfg.extractor_save,
            check_uncommit=cfg.extractor_check_uncommit,
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
                cfg.dataset_save_path,
                cfg.processor_save,
            )
        else:
            self.create_dataset = False

    def set_repo(self, cfg):
        assert cfg.mode in ["local", "remote"], "Invalid mode: {}".format(cfg.mode)
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
        print("Running repository: {}/{}".format(self.repo.owner, self.repo.name))
        # extract repo
        self.extractor.set_repo(self.repo)
        self.extractor.run()
        
        if self.create_dataset:
            # run pyszz
            self.pyszz.set_repo(self.repo)
            self.pyszz.run()
            # process dataset
            self.processor.set_repo(self.repo)
            self.processor.run()
