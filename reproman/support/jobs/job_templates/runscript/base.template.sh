#!/bin/sh
{% block header %}
{% endblock %}

set -eu

jobid={{ _jobid }}
subjob=$1
num_subjobs={{ _num_subjobs }}

metadir={{ shlex_quote(_meta_directory) }}
rootdir={{ shlex_quote(root_directory) }}
workdir={{ shlex_quote(working_directory) }}

_reproman_cmd_idx=$(($subjob + 1))
export _reproman_cmd_idx

echo "submitted" >"$metadir/status.$subjob"
echo "[ReproMan] pre-command..."

{% block pre_command %}
cd "$workdir"
{% endblock %}

get_command () {
    perl -n0e \
         '$idx=$ENV{_reproman_cmd_idx}; print "$_" if $. == $idx;' \
         "$metadir/command-array"
}

cmd=$(get_command)
if test -z "$cmd"
then
    echo "[ReproMan] failed getting command at position $_reproman_cmd_idx" >&2
    echo "pre-command failure" >"$metadir/status.$subjob"
    exit 1
fi

echo "running" >"$metadir/status.$subjob"
echo "[ReproMan] executing command $cmd"
echo "[ReproMan] ... within $PWD"
{% block command %}
/bin/sh -c "$cmd" && \
    echo "succeeded" >"$metadir/status.$subjob" || \
    (echo "failed: $?" >"$metadir/status.$subjob";
     mkdir -p "$metadir/failed" && touch "$metadir/failed/$subjob")
{% endblock %}

{% if killjob_factors is defined %}
{% include "includes/killjob-factors.template.sh" %}
{% else %}
{% include "includes/cleanup.template.sh" %}
{% endif %}