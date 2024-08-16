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
        'gdown>=5.1.0',
        'icecream>=2.1.3',
        'imblearn>=0.0',
        'numpy>=1.24.4',
        'pandas>=2.0.3',
        'PyGithub>=2.1.1',
        'scikit_learn>=1.2.2',
        'scipy>=1.10.1',
        'setuptools>=67.8.0',
        'torch>=2.1.0',
        'GitPython>=3.1.7',
        'PyDriller>=1.15.2',
        'PyYAML>=5.3.1',
        'options>=1.4.10',
        'testresources>=2.0.1',
        'dateparser>=0.7.6',
        'networkx>=2.6.3',
        'beautifulsoup4>=4.10.0',
        'lxml>=4.6.4',
        'packaging>=21.3',
        'regex>=2022.1.18'
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