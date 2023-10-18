from glob import glob
from setuptools import find_packages, setup
from os.path import splitext, basename


setup(
    name='goalplan',
    version='0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires=[
        "google-cloud-storage==2.12.0",
        "requests==2.31.0",
    ],
)
