""" Setup.py for packaging log-anomaly-detector as library """
from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

REQUIRED_PKG = [
    "Click",
    "elasticsearch5",
    "gensim",
    "matplotlib",
    "numpy",
    "pandas",
    "prometheus_client",
    "Flask==1.0.4",
    "scikit-learn",
    "scipy",
    "tqdm",
    "SQLAlchemy",
    "PyMySQL",
    "sompy",
    "pyyaml",
    "boto3",
    "pyyaml",
    "numba",
    "kafka-python",
    "jaeger-client",
    "opentracing_instrumentation",
    "prometheus_flask_exporter"
]

setup(
    name="log-anomaly-detector",
    version="0.0.1b5",
    py_modules=['app'],
    packages=find_packages(),
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
        "pytest-sugar",
        "pytest-xdist"],
    zip_safe=False,
    classifiers=(
        "Development Status :: 1 - Planning",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ),
    python_requires=">3.5",
    url="https://github.com/AICoE/log-anomaly-detector",
    author="Zak Hassan",
    author_email="zak.hassan@redhat.com",
    description="Log anomaly detector for streaming logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    dependency_links=[
	"git+https://github.com/sevamoo/SOMPY.git@76b60ebd6ffd550b0f7faaf632451dfd68827bf7#egg=sompy",
    ],
    install_requires=REQUIRED_PKG,
    entry_points="""
        [console_scripts]
        log-anomaly-detector=app:cli
    """,
)
