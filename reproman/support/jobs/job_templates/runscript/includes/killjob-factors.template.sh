nstatus () {
    grep -E '^(succeed|fail)' "$metadir"/status.* | wc -l
}

if test $(nstatus) -eq 1; then

	echo "[ReproMan] waiting for threshold of jobs to complete before continuing..."

	job_name={{ job_name }}
	software="${job_name#*-}"
	dataset="${job_name%-*}"
	work_dir_scratch="$SCRATCH/work_dir/$software"
	work_dir_tmp="/tmp/work_dir/"
	killjob_factors={{ killjob_factors }}
	threshold_factor=$(echo "$killjob_factors" | awk -F, '{ print $1 }')
	add_time_factor=$(echo "$killjob_factors"| awk -F, '{ print $2 }')
	majority_num=$(echo "$num_subjobs * $threshold_factor" | bc -l | xargs printf "%.0f\n")

	while test $(nstatus) -lt "$majority_num"; do
    	sleep 1
	done

	echo "[ReproMan] waiting for all jobs to complete before running post-command..."
	runtime_stamp=$(squeue --job "$SLURM_JOB_ID" | tail -n 1 | awk '{ print $6 }')
	runtime_seconds=$(echo "${runtime_stamp#*-}" | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')
	if [[ "$runtime_stamp" =~ [-] ]]; then
		runtime_seconds=$((runtime_seconds+86400))
	fi
	add_time_seconds=$(echo "$runtime_seconds * $add_time_factor" | bc -l | xargs printf "%.0f\n")
	count=0
	while test $(nstatus) -lt "$num_subjobs" && test "$count" -lt "$add_time_seconds"; do
    	sleep 1
		count=$((count+1))
	done

	echo "[ReproMan] post-command..."

	{% block post_command %}
	{% endblock %}

	mkdir -p "$rootdir/completed/"
	touch "$rootdir/completed/$jobid"

	if test $(nstatus) -lt "$num_subjobs"; then
		collect.bash "$work_dir_tmp" "$work_dir_scratch"
		for d in "${work_dir_scratch}/${dataset}_*_0"; do
			subdir_0=$(basename "$d")
			subdir=$(echo "$subdir_0" | sed 's/_0//g')
			mv "$subdir" "${subdir}_old"
			mv "$subdir_0" "$subdir"
		done
		scancel "$SLURM_JOB_ID"
	fi
fi