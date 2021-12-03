if test $num_subjobs -eq $_reproman_cmd_idx
then
# Not all jobs should do the cleanup. Ideally none of them should and there
# should be some post-job cleanup triggered through the batch system. But, at
# least for now, below is a brittle solution were the last job waits until it
# sees that all other jobs have exited and then runs the post-command stuff.
nstatus () {
    grep -E '^(succeed|fail)' "$metadir"/status.* | wc -l
}

echo "[ReproMan] waiting for all jobs to complete before running post-command..."
while test $(nstatus) -lt $num_subjobs
do
    sleep 1
done

echo "[ReproMan] post-command..."

{% block post_command %}
{% endblock %}

mkdir -p "$rootdir/completed/"
touch "$rootdir/completed/$jobid"
fi
