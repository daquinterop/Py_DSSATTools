import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('/home/diego/Py_DSSATTools/requirements.txt', 'r') as f:
    requirements = [i.split('=')[0] for i in f.readlines()]

setuptools.setup(
    name="DSSATTools",
    version="1.0.0",
    author="Diego Quintero",
    author_email="daquinterop@gmail.com",
    description="A set of Tools to ease the crop simulation ussing DSSAT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daquinterop/Py_DSSATTools",
    project_urls={
        "Bug Tracker": "https://github.com/daquinterop/Py_DSSATTools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    licence='MIT',
    install_requires=requirements
)
