nstatus () {
    grep -E '^(succeed|fail)' "$metadir"/status.* | wc -l
}

if test $(nstatus) -eq 1
then

echo "[ReproMan] waiting for threshold of jobs to complete before continuing..."

killjob_factors={{ killjob_factors }}
threshold_factor=$(echo "$killjob_factors" | awk -F, '{ print $1 }')
add_time_factor=$(echo "$killjob_factors"| awk -F, '{ print $2 }')
majority_num=$(echo "$num_subjobs * $threshold_factor" | bc -l | xargs printf "%.0f\n")
runtime_stamp=$(squeue --job "$SLURM_JOB_ID" | tail -n 1 | awk '{ print $6 }')
runtime_seconds=$(echo "$runtime_stamp" | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
add_time_seconds=$(echo "$runtime_seconds * $add_time_factor" | bc -l | xargs printf "%.0f\n")

while test $(nstatus) -lt "$majority_num"
do
    sleep 1
done

echo "[ReproMan] waiting for all jobs to complete before running post-command..."
count=0
while test $(nstatus) -lt "$num_subjobs" && test "$count" -lt "$add_time_seconds"
do
    sleep 1
	count=$((count+1))
done

echo "[ReproMan] post-command..."

{% block post_command %}
{% endblock %}

mkdir -p "$rootdir/completed/"
touch "$rootdir/completed/$jobid"

scancel "$SLURM_JOB_ID"
fi