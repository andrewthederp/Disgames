from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
desc = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="disgames",
    version="1.0.1",
    description="A games module that can be used to instantly add games to your discord bot",
    long_description=desc,
    author="andrew",
    maintainer="Marcus",
    url="https://github.com/andrewthederp/Disgames",
    license="Apache",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires="discord.py",
    python_requires=">=3.6",
    packages=find_packages(include=["disgames", "disgames.*"]),
)
