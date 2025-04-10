from setuptools import setup, find_packages

setup(
    name="exo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "autogen",
        "grpcio",
        "protobuf",
        "websockets",
        "pyautogui",
        "neo4j",
        "chromadb",
        "redis",
        "pytest",
    ],
)
