### Updated CRD Definition for `bridge.io`


```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: bridges.bridge.io
spec:
  group: bridge.io
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                bridge_name:
                  type: string
                value:
                  type: string
  scope: Cluster
  names:
    plural: bridges
    singular: bridge
    kind: Bridge
    shortNames:
    - brg
```

### Folder Structure

```
eks-agent/
├── Dockerfile
├── requirements.txt
├── crd_controller.py
├── deployment.yaml
├── bridge_crd.yaml
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY crd_controller.py crd_controller.py

CMD ["python", "crd_controller.py"]
```

### requirements.txt

```plaintext
kubernetes
requests
```

### crd_controller.py

```python
from kubernetes import client, config, watch
import os
import requests

BRIDGE_API = os.getenv('BRIDGE_API', 'http://localhost:5000/api/resource')

def resolve_bridge_reference(resource_name):
    response = requests.get(f"{BRIDGE_API}/{resource_name}")
    if response.status_code == 200:
        return response.json().get('arn')
    return None

def watch_bridge_crds():
    config.load_incluster_config()
    v1 = client.CustomObjectsApi()
    stream = watch.Watch().stream(v1.list_cluster_custom_object, group="bridge.io", version="v1", plural="bridges")

    for event in stream:
        crd = event['object']
        event_type = event['type']
        if event_type in ['ADDED', 'MODIFIED']:
            bridge_name = crd['spec'].get('bridge_name')
            if bridge_name:
                arn = resolve_bridge_reference(bridge_name)
                if arn:
                    print(f"Resolved ARN: {arn} for bridge name: {bridge_name}")

if __name__ == "__main__":
    watch_bridge_crds()
```

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crd-controller
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crd-controller
  template:
    metadata:
      labels:
        app: crd-controller
    spec:
      containers:
      - name: crd-controller
        image: your-dockerhub-username/crd-controller:latest
        env:
        - name: BRIDGE_API
          value: "http://bridge-api-service.default.svc.cluster.local:5000"
```

### bridge_crd.yaml

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: bridges.bridge.io
spec:
  group: bridge.io
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                bridge_name:
                  type: string
                value:
                  type: string
  scope: Cluster
  names:
    plural: bridges
    singular: bridge
    kind: Bridge
    shortNames:
    - brg
```

### Steps for Deployment

1. **Build and Push Docker Image**
   ```sh
   docker build -t your-dockerhub-username/crd-controller:latest .
   docker push your-dockerhub-username/crd-controller:latest
   ```

2. **Apply the CRD**
   ```sh
   kubectl apply -f bridge-eks-agent/bridge_crd.yaml
   ```

3. **Deploy the Controller**
   ```sh
   kubectl apply -f bridge-eks-agent/deployment.yaml
   ```

This setup packages your CRD controller for easy deployment in an EKS cluster. The controller monitors and manages CRDs, interacting with the Bridge API to register and update resources.