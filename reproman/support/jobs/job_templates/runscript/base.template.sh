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
work_dir_tmp_bind=$( echo "$cmd" | grep -o -P "(?<=-w ')[^']+(?=')" )
work_dir_base=$(basename "$work_dir_tmp_bind")
software=$(dirname "$work_dir_tmp_bind" | xargs basename)
work_dir_scratch="$SCRATCH/work_dir/${software}/${work_dir_base}"
work_dir_tmp="/tmp/work_dir/${software}/${work_dir_base}"
walltime={{ walltime }}
walltime_seconds=$(echo "$walltime" | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
walltime_90p=$(printf "%.0f" $(echo "$walltime_seconds * 0.9 - 300" | bc))

mkdir -p "/tmp/work_dir/${software}"
if [[ -d "$work_dir_scratch" ]]; then
	rsync -a "$work_dir_scratch" "$work_dir_tmp"
fi

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
timeout "${walltime_90p}"s --preserve-status /bin/sh -c "$cmd" && \
    (rm -rf "$work_dir_tmp"; "succeeded" >"$metadir/status.$subjob") || \
    (rsync -a --delete  "$work_dir_tmp" "$work_dir_scratch" ; echo "failed: $?" >"$metadir/status.$subjob";
     mkdir -p "$metadir/failed" && touch "$metadir/failed/$subjob")
{% endblock %}

{% if killjob_factors is defined %}
{% include "includes/killjob-factors.template.sh" %}
{% else %}
{% include "includes/cleanup.template.sh" %}
{% endif %}