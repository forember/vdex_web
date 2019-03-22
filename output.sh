#!/bin/sh
cd "$(dirname "$0")"
wget --mirror --page-requisites --adjust-extension --no-parent --convert-links \
     --directory-prefix=output "http://$1/"
