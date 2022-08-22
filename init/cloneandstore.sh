#!/bin/sh

if [ -f "/kee/ssh-privatekey" ]; then
    GIT_SSH_COMMAND='ssh -i /kee/ssh-privatekey -o IdentitiesOnly=yes' git clone $1 /app
else
    git clone $1 /app
fi

podman build -t container-svc.default.svc.cluster.local:5000/$2 /app
podman push container-svc.default.svc.cluster.local:5000/$2