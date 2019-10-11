"""Openshift Testing Utility."""
import time
from typing import Callable, Optional
import pytest
import requests
from openshift.dynamic import exceptions, DynamicClient, ResourceInstance, \
    ResourceField
import yaml
import logging
from urllib import request as url_request
from openshift.dynamic.exceptions import NotFoundError, ConflictError


class OpenShift:
    """Interaction with OpenShift within a project."""

    def __init__(self,
                 *,
                 namespace: str = None,
                 kubernetes_verify_tls: bool = False,
                 openshift_api_url: str = None,
                 token: str = None,
                 client: DynamicClient = None
                 ):
        """Initialize Openshift with an associated work namespace."""
        self.namespace = namespace
        self.kubernetes_verify_tls = kubernetes_verify_tls
        self.openshift_api_url = openshift_api_url
        self.token = token
        self.client = client
        self.projects_resource = None

    def _get_template(self, name: str) -> dict:
        """Get template from namespace."""
        response = self.client.resources.get(
            api_version="template.openshift.io/v1",
            kind="Template",
            singular_name='template'
        ).get(
            namespace=self.namespace,
            name=name
        )
        logging.debug(
            "OpenShift response for getting template by label_selector %r: %r",
            name,
            response.to_dict(),
        )
        return response.to_dict()

    def _get_resource(self, resource: dict) -> dict:
        """Get resource from namespace."""
        name = resource['metadata']['name']
        api_version = resource['apiVersion']
        kind = resource['kind']

        v1_resource = self.client.resources.get(api_version=api_version,
                                                kind=kind)
        return v1_resource.get(name=name, namespace=self.namespace)

    def _get_kind_res_instance(self, kind) -> ResourceInstance:
        """Get all ResourceInstance of this kind from this namespace."""
        return self.client.resources.get(
            api_version='v1',
            kind=kind
        ).get(namespace=self.namespace)

    def get_builds_by_buildconfig(self, build_config: dict) -> list:
        """Retrieve builds that were configured by build_config."""
        builds = self._get_kind_res_instance("Build").items
        bfg_name = build_config['metadata']['name']

        filtered_builds = []
        for build in builds:
            annotations = build['metadata']['annotations']
            if annotations['openshift.io/build-config.name'] == bfg_name:
                filtered_builds.append(build)
        return filtered_builds

    def get_pods(self) -> list:
        """Get pod resources from this namespace."""
        return self._get_kind_res_instance('Pod').items

    def get_pods_by_deployment_cfg(self, config: dict):
        """Return pods configured by config, ignore deployer pods."""
        pods = self.get_pods()
        filtered_pods = []
        cfg_name = config['metadata']['name']

        for pod in pods:
            annotations = pod['metadata']['annotations']
            annotation_keys = annotations.keys()
            annotation_cfg = "openshift.io/deployment-config.name"
            # Ignore deployer pods:
            is_deployer_pod = pod['metadata']['name'].endswith("deploy")
            if annotation_cfg in annotation_keys \
                    and annotations[annotation_cfg] == cfg_name\
                    and not is_deployer_pod:
                filtered_pods.append(pod)
        return filtered_pods

    def get_route_by_name(self, name: str):
        """Get a route by <name>."""
        routes = self._get_kind_res_instance("Route")['items']
        routes = list(filter(
            lambda route: route['metadata']['name'] == name,
            routes
        ))

        return routes.pop()

    def get_route_status_code(self, route_name: str, path_suffix: str = ''):
        """Get a route status code for route <name>."""
        oc_fs_route = self.get_route_by_name(route_name)
        host = oc_fs_route['spec']['host']
        if path_suffix:
            r = requests.head("http://{}{}".format(host, path_suffix))
        else:
            r = requests.head("http://{}".format(host))
        return r.status_code

    def is_build_complete(self, build_cfg: dict) -> bool:
        """
        Check if Build is complete.

        Finds build configured by build_cfg and returns True if
        all builds are complete.

        Precondition: Assumes there is only one build configured by build_cfg.
        If there are multiple builds associated with build_cfg, return first
        one found.
        """
        # TODO: Consider changing to verifying all existing builds and checking
        # if one is complete
        all_success = []
        builds = self.get_builds_by_buildconfig(build_cfg)
        for build in builds:
            name = build['metadata']['name']
            phase = build['status']['phase']
            logging.debug("Checking build {} for completion, has phase:{}".format(
                name, phase))
            if phase == 'Complete':
                all_success.append(True)
            else:
                all_success.append(False)
        return all_success != [] and all(all_success)

    def is_build_failed(self, build_cfg: dict) -> bool:
        """
        Check if build failed.

        Finds build configured by build_cfg and returns True if
        build failed.

        Precondition: Assumes there is only one build configured by build_cfg.
        If there are multiple builds associated with build_cfg, return first
        one found.
        """
        builds = self.get_builds_by_buildconfig(build_cfg)
        any_fails = []
        for build in builds:
            name = build['metadata']['name']
            phase = build['status']['phase']
            logging.debug("Checking build {} for errors, has phase:{}".format(
                name, phase))
            failed = phase == 'Failed'
            error = phase == 'Error'
            cancelled = phase == 'Cancelled'
            if failed or error or cancelled:
                any_fails.append(True)
        return any_fails != []

    def get_build_log(self, build_id: str) -> str:
        """Get log of a build in the given namespace."""
        endpoint = "{}/apis/build.openshift.io/v1/namespaces/{}/builds/{}/log"\
            .format(self.openshift_api_url, self.namespace, build_id)

        response = requests.get(
            endpoint,
            headers={
                "Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json",
            },
            verify=self.kubernetes_verify_tls,
        )

        if response.status_code == 404:
            raise Exception(
                f"Build with id {build_id} was not found in "
                f"namespace {self.namespace}"
            )

        logging.debug(
            "OpenShift response for build log (%d): %r",
            response.status_code,
            response.text,
        )
        response.raise_for_status()

        return response.text

    def get_pod_log(self, pod_id: str) -> Optional[str]:
        """Get log of a pod based on assigned pod ID."""
        endpoint = "{}/api/v1/namespaces/{}/pods/{}/log".format(
            self.openshift_api_url, self.namespace, pod_id
        )
        response = requests.get(
            endpoint,
            headers={
                "Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json",
            },
            verify=self.kubernetes_verify_tls,
        )
        logging.debug(
            "Kubernetes master response for pod log (%d): %r",
            response.status_code,
            response.text,
        )

        if response.status_code == 404:
            raise Exception(
                f"Pod with id {pod_id} was not found in "
                f"namespace {self.namespace}"
            )

        if response.status_code == 400:
            # If Pod has not been initialized yet, there is returned 400
            # status code. Return None in this case.
            return None

        response.raise_for_status()
        return response.text

    @staticmethod
    def pods_running(pods: list):
        """Return true if all pods are in running phase."""
        all_running = []
        for pod in pods:
            if pod['status']['phase'] == 'Running':
                logging.debug("Found pod {} to be in running phase.".format(
                    pod['metadata']['name']
                ))
                all_running.append(True)
            else:
                all_running.append(False)
        return all_running != [] and all(all_running)

    @staticmethod
    def pods_failed(pods: list):
        """Check if any pod in <pods> has faild."""
        all_running = []
        for pod in pods:
            phase = pod['status']['phase']
            if phase == 'Failed' or phase == 'Unknown':
                logging.debug("Found pod {} to be in {} phase.".format(
                    pod['metadata']['name'], phase))
                all_running.append(True)
        return all_running != []

    def containers_are_running(self, container_id: int, pods: list):
        """Check if containers with <container_id> in <pods> are running."""
        containers_running = []
        for pod in pods:
            if self.container_is_running(
                    container_id=container_id,
                    pod=pod):
                containers_running.append(True)
            else:
                containers_running.append(False)
        return containers_running != [] and all(containers_running)

    def containers_are_failing(self, container_id: int, pods: list):
        """Return True if any <container_id> in <pods> are in fail state."""
        containers_running = []
        for pod in pods:
            if self.container_stuck_or_terminated(
                    container_id=container_id,
                    pod=pod):
                containers_running.append(True)
        return containers_running != []

    @staticmethod
    def container_is_running(container_id: int, pod: ResourceField) -> bool:
        """
        Check if container is running.

        Check if a particular container indexed at <container_id> is
        running in <pod>.
        """
        container_status = pod['status']['containerStatuses'][container_id]
        if 'running' in container_status['state'].keys():
            logging.info(
                "Container [id: {}] with name {} started at {}.".format(
                    container_status['containerID'],
                    container_status['name'],
                    container_status['state']['running']['startedAt']
                ))
            return True
        else:
            return False

    @staticmethod
    def container_stuck_or_terminated(container_id: int,
                                      pod: ResourceField) -> bool:
        """
        Check if container is stuck or terminated.

        Check if container indexed at <container_id> in <pod> has
        terminated or is stuck, return True if it has.
        """
        container_status = pod['status']['containerStatuses'][container_id]
        if 'waiting' in container_status['state'].keys():
            reason = container_status['state']['waiting']['reason']
            if reason == 'CrashLoopBackOff':
                logging.error("Container [id: {}] with name {} is "
                              "Crashlooping.".format(
                               container_status['containerID'],
                               container_status['name']))
                return True
            return False
        elif 'terminated' in container_status['state'].keys():
            reason = container_status['state']['terminated']['reason']
            logging.error("Container [id: {}] with name {} Terminated."
                          "Reason: {}".format(
                           container_status['containerID'],
                           container_status['name'],
                           reason))
            return True
        else:
            return False

    def create_project(self):
        """
        Create a project in this namespace.

        If the project already exists, do nothing.
        """
        try:
            self.projects_resource = self.client.resources.get(
                api_version='project.openshift.io/v1',
                kind='Project'
            )
        except Exception as e:
            print("\tFailed with exception: {}".format(type(e)))

        project = """
            "kind": "Project"
            "apiVersion": "project.openshift.io/v1"
            "metadata":
                "name": "{}"
            """.format(self.namespace)
        project_yaml = yaml.load(project, Loader=yaml.FullLoader)

        try:
            self.projects_resource.get(name=self.namespace)
            logging.warning("Namespace {} already exists.".format(
                self.namespace
            ))
        except exceptions.NotFoundError:
            logging.info("Project {} not found, creating...".format(
                self.namespace
            ))
            self.projects_resource.create(body=project_yaml)

    def oc_process(self, template: dict) -> dict:
        """
        Process the given template in OpenShift.

        :returns a processed template
        """
        endpoint = "{}/apis/template.openshift.io" \
                   "/v1/namespaces/{}/processedtemplates".format(
                    self.openshift_api_url,
                    self.namespace
                    )
        response = requests.post(
            endpoint,
            json=template,
            headers={
                "Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json",
            },
            verify=self.kubernetes_verify_tls,
        )

        logging.debug(
            "OpenShift master response template (%d): %r",
            response.status_code,
            response.text,
        )

        try:
            response.raise_for_status()
        except Exception:
            logging.error("Failed to process template: %s", response.text)
            raise

        return response.json()

    def deploy_template(self, template_yaml: dict) -> list:
        """
        Deploy a processed template's objects.

        :param template_yaml: a processed template
        :return: the list of deployed objects
        """
        template = self.oc_process(template_yaml)
        deployed_objects = []
        for template_object in template['objects']:
            response = self.client.resources.get(
                api_version=template_object["apiVersion"],
                kind=template_object["kind"]
            ).create(
                body=template_object,
                namespace=self.namespace
            )

            response = response.to_dict()
            deployed_objects.append(response)
            logging.debug("OpenShift response for creating tempate object: %r",
                          response)
        return deployed_objects

    @staticmethod
    def set_template_parameters(template: dict, **parameters: object) -> dict:
        """
        Set template parameters.

        Set parameters in the template - replace existing ones or append to
        parameter list if not exist.

        :returns    template with parameters set/replaced/appended
        """
        logging.debug(
            "Setting parameters for template %r: %s",
            template["metadata"]["name"],
            parameters,
        )

        if "parameters" not in template:
            template["parameters"] = []

        for parameter_name, parameter_value in parameters.items():
            for entry in template["parameters"]:
                if entry["name"] == parameter_name:
                    entry["value"] = (
                        str(parameter_value)
                        if parameter_value is not None
                        else ""
                    )
                    break
            else:
                logging.warning(
                    "Requested to assign parameter %r (value %r) to template "
                    "but template does not provide the given parameter, "
                    "forcing...",
                    parameter_name,
                    parameter_value,
                )
                template["parameters"].append(
                    {
                        "name": parameter_name,
                        "value": str(parameter_value)
                        if parameter_value is not None
                        else "",
                    }
                )
        return template

    def remove_objects(self, oc_objects: list):
        """Remove Openshift."""
        for obj in oc_objects:
            api_version, kind = obj['apiVersion'], obj['kind']
            name = obj['metadata']['name']
            res = self.client.resources.get(api_version=api_version, kind=kind)
            try:
                logging.info("Attempting to delete object {} "
                             "with name {}".format(kind, name))
                res.delete(name=name, namespace=self.namespace)
                logging.info("Deleted resource {} : {}".format(kind, name))
            except NotFoundError as e:
                logging.warning("Could not find template {} to delete.".format(
                    name
                ))

    def remove_template(self, template: dict):
        """Remove template from ocp namespace."""
        api_version, kind = template['apiVersion'], template['kind']
        name = template['metadata']['name']
        res = self.client.resources.get(api_version=api_version,
                                        kind=kind,
                                        singular_name="template")
        try:
            logging.info("Attempting to delete template {} "
                         "with name {}".format(kind, name))
            res.delete(name=name, namespace=self.namespace)
        except NotFoundError as e:
            logging.warning("Could not find template {} to delete.".format(name))

    @staticmethod
    def extract_resource_from_response(resp: list, kind: str) -> list:
        """
        Take a list of openshift objects and filters on <kind>.

        :returns a list of <kind> objects
        """
        resources = []
        for obj in resp:
            if obj['kind'] == kind:
                resources.append(obj)
        if not resources:
            logging.error("Resource {} does not exist in the list of "
                          "objects given".format(kind))
            raise Exception("Resource does not exist.")
        return resources


def wait_for_condition(success_cond: Callable,
                       min_to_wait: int,
                       fail_cond: Callable = None) -> bool:
    """
    Wait for condition <bool_fn()> for <min_to_wait> minutes.

    :returns True to indicate success, False otherwise (timeout or failure).
    """
    timeout = time.time() + 60 * min_to_wait
    timedout = False
    failed = False
    success = False
    while not success and not timedout and not failed:
        if success_cond():
            success = True
        elif fail_cond is not None and fail_cond():
            failed = True
        elif time.time() > timeout:
            timedout = True
        else:
            time.sleep(1)
    return success


def template_deployer(openshift: OpenShift,
                      spec: str,
                      config: dict,
                      **parameters: object) -> list:
    """
    Deploy template.

    Deploy the template_yaml objects on an openshift namespace, if nodeploy is
    set, then simply return the processed template instead.

    :returns list of processed template objects that are deployed on openshift
    """
    template_yaml = load_yaml(config=config, spec=spec)

    if parameters.items():
        openshift.set_template_parameters(template_yaml, **parameters)
    deploy = config['spec'][spec]['deploy'].lower() == "true"
    action_msg = "Nodeploy enabled, Retrieving" if not deploy \
        else "Deploy enabled, attempting to deploy"
    logging.info("{} template: {}".format(action_msg,
                                          template_yaml['metadata']['name']))
    v1_templates = openshift.client.resources.get(
        api_version=template_yaml['apiVersion'],
        kind=template_yaml['kind'],
        singular_name='template')
    if not deploy:
        return openshift.oc_process(template_yaml)['objects']
    else:
        try:
            v1_templates.create(
                body=template_yaml,
                namespace=openshift.namespace
            )
            resource_objects = openshift.deploy_template(template_yaml)
        except ConflictError as e:
            error_msg = "Encountered error when attempting to create template" \
                        " objects from template {}. Response from ocp: {}"\
                        .format(template_yaml['metadata']['name'],
                                e.body,)
            logging.error(error_msg)
            return []
        return resource_objects


def delete_template(openshift: OpenShift, config: dict, spec: str):
    """Delete template."""
    template_yaml = load_yaml(config=config, spec=spec)
    openshift.remove_template(template_yaml)


def delete_objects(openshift: OpenShift,
                   config: dict,
                   spec: str,
                   **parameters: object):
    """Delete template."""
    template_yaml = load_yaml(config=config, spec=spec)
    if parameters.items():
        openshift.set_template_parameters(template_yaml, **parameters)
    processed_template = openshift.oc_process(template_yaml)
    openshift.remove_objects(processed_template['objects'])


def deployment_running(openshift: OpenShift, deploy_cfg: dict,
                       timeout_amount: int) -> bool:
    """
    Check if deployment is running.

    Test if a Deployment in openshift that was configured by the deploy_cfg
    deployed successfully. Wait timeout_amount minutes for deployment to reach
    Running phase.

    :returns True if deployment configured by deploy_cfg was successful.
    """
    # wait <timeout_amount> minutes for deployment or else time out
    deployments_started = wait_for_condition(
        success_cond=lambda: len(
            openshift.get_pods_by_deployment_cfg(deploy_cfg)
        ) > 0,
        min_to_wait=timeout_amount
    )

    assert deployments_started

    # Wait for pods to reach running state
    deployment_pods_running = wait_for_condition(
        success_cond=lambda: openshift.pods_running(
            pods=openshift.get_pods_by_deployment_cfg(deploy_cfg)
        ),
        fail_cond=lambda: openshift.pods_failed(
            pods=openshift.get_pods_by_deployment_cfg(deploy_cfg)
        ),
        min_to_wait=timeout_amount
    )
    return deployment_pods_running


def container_running(openshift: OpenShift,
                      deploy_cfg: dict,
                      timeout_amount: int,
                      container_id: int,
                      pod_log_file_prefix: str = None) -> bool:
    """
    Check if container is running.

    Test if a container in an openshift pod that was configured by
    the deploy_cfg is running. Wait timeout_amount minutes for deployment to
    reach Running state.

    precondition: pod deployment is assumed to have started

    :returns True if container reaches running state in <timeout_amount> min.
    """
    # Wait for pods to reach running state
    deployment_pod_running = wait_for_condition(
        success_cond=lambda: openshift.containers_are_running(
            container_id=container_id,
            pods=openshift.get_pods_by_deployment_cfg(deploy_cfg)
        ),
        fail_cond=lambda: openshift.containers_are_failing(
            container_id=container_id,
            pods=openshift.get_pods_by_deployment_cfg(deploy_cfg)
        ),
        min_to_wait=timeout_amount
    )
    pods = openshift.get_pods_by_deployment_cfg(deploy_cfg)
    for i, pod in enumerate(pods):
        if pod_log_file_prefix:
            try:
                name = pod['metadata']['name']
                store_logs(filename_prefix=pod_log_file_prefix, name=name,
                           log_fn=lambda x: openshift.get_pod_log(pod_id=x))
            except Exception:
                # Might encounter an error if the build was cancelled
                logging.error("Could not save pod logs to {}, this maybe due "
                              "to the pod being unable to "
                              "start.".format(pod_log_file_prefix))

    return deployment_pod_running


def build_finished_successfully(openshift: OpenShift,
                                build_cfg: dict,
                                timeout_amount: int,
                                build_log_file: str = None):
    """
    Check if build finished successfully (reached completion).

    Test if a Build in openshift that was configured by the <build_cfg>
    finished successfully. Wait <timeout_amount> minutes for build to reach
    Completed phase.

    If <bulid_log_file> is provided, then the build log output is saved
    to this filepath.

    :returns    True if build configured by <build_cfg> completed.
                False if build failed, was cancelled, or error'd out.
    """
    # Ensure that there are builds that were configured by factstore build_cfg
    builds_started = wait_for_condition(
        success_cond=lambda: len(
            openshift.get_builds_by_buildconfig(build_cfg)
        ) > 0,
        min_to_wait=timeout_amount
    )
    assert builds_started

    build_sucessfully_completed = wait_for_condition(
        success_cond=lambda: openshift.is_build_complete(build_cfg),
        min_to_wait=timeout_amount,
        fail_cond=lambda: openshift.is_build_failed(build_cfg)
    )

    if build_log_file:
        builds = openshift.get_builds_by_buildconfig(build_cfg)
        for build in builds:
            try:

                name = build['metadata']['name']
                store_logs(filename_prefix=build_log_file,
                           name=name,
                           log_fn=lambda x: openshift.get_build_log(build_id=x))
            except Exception:
                # Might encounter an error if the build was cancelled
                logging.error("Could not save "
                              "build logs to {}".format(build_log_file))
    return build_sucessfully_completed


def load_yaml(config: dict, spec: str):
    """Load and return a dict as yaml file."""
    path = config['spec'][spec]['template']
    if path.startswith("http"):
        with url_request.urlopen(path) as stream:
            yml = yaml.safe_load(stream)
    else:
        with open(path, 'r') as stream:
            yml = yaml.safe_load(stream)
    return yml


def store_logs(filename_prefix: str, name: str,
               log_fn: Callable, append: bool = False):
    """Store logs with the option to append with prefix and name."""
    logs = log_fn(name)
    filename = "{}-{}".format(filename_prefix, name)
    mode = 'a' if append else 'w+'
    with open(filename, mode) as build_log:
        build_log.write(logs)


def check_skip_test(config: dict, spec: str, test_name: str):
    """Skip tests for a spec if indicated in the pytest yaml config."""
    if config['spec'][spec]['runtests'].lower() == "false":
        pytest.skip("Test: {}.".format(test_name))
