import os
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_requirements():
    packages = []

    with open("./requirements.txt") as fd:
        for line in fd.readlines():
            if not line or line.startswith('-i'):
                continue
            packages.append(line.split(';', 1)[0])

    return packages

def get_test_requires():
  if os.path.exists('requirements-test.txt'):
    with open('requirements-test.txt', 'r') as requirements_file:
        res = requirements_file.readlines()
        return [req.split(' ', maxsplit=1)[0] for req in res if req]
  else:
    return []


class Test(TestCommand):
    user_options = [
        ('pytest-args=', 'a', "Arguments to pass into py.test")
    ]

    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = ['--timeout=2', '--cov=./thoth', '--capture=no', '--verbose']

    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.pytest_args))


setup(
    name='log-anomaly-detector',
    version="0.0.1",
    description='A service which processes log entries and marks anomalies',
    long_description='A service which processes log entries and marks anomalies',
    author='',
    author_email='',
    license='GPLv3+',
    packages=[
        'anomaly_detector'
    ],
    zip_safe=False,
    install_requires=get_requirements(),
    tests_require=get_test_requires(),
    cmdclass={'test': Test},
)