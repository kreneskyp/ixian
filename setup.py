import os

from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from setuptools import setup

from power_shovel import VERSION


DIR = os.path.dirname(os.path.realpath(__file__))

requirements_path = f"{DIR}/requirements.txt"
requirements = [
    str(ir.req) for ir in parse_requirements(requirements_path, session=PipSession())
]


setup(
    name="power_shovel",
    version=VERSION,
    author="Peter Krenesky",
    author_email="kreneskyp@gmail.com",
    maintainer="Peter Krenesky",
    maintainer_email="kreneskyp@gmail.com",
    description="Task tool with make-like features.",
    keywords="tasks, shovel, power_shovel, rake, make",
    long_description=open("%s/README.md" % DIR, "r").read(),
    url="https://github.com",
    packages=["power_shovel"],
    package_dir={"power_shovel": "power_shovel"},
    include_package_data=True,
    entry_points={"console_scripts": ["s2 = power_shovel:cli"]},
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)
