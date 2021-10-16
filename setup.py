import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="NodeNotePackage",
    version="2.0.10",
    author="Ye Tao",
    author_email="helper033@163.com",
    description="Mind map software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MPL",
    url="https://github.com/yetao0806/NodeNote",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"": ["*.*"]},
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "numpy==1.21.2",
        "matplotlib==3.4.3",
        "validators==0.18.2",
        "Pillow==8.3.2",
        "protobuf==3.18.1",
        "PyQt5==5.15.4"
    ]
)
