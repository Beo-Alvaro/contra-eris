from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="contra-eris",
    version="0.1.0",
    author="Beo Alvaro Edep Salguero",
    author_email="beoalvarosalguero@gmail.com",
    description="A system for generating and evaluating Compressed Base Summary Files (CBSF) of codebases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Beo-Alvaro/contra-eris.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "matplotlib>=3.5.0",
        "networkx>=2.7.0", 
        "numpy>=1.20.0",
        "beautifulsoup4>=4.11.0",
        "esprima>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "contra-eris-generate=contra_eris.cli:generate_main",
            "contra-eris-evaluate=contra_eris.cli:evaluate_main",
            "contra-eris=contra_eris.cli:main",
        ],
    },
) 