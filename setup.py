from setuptools import setup, find_packages


setup(
    name="verificac19",
    version="0.0.0",
    url="https://github.com/lotrekagency/pyverificac19",
    install_requires=[
        "requests==2.26.01",
    ],
    description="VerificaC19 SDK for Python",
    long_description=open("README.rst").read(),
    license="MIT",
    author="Lotrèk Digital Agency",
    author_email="dimmitutto@lotrek.it",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
