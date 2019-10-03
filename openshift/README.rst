OpenShift Templates
--------------------

The following files can be used to deploy different components of log-anomaly-detector. Below I describe what each template is used for:

* aiops_factstore.deployment.yaml - Human in the loop feedback system and metadata store for LAD ML Service.
* aiops_lad_core.buildconfig.yaml - Openshift build configuration for building s2i image from git to Kubernetes container image.
* aiops_lad_core.elasticsearch.storage.yaml - Elasticsearch component for usage along with LAD to process logs that come in.
* aiops_lad_core.ml.job.yaml	 - Kubernetes job template to run LAD CORE machine learning service.
* aiops_lad_core.k8s.service.yaml - Kubernetes service to connect log anomaly detector pod to service.
* aiops_lad_core.minimal.deployment.yaml - Minimal installation for demo purposes.
* aiops_lad_core.env_var_config.deployment.yaml - Full installation of machine learning LAD Core but uses environment variables to setup configurations.
* aiops_lad_core.configmap.deployment.yaml - Full installation of machine learning LAD Core and has parameters to set for mounting custom configmap.
* sample.config.yaml - Provides an example of creating a custom configmap which you can use later to mount into LAD Job.
