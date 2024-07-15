from kubernetes import client, config, watch
import os
import requests

BRIDGE_API = os.getenv('BRIDGE_API', 'http://localhost:5000/api/resource')

def resolve_bridge_reference(resource_name, namespace):
    response = requests.get(f"{BRIDGE_API}/{namespace}/{resource_name}")
    if response.status_code == 200:
        return response.json().get('arn')
    return None

def watch_bridge_crds():
    config.load_incluster_config()
    v1 = client.CustomObjectsApi()
    namespace = os.getenv('NAMESPACE', 'default')
    stream = watch.Watch().stream(v1.list_namespaced_custom_object, group="bridge.io", version="v1", namespace=namespace, plural="bridges")

    for event in stream:
        crd = event['object']
        event_type = event['type']
        if event_type in ['ADDED', 'MODIFIED']:
            bridge_name = crd['spec'].get('bridge_name')
            if bridge_name:
                arn = resolve_bridge_reference(bridge_name, namespace)
                if arn:
                    print(f"Resolved ARN: {arn} for bridge name: {bridge_name} in namespace: {namespace}")

if __name__ == "__main__":
    watch_bridge_crds()
