#!/bin/sh

set -x
exec > /var/log/startup.log
exec 2>&1

{% set user = data['user'] -%}
{% set channel = data['channel'] -%}
{% set split_branch = branch.split(':') -%}
{% set target_branch = split_branch[1] if split_branch | length == 2 else split_branch[0] -%}
{% set target_repository = split_branch[0] if split_branch | length == 2 else 'refinery29' -%}

my_short_name={{ name }}
my_ip=$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')

curl 'https://jenkins.prod.rf29.net/buildByToken/buildWithParameters' \
  --data 'job=CloudInit' \
  --data 'token=CloudInit' \
  --data "short_name=${my_short_name}" \
  --data "ip=${my_ip}" \
  --data "target_repo={{ target_repository }}" \
  --data "target_branch={{ target_branch }}" \
  --data "user={{ user }}" \
  --data "channel={{ channel }}" \
  -v

