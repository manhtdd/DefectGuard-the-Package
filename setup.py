from setuptools import setup, find_packages
from defectguard.cli import __version__

VERSION = __version__
DESCRIPTION = 'A cutting-edge defect prediction tool with up-to-date Just-in-Time techniques and a robust API, empowering software development teams to proactively identify and mitigate defects in real-time'

# Setting up
setup(
    name="defectguard",
    version=VERSION,
    author="manhtd",
    author_email="manh.td194616@sis.hust.edu.vn",
    description=DESCRIPTION,
    packages=find_packages(),
    package_data={
        "defectguard.utils": ["*.json", "*.pkl"],
        "defectguard.models.jitline": ["*.pkl"],
    },
    dependency_links = [
        "https://download.pytorch.org/whl/torch_stable.html"
    ],
    install_requires=[
        'numpy==1.26.2',
        'pandas==2.1.4',
        'PyGithub==2.1.1',
        'scikit_learn==1.3.2',
        'torch==2.1.0+cpu',
        'imblearn==0.0',
        'scipy==1.11.4',
        'gdown==4.7.1',
        'icecream==2.1.3'
        ],
    keywords=['python', 'defect', 'prediction', 'just-in-time', 'defect prediction'],
    entry_points={
        'console_scripts': ['defectguard=defectguard:main'],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)