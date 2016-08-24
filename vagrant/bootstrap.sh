#!/bin/bash

cat > .profile <<EOF
source ~/.bashrc

# env vars for sota.toml.template
export AUTH_SERVER=http://192.168.50.1:9001
export AUTH_CREDENTIALS_FILE=/tmp/sota_credentials.toml

export CORE_SERVER=http://192.168.50.1:8080

export DBUS_NAME=org.genivi.SotaClient
export DBUS_PATH=/org/genivi/SotaClient
export DBUS_INTERFACE=org.genivi.SotaClient
export DBUS_SOFTWARE_MANAGER=org.genivi.SoftwareLoadingManager
export DBUS_SOFTWARE_MANAGER_PATH=/org/genivi/SoftwareLoadingManager
export DBUS_TIMEOUT=60

export DEVICE_PACKAGES_DIR=/tmp/
export DEVICE_PACKAGE_MANAGER=deb
export DEVICE_POLLING_INTERVAL=10
export DEVICE_CERTIFICATES_PATH=/rvi_sota_client/run/sota_certificates
export DEVICE_SYSTEM_INFO=system_info.sh

export GATEWAY_CONSOLE=false
export GATEWAY_DBUS=true
export GATEWAY_HTTP=false
export GATEWAY_RVI=false
export GATEWAY_WEBSOCKET=true

export RVI_CLIENT=http://192.168.50.1:8901
export RVI_EDGE=http://192.168.50.2:9080
export RVI_STORAGE_DIR=/var/sota
export RVI_TIMEOUT=20

# additional env vars for /rvi_sota_client/run/run.sh
export REGISTRY_SERVER=http://192.168.50.1:8083
export TEMPLATE_PATH=/rvi_sota_client/run/sota.toml.template
export OUTPUT_PATH=/home/vagrant/sota.toml
EOF
