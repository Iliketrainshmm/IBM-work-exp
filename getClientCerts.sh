#!/bin/sh

# Make sure we have the mounted/certs directory
if [ ! -d mounted/certs ]; then
  mkdir -p mounted/certs;
fi

# Find the proxy pod, looks for name containing "analytics-proxy"
PROXY_POD=$(kubectl get pods -o=jsonpath='{range .items..metadata}{.name}{"\n"}{end}' | fgrep analytics-proxy)

# Download the certs from the pod (YOU NEED THE CORRECT NAMESPACE SET IN YOUR KUBECONFIG)
kubectl exec $PROXY_POD -- tar cf - "/etc/velox/certs/v2" | tar xf -

# Move them to the right directory
mv $(ls -d etc/velox/certs/v2/..$(date +%Y)*)/ca.crt mounted/certs/ca.crt
mv $(ls -d etc/velox/certs/v2/..$(date +%Y)*)/tls.key mounted/certs/tls.key
mv $(ls -d etc/velox/certs/v2/..$(date +%Y)*)/tls.crt mounted/certs/tls.crt

# Cleanup
rm -rf etc
