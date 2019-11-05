Installation
============

There are various ways you can begin using LAD depending on your environment.

Pip installation
-----------------

The LAD project can be found on `Pypy <https://pypi.org/project/log-anomaly-detector/>`_ and can be installed using :code:`pip` as follows:

.. code-block:: shell

   pip install git+https://github.com/AICoE/log-anomaly-detector.git

.. note::

   LAD requires python 3.6

Build LAD
---------

You may also clone the github repository and build lad yourself. See the
:ref:`development-guide` on further instructions on how you may do this.

Openshift Installation
=======================

There are two ways you may install LAD on openshift. The first way is done
using Ansible and the second using the provided Makefile. For both methods
you will need to clone the repo:

.. code-block:: shell

    $ git clone https://github.com/AICOE/log-anomaly-detector.git
    $ cd log-anomaly-detector/

Ansible OCP Install
-------------------
Not surprisingly you will need Ansible and an OCP cluster with access to a
namespace with deployment privileges. Navigate to the playbooks directory:


.. code-block:: shell

    $ cd playbooks/
    $ ls
    playbook.yaml  README.md  roles  vars

We include one playbook that will provision an entire stack of tools alongside
LAD. The stack includes a MySQL database, Prometheus, Grafana (with pre built
dashboards for LAD), Factstore and LAD itself. See the :code:`roles/` folder
for more info.

Using the playbook is relatively straight forward, you first define your
configuration within :code:`vars/` directory and then run the following
command from the :code:`playbooks/` directory`.

Feel free to adjust the variables as you see fit. If you are just looking to
try out LAD on openshift, you may also use the standard variables provided within
:code:`playbooks/vars/demo/dev-vars.yaml`. You will however, need to update
the namespace variable to match your OCP namespace (which needs to be already
created):

.. code-block:: yaml

    common:
        # The namespace you want to install LAD
        namespace: "lad"
        kubeconfig: $HOME/.kube/config
        state: present
        customer_id: "demo"

Once that is done, simply invoke the following command to deploy the entire stack:

.. code-block:: shell

    $ ansible-playbook playbook.yaml -e target_env=dev -e customer=demo

Here :code:`dev/demo` refers to custom profile setting for a dev environment located
in :code:`playbooks/vars/demo/dev-vars.yaml`. Similarly, by supplying :code:`dev`
we also use the common vars found within the :code:`playbooks/vars/common/dev-vars.yaml`
directory.

By default LAD is scaled down to zero pods. You will have to first configure
a proper data source and sink before running a LAD deployment. For example,
if we peek inside :code:`playbooks/vars/demo/dev-vars.yaml` and look at the
config map settings, we see:

.. code-block:: yaml

    lad:
        ...
        es_secrets_name: "log-anomaly-detector-certs"
        app_config: |
            STORAGE_DATASOURCE:           "es"
            STORAGE_DATASINK:             "stdout"
            ES_ENDPOINT:                  <elastic search URL>
            ES_QUERY:                     'ecommerce'
            ES_USE_SSL:                   False
            ES_INPUT_INDEX:               "lad-"
            ES_VERSION:                   7
            FACT_STORE_URL:               { { factstore_route } }
            INFER_ANOMALY_THRESHOLD:      1.3
            INFER_TIME_SPAN:              900
            INFER_LOOPS:                  1
            INFER_MAX_ENTRIES:            3000
            TRAIN_TIME_SPAN:              900
            TRAIN_MAX_ENTRIES:            3000
            PARALLELISM:                  6
            SOMPY_TRAIN_ROUGH_LEN:        100
            SOMPY_TRAIN_FINETUNE_LEN:     5
            SOMPY_INIT:                   "random"


Note that ES_ENDPOINT needs to be provided if that is your source. If your
Elasticsearch requires cert files, you will have to manually add them to your
namespace and provide their name using the :code:`es_secrets_name` var otherwise
you may simply exclude this variable. Once done, run the following command again:

.. code-block:: shell

    $ ansible-playbook playbook.yaml -e target_env=dev -e customer=demo

Then scale up LAD to a single pod and watch the logs to see it in action.

.. Note::

    An Elasticsearch ansible role is included but not enabled by default in the playbook, the
    general assumption is that you already have an Elasticsearch instance should
    you wish to injest data from it with LAD. If you would like the playbook
    to provision elasticsearch as well, simply change the :code:`es.deploy` var to :code:`true` in
    :code:`playbooks/vavs/common/dev-vars.yaml`:

    .. code-block:: yaml

        # dev-vars.yaml
        es:
            deploy: true
            ...

Makefile Installation
---------------------

To deploy LAD and all accomodating tools (Prometheus, MySQL, Grafana, Elastic Search, Elastalert, Factstore)
run the following commands from the root of the project:

.. code-block:: shell

    $ git clone https://github.com/AICOE/log-anomaly-detector.git
    $ cd log-anomaly-detector
    $ make NAMESPACE=<your_namespace> oc_deploy_demo_prereqs

In the Makefile update the FACTSTORE_ROUTE (based on your newly deployed
Factstore route) and SMTP_SERVER_URL (in order to use Elastalert, you will need
a ready SMTP server).

.. code-block:: shell

    $ cat Makefile
    ...
    # route for the Factstore deployed
    FACTSTORE_ROUTE="http://LAD.FACTSTORE.URL.ENTER.HERE.com/"

    # mailing server used by elastalerts to send anomaly alerts
    SMTP_SERVER_URL="my.mailing.server.url"
    ...

Now run the following command to deploy LAD, Prometheus, and Grafana:

.. code-block:: shell

    $ make NAMESPACE=<your_namespace> oc_deploy_lad
    $ make NAMESPACE=<your_namespace> oc_deploy_demo_monitoring

LAD will launch alongside a demo ecommerce app. If you place order on this demo
app, you will see LAD try to detect anomolies based on the order logs produced.
Update the configmaps for LAD to use your own data sources instead.


For more information on how to configure LAD to better suit your needs, see :ref:`Configurations <config-info>`.