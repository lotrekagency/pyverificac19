from setuptools import setup


setup(
    name="verificac19",
    version="0.0.0",
    url="https://github.com/lotrekagency/pyverificac19",
    install_requires=["requests==2.26.01", "dcc-utils==0.1.0"],
    description="VerificaC19 SDK for Python",
    long_description=open("README.rst").read(),
    license="MIT",
    author="Lotrèk Digital Agency",
    author_email="dimmitutto@lotrek.it",
    packages=["verificac19"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
