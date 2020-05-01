import os
from setuptools import setup

try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements

from ixian.version import VERSION


DIR = os.path.dirname(os.path.realpath(__file__))

requirements_path = f"{DIR}/requirements.txt"
requirements = [
    str(ir.req) for ir in parse_requirements(requirements_path, session=PipSession())
]


setup(
    name="ixian",
    VERSION="0.0.1",
    description="Task tool with make-like features.",
    author="Peter Krenesky",
    author_email="kreneskyp@gmail.com",
    maintainer="Peter Krenesky",
    maintainer_email="kreneskyp@gmail.com",
    keywords="tasks, shovel, rake, make, ixian, ix",
    long_description=open("%s/README.md" % DIR, "r").read(),
    #long_description="Task tool with make-like features.",
    long_description_content_type="text/markdown",
    url="https://github.com/kreneskyp/ixian",
    packages=["ixian"],
    package_dir={"ixian": "ixian"},
    include_package_data=True,
    entry_points={"console_scripts": ["s2 = power_shovel.runner:cli"]},
    install_requires=requirements,
    setup_requires=["pbr"],
    pbr=True,
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)
