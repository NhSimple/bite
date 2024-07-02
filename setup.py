from setuptools import setup, find_packages

setup(
    name="bite",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "blessed",
        "simple-term-menu",
    ],
    entry_points={
        "console_scripts": [
            "bite=main:main",
        ],
    },
    author="NhSimple",
    author_email="",  # You can leave this blank or add an email if you wish
    description="A CLI tool for viewing SQLite databases",
    long_description="A command-line interface tool for viewing and interacting with SQLite databases.",
    url="https://github.com/NhSimple/bite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
