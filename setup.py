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

from power_shovel.version import VERSION


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
