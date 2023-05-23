#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

from pathlib import Path
from setuptools import setup

name = 'pinstall'
module = name.replace('-', '_')
here = Path(__file__).resolve().parent

setup(
    name=name,
    version='1.3',
    description='Installer Tool for Python Programs',
    long_description=here.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    url=f'https://github.com/bulletmark/{name}',
    author='Mark Blakeney',
    author_email='mark.blakeney@bullet-systems.net',
    keywords='venv virtualenv systemd service',
    license='GPLv3',
    packages=[module] + [str(d) for d in Path(module).iterdir() if d.is_dir()
                         and d.name[0] not in '._'],
    python_requires='>=3.6',
    install_requires=['looseversion'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        (f'share/{name}', ['README.md']),
    ],
    entry_points={
        'console_scripts': [f'{name}={module}:{module}.main'],
    }
)
