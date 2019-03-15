""" Setup.py for packaging log-anomaly-detector as library """
from setuptools import setup

REQUIRED_PKG = ["elasticsearch5", "gensim", "matplotlib", "numpy",
                "pandas", "prometheus_client", "boto3", "Flask", "fastparquet",
                "scikit-learn", "scipy", "tqdm", "s3fs",
                "sompy", "pybloom"]

setup(
    name='lad-anomaly-detector',
    version='0.0.1',
    packages=['fact_store',
              'anomaly_detector',
              'anomaly_detector.model',
              'anomaly_detector.types',
              'anomaly_detector.events',
              'anomaly_detector.storage'],
    zip_safe=False,
    classifiers=(
        'Dev Status :: 1 - Alpha',
        'Intended Audience :: DevOps',
        'Natural Language :: English',
        'Language :: Python :: 3.6'
    ),
    python_requires=">3.5",
    url='https://github.com/AICoE/log-anomaly-detector',
    license='',
    author='AiOps',
    author_email='zak.hassan@redhat.com',
    description='Log anomaly detector for streaming logs',
    dependency_links=[
        'git+https://github.com/sevamoo/SOMPY.git' +
        '@76b60ebd6ffd550b0f7faaf632451dfd68827bf7',
        'git+https://github.com/jaybaird/python-bloomfilter.git' +
        '@2bbe01ad49965bf759e31781e6820408068862ac'
    ],
    install_requires=REQUIRED_PKG
)
