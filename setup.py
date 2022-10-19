import setuptools
import os 
import pdb

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
pdb.set_trace()
with open(os.path.abspath('requirements.txt'), 'r') as f:
    requirements = [i.split('=')[0] for i in f.readlines()]

setuptools.setup(
    name="DSSATTools",
    version="2.0.0",
    author="Diego Quintero",
    author_email="daquinterop@gmail.com",
    description="A DSSAT's Python implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daquinterop/Py_DSSATTools",
    project_urls={
        "Bug Tracker": "https://github.com/daquinterop/Py_DSSATTools/issues",
        "Documentation": "https://py-dssattools.readthedocs.io/en/latest/"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=[
        'DSSATTools', 
        
        'DSSATTools.static', 'DSSATTools.static.bin', 
        'DSSATTools.static.Genotype', 'DSSATTools.static.Pest', 
        'DSSATTools.static.StandardData', 'DSSATTools.static.Soil', 
        
        'DSSATTools.models', 'DSSATTools.base'
        ],
    python_requires=">=3.6",
    license='MIT',
    install_requires=requirements,
    package_data = {
        'DSSATTools.static.Genotype': ['*'],
        'DSSATTools.static.Pest': ['*'],
        'DSSATTools.static.StandardData': ['*'],
        'DSSATTools.static.Soil': ['*'],
        'DSSATTools.static.bin': ['dscsm048'],
        'DSSATTools.static': ['*.CDE']
    },
    # include_package_data=True
)
#