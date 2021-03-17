
from setuptools import setup
import os

HERE = os.path.abspath(os.path.dirname(__file__))

requirements = ['requests', 'python-dateutil']

setup(
    name="concourse-version-checker-resource",
    version='0.1.0',
    description='Concourse CI resource that triggers sync pipeline',
    long_description='',
    url='',
    author='c0ldCalamari',
    license='AGPLv3.0',
    packages=['src'],
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock'
        ]
    },
    tests_require=['pytest', 'pytest-mock'],
    test_suite='tests',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'check = src.check:main',
            'in = src.in_:main',
            'out = src.out:main',
        ]
    }
)
