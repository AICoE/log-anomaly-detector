"""Pytest Configurations and Fixtures."""
from tests.e2e.util import OpenShift, template_deployer, delete_template, \
    delete_objects
import pytest
from kubernetes import client as kubeclient
from openshift.dynamic import DynamicClient
import yaml
from openshift.dynamic.exceptions import UnauthorizedError
import logging
from os import path, makedirs


class Spec:
    """Spec config constants."""

    FACTSTORE = "factstore"
    AD_DEMO = "ad_demo"
    ELASTICSEARCH = "elasticsearch"
    MYSQL = "mysql"
    LAD = "lad"


MY_SQL_CONF = {
    "MYSQL_USER": "admin",
    "MYSQL_PASSWORD": "admin",
    "MYSQL_ROOT_PASSWORD": "admin",
    "MYSQL_DATABASE": "factstore"
}

DB_URI = "mysql+pymysql://{}:{}@{}/{}".format(
    MY_SQL_CONF['MYSQL_USER'],
    MY_SQL_CONF['MYSQL_PASSWORD'],
    "mysql:3306",
    MY_SQL_CONF['MYSQL_DATABASE']
)


logger = logging.getLogger('chardet.charsetprober')
logger.setLevel(logging.INFO)


def pytest_addoption(parser):
    """Update pytest options."""
    parser.addoption("--pytest_config",
                     action="store",
                     default="config.yaml",
                     help="pytest yaml config name")


def pytest_configure(config):
    """Configure pytest."""
    value = config.getini("log_file")
    pytest_yml_config = config.getoption("--pytest_config")

    directory = path.dirname(value)
    if not path.exists(directory):
        makedirs(directory)
    with open(pytest_yml_config, 'r') as stream:
        config_def = yaml.safe_load(stream)
    value = config_def['logs']['build_log_file']
    directory = path.dirname(value)
    if not path.exists(directory):
        makedirs(directory)


@pytest.fixture(scope="session")
def config(request) -> dict:
    """Return the pytest yaml config."""
    with open(request.config.getoption("--pytest_config"), 'r') as stream:
        config_def = yaml.safe_load(stream)
    return config_def


@pytest.fixture(scope="session")
def openshift(config: dict):
    """Provide openshift instance."""
    token = config['openshift']['authToken']
    host = config['openshift']['host']
    namespace = config['openshift']['namespace']

    configuration = kubeclient.Configuration()

    token_auth = dict(
        api_key={'authorization': 'Bearer {}'.format(token)},
        host='https://{}'.format(host),
        verify_ssl=False
    )

    for k, v in token_auth.items():
        setattr(configuration, k, v)

    kubeclient.Configuration.set_default(configuration)

    k8s_client = kubeclient.ApiClient(configuration)
    client = None
    try:
        client = DynamicClient(k8s_client)
    except UnauthorizedError:
        logging.error("Token is not authorized. Please supply another token.")
        exit(1)
    except Exception:
        logging.error("Could not connect to openshift cluster, "
                      "please ensure host settings are accurate.")

    ocp_url = "https://{}".format(host)

    openshift = OpenShift(
        namespace=namespace,
        openshift_api_url=ocp_url,
        token=token,
        client=client
    )

    openshift.create_project()

    # The fixture return value
    return openshift


@pytest.fixture(scope="session")
def mysql_persistent(openshift: OpenShift, config: dict) -> list:
    """Provide deployed mysql_persistent objects."""
    mysql_persistent = template_deployer(
        openshift=openshift, spec=Spec.MYSQL, config=config, **MY_SQL_CONF
    )
    yield mysql_persistent
    if config['openshift']['clean'].lower() == "true":
        delete_objects(openshift, config, Spec.MYSQL, **MY_SQL_CONF)
        delete_template(openshift, config, Spec.MYSQL)


@pytest.fixture(scope="session")
def factstore(openshift: OpenShift, config: dict):
    """Provide deployed factstore objects."""
    factstore = template_deployer(
        openshift=openshift,
        spec=Spec.FACTSTORE,
        config=config,
        CUSTOMER_ID="c1",
        SQL_CONNECT=DB_URI
    )
    yield factstore
    if config['openshift']['clean'].lower() == "true":
        delete_objects(openshift, config, Spec.FACTSTORE,
                       CUSTOMER_ID="c1", SQL_CONNECT=DB_URI)
        delete_template(openshift, config, Spec.FACTSTORE)


@pytest.fixture(scope="session")
def elasticsearch(openshift: OpenShift, config: dict) -> list:
    """Provide deployed elasticsearch objects."""
    elasticsearch = template_deployer(
        openshift=openshift,
        spec=Spec.ELASTICSEARCH,
        config=config
    )
    yield elasticsearch
    if config['openshift']['clean'].lower() == "true":
        delete_objects(openshift, config, Spec.ELASTICSEARCH)
        delete_template(openshift, config, Spec.ELASTICSEARCH)


@pytest.fixture(scope="session")
def ad_demo(openshift: OpenShift, config: dict) -> list:
    """Provide deployed ad_demo objects."""
    ad_demo = template_deployer(
        openshift=openshift,
        spec=Spec.AD_DEMO,
        config=config
    )
    yield ad_demo
    if config['openshift']['clean'].lower() == "true":
        delete_objects(openshift, config, Spec.AD_DEMO)
        delete_template(openshift, config, Spec.AD_DEMO)


@pytest.fixture(scope="session")
def lad(openshift: OpenShift, config: dict, factstore: list) -> list:
    """Provide deployed lad objects."""
    es_endpoint = "lad-elasticsearch-service.{}.svc:9200".format(
        openshift.namespace
    )

    if not factstore:
        host = "no-host"
    else:
        resources = openshift.extract_resource_from_response(
            resp=factstore,
            kind="Route",
        )
        template_route = resources.pop()
        route_name = template_route['metadata']['name']
        try:
            oc_fs_route = openshift.get_route_by_name(route_name)
            host = oc_fs_route['spec']['host']
        except Exception as e:
            logging.warning("Could not retrieve factstore route.")
            host = "no-host"
    factstore_url = "http://{}".format(host)

    lad = template_deployer(openshift=openshift,
                            spec=Spec.LAD,
                            config=config,
                            FACT_STORE_URL=factstore_url,
                            ES_ENDPOINT=es_endpoint)

    yield lad
    if config['openshift']['clean'].lower() == "true":
        delete_objects(openshift, config, Spec.LAD,
                       FACT_STORE_URL=factstore_url,
                       ES_ENDPOINT=es_endpoint)
        delete_template(openshift, config, Spec.LAD)
