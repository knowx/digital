#!/user/bin/env bash

groupadd -g 168 digital
useradd -u 168 -g 168 -c "Digital Daemons" -d /var/lib/digital digital

mkdir -p /var/log/digital
mkdir -p /var/lib/digital/certificates
mkdir -p /var/run/digital

chown digital.digital /var/log/digital
chown digital.digital /var/lib/digital
chown digital.digital /var/lib/digital/certificates
chown digital.digital /var/run/digital
