import os
from setuptools import find_packages, setup

from pip.download import PipSession
from pip.req import parse_requirements

from power_shovel import VERSION


DIR = os.path.dirname(os.path.realpath(__file__))

requirements_path = '%s/requirements.txt' % DIR
requirements = [
    str(ir.req)
    for ir in parse_requirements(requirements_path, session=PipSession())]

setup(
    name='power_shovel',
    version=VERSION,
    author='Peter Krenesky',
    author_email='kreneskyp@gmail.com',
    maintainer='Peter Krenesky',
    maintainer_email='kreneskyp@gmail.com',
    description='Task tool with make-like features.',
    long_description=open('%s/README.md' % DIR, 'r').read(),
    url='https://github.com',
    packages=find_packages(exclude=["*.tests",
                                    "*.tests.*",
                                    "tests.*",
                                    "tests"]),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
)
