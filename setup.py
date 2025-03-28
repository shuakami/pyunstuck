from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyunstuck",
    version="0.1.0",
    author="shuakami",
    author_email="shuakami@sdjz.wiki",
    description="A lifesaver for frozen Python scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shuakami/pyunstuck",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "pyunstuck=pyunstuck.cli:main",
        ],
    },
) 