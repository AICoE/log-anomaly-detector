"""Openshift Tests."""
import requests
from tests.e2e.conftest import Spec
from tests.e2e.util import OpenShift, wait_for_condition, deployment_running, \
    build_finished_successfully, container_running, check_skip_test


def test_mysql_deployment(openshift: OpenShift, mysql_persistent: list,
                          config: dict):
    """Test MySQL Deployment."""
    check_skip_test(
        config=config,
        spec=Spec.MYSQL,
        test_name=test_mysql_deployment.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(mysql_persistent) > 0

    timeout = config['spec'][Spec.MYSQL]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=mysql_persistent,
        kind="DeploymentConfig",
    )
    deploy_cfg = resources.pop()
    is_running = deployment_running(openshift, deploy_cfg, timeout)
    assert is_running


def test_fact_store_build(openshift: OpenShift, factstore: list, config: dict):
    """Test factstore build."""
    check_skip_test(
        config=config,
        spec=Spec.FACTSTORE,
        test_name=test_fact_store_build.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(factstore) > 0

    timeout_amount = config['spec'][Spec.FACTSTORE]['timeout']
    build_log_file = config['logs']["build_log_file"]

    resources = openshift.extract_resource_from_response(
        resp=factstore,
        kind="BuildConfig",
    )
    build_cfg = resources.pop()

    build_sucessfully_completed = build_finished_successfully(
        openshift, build_cfg, timeout_amount, build_log_file
    )

    assert build_sucessfully_completed


def test_fact_store_deployment(openshift: OpenShift,
                               factstore: list,
                               config: dict):
    """Test factstore deployment."""
    check_skip_test(
        config=config,
        spec=Spec.FACTSTORE,
        test_name=test_fact_store_deployment.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(factstore) > 0

    timeout_amount = config['spec'][Spec.FACTSTORE]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=factstore,
        kind="DeploymentConfig",
    )
    deploy_cfg = resources.pop()
    is_running = deployment_running(openshift, deploy_cfg, timeout_amount)
    assert is_running


def test_fact_store_route_health(openshift: OpenShift, factstore: list,
                                 config: dict):
    """Test Facstore route."""
    check_skip_test(
        config=config,
        spec=Spec.FACTSTORE,
        test_name=test_fact_store_route_health.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(factstore) > 0

    timeout = config['spec'][Spec.FACTSTORE]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=factstore,
        kind="Route",
    )
    template_route = resources.pop()
    route_name = template_route['metadata']['name']

    route_is_healthy = wait_for_condition(
        success_cond=lambda: openshift.get_route_status_code(route_name) == 200,
        min_to_wait=timeout
    )

    assert route_is_healthy

    db_route_connection_is_healthy = wait_for_condition(
        success_cond=lambda: openshift.get_route_status_code(
            route_name,
            path_suffix='/api/false_positive'
        ) == 200,
        min_to_wait=timeout
    )

    assert db_route_connection_is_healthy


def test_es_deployment(openshift: OpenShift, elasticsearch: list,
                       config: dict):
    """Test Elastic Search Deployment."""
    check_skip_test(
        config=config,
        spec=Spec.ELASTICSEARCH,
        test_name=test_es_deployment.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(elasticsearch) > 0
    timeout = config['spec'][Spec.ELASTICSEARCH]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=elasticsearch,
        kind="DeploymentConfig",
    )
    deploy_cfg = resources.pop()
    is_running = deployment_running(openshift, deploy_cfg, timeout)
    assert is_running


def test_ad_demo_build(openshift: OpenShift, ad_demo: list, config: dict):
    """Test Anomaly Detection Demo Build."""
    check_skip_test(
        config=config,
        spec=Spec.AD_DEMO,
        test_name=test_ad_demo_build.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(ad_demo) > 0

    timeout = config['spec'][Spec.AD_DEMO]['timeout']
    build_log_file = config['logs']["build_log_file"]
    resources = openshift.extract_resource_from_response(
        resp=ad_demo,
        kind="BuildConfig",
    )
    build_cfg = resources.pop()

    build_sucessfully_completed = build_finished_successfully(
        openshift, build_cfg, timeout, build_log_file
    )

    assert build_sucessfully_completed


def test_ad_demo_deployment(openshift: OpenShift, ad_demo: list, config: dict):
    """Test Anomaly Detection Demo Deployment."""
    check_skip_test(
        config=config,
        spec=Spec.AD_DEMO,
        test_name=test_ad_demo_deployment.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(ad_demo) > 0
    timeout = config['spec'][Spec.AD_DEMO]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=ad_demo,
        kind="DeploymentConfig",
    )
    deploy_cfg = resources.pop()
    is_running = deployment_running(openshift, deploy_cfg, timeout)
    assert is_running


def test_ad_demo_container_started(openshift: OpenShift,
                                   ad_demo: list, config: dict):
    """Test Anomaly Detection Demo container status."""
    check_skip_test(
        config=config,
        spec=Spec.AD_DEMO,
        test_name=test_ad_demo_container_started.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(ad_demo) > 0
    timeout = config['spec'][Spec.AD_DEMO]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=ad_demo,
        kind="DeploymentConfig",
    )

    deploy_cfg = resources.pop()
    is_running = container_running(
        openshift=openshift,
        deploy_cfg=deploy_cfg,
        timeout_amount=timeout,
        container_id=0,
        pod_log_file_prefix=config['logs']['pod_log_file']
    )
    assert is_running


def test_ad_demo_route_health(openshift: OpenShift,
                              ad_demo: list, config: dict):
    """Test Anomaly Detection Demo Route Health."""
    check_skip_test(
        config=config,
        spec=Spec.AD_DEMO,
        test_name=test_ad_demo_route_health.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(ad_demo) > 0
    timeout = config['spec'][Spec.AD_DEMO]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=ad_demo,
        kind="Route",
    )

    resources = list(filter(
        lambda route: not route['metadata']['name'].endswith('metrics'),
        resources
    ))
    template_route = resources.pop()
    route_name = template_route['metadata']['name']

    is_healthy = wait_for_condition(
        success_cond=lambda: openshift.get_route_status_code(route_name) == 200,
        min_to_wait=timeout
    )
    assert is_healthy


def test_ad_demo_order_placement(openshift: OpenShift,
                                 ad_demo: list, config: dict):
    """Test Anomaly Detection Demo Order Placement."""
    check_skip_test(
        config=config,
        spec=Spec.AD_DEMO,
        test_name=test_ad_demo_order_placement.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(ad_demo) > 0
    resources = openshift.extract_resource_from_response(
        resp=ad_demo,
        kind="Route",
    )
    resources = list(filter(
        lambda route: not route['metadata']['name'].endswith('metrics'),
        resources
    ))
    template_route = resources.pop()
    route_name = template_route['metadata']['name']
    route = openshift.get_route_by_name(route_name)
    route_url = "http://{}/mock/orderService".format(route['spec']['host'])
    form_data = {
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[id]": "1",
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[image]": "bananas.jpg",
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[pname]": "bananas",
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[pprice]": "5",
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[pquant]": "1",
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[ptype]": "fruit",
        "79161a98-30e0-11e7-b4e8-9801a798fc8f[newQuant]": "1",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[id]": "2",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[image]": "onions.jpg",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[pname]": "onions",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[pprice]": "3",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[pquant]": "1",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[ptype]": "vegetables",
        "7915f0cc-30e0-11e7-91c7-9801a798fc8f[newQuant]": "1"
    }
    with requests.Session() as s:
        s.headers = {"User-Agent": "Mozilla/5.0"}
        res = s.post(route_url, data=form_data)
    assert res.status_code == 200


def test_lad_deployment(openshift: OpenShift, lad: list, config: dict):
    """Test Lad Deployment."""
    check_skip_test(
        config=config,
        spec=Spec.LAD,
        test_name=test_lad_deployment.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(lad) > 0
    timeout = config['spec'][Spec.LAD]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=lad,
        kind="DeploymentConfig",
    )
    deploy_cfg = resources.pop()
    is_running = deployment_running(openshift, deploy_cfg, timeout)
    assert is_running


def test_lad_container_started(openshift: OpenShift, lad: list, config: dict):
    """Test Lad container status."""
    check_skip_test(
        config=config,
        spec=Spec.LAD,
        test_name=test_lad_container_started.__name__
    )
    # Ensure we successfully deployed (if indicated) or retrieved template.
    assert len(lad) > 0
    timeout = config['spec'][Spec.LAD]['timeout']
    resources = openshift.extract_resource_from_response(
        resp=lad,
        kind="DeploymentConfig",
    )

    deploy_cfg = resources.pop()
    is_running = container_running(
        openshift=openshift,
        deploy_cfg=deploy_cfg,
        timeout_amount=timeout,
        container_id=0,
        pod_log_file_prefix=config['logs']['pod_log_file']
    )
    assert is_running
