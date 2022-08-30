#!/bin/sh

if [ -f "/kee/ssh-privatekey" ]; then
    cp /kee/ssh-privatekey /opt/kee && chmod 700 /opt/kee
    GIT_SSH_COMMAND='ssh -i /opt/kee -o IdentitiesOnly=yes -o StrictHostKeyChecking=no' git clone $1 /app
else
    git clone $1 /app
fi
if [ -f "/repokee/.dockerconfigjson" ]; then
    chmod -R 700 /repokee
    REGISTRY_AUTH_FILE=/repokee/.dockerconfigjson
fi
podman build -t registry-svc.default.svc.cluster.local:5000/$2 /app
podman push registry-svc.default.svc.cluster.local:5000/$2