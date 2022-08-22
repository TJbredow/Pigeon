from pprint import pprint
from contextlib import suppress

import kubernetes
from jinja2 import Environment, PackageLoader, select_autoescape
import yaml


CRD_GROUP = 'tbkb.info'
CRD_VERSION = 'v1'
CRD_PLURAL = 'pigeons'
with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as nsf:
    NAMESPACE = nsf.read()
# kubernetes.config.load_kube_config()
kubernetes.config.load_incluster_config()
def build_pigeon(client, spec: dict):
    env = Environment(
        loader=PackageLoader("pigeonOperator"),
        autoescape=select_autoescape()
    )
    template = env.get_template("pigeon.yaml")
    data = yaml.safe_load_all(template.render(
        pig_name=spec["app-name"],
        git_repo=spec["git-repo"],
        namespace=NAMESPACE,
        container_port=spec["service-port"],
        ssh_key=spec.get("git-repo-secret", False)
        ))
    try:
        kubernetes.utils.create_from_yaml(client,None,data)
    except kubernetes.utils.FailToCreateError as e:
        if "AlreadyExists" in e.api_exceptions[0].body:
            print("Resource already Exists")
        else:
            print(e)

def delete_pigeon(api, appapi, spec):
    # Delete deployment
    resp = appapi.delete_namespaced_deployment(
        name=spec["app-name"],
        namespace=NAMESPACE,
        body=kubernetes.client.V1DeleteOptions(
            propagation_policy="Foreground", grace_period_seconds=5
        ),
    )
    resp = api.delete_namespaced_service(
        name=spec["app-name"],
        namespace=NAMESPACE
    )
    print(spec["app-name"] + " deleted")
def load_crd(namespace, name):

    client = kubernetes.client.ApiClient()
    custom_api = kubernetes.client.CustomObjectsApi(client)

    crd = custom_api.get_namespaced_custom_object(
        CRD_GROUP,
        CRD_VERSION,
        namespace,
        CRD_PLURAL,
        name,
    )

    return crd

def watcher():
    client = kubernetes.client.ApiClient()
    appv1 = kubernetes.client.AppsV1Api()
    v1 = kubernetes.client.CoreV1Api()
    custom_api = kubernetes.client.CustomObjectsApi(client)
    while True:
        w = kubernetes.watch.Watch()
        for event in w.stream(custom_api.list_namespaced_custom_object, group=CRD_GROUP, version=CRD_VERSION, namespace=NAMESPACE, plural=CRD_PLURAL):
            print("Event: %s %s %s" % (event['type'], event['object']['kind'], event['object']['metadata']['name']))
            if event['type'] == 'ADDED':
                build_pigeon(client, event['object']['spec'])
            if event['type'] == 'DELETED':
                delete_pigeon(v1, appv1, event['object']['spec'])

if __name__ == "__main__":
    watcher()