
# Setup

1. Clone the SLP simulation framework

   * Anonymously:
     ```bash
     hg clone https://MBradbury@bitbucket.org/MBradbury/slp-algorithms-tinyos
     ```

   * With a username (one of the following):
     ```bash
     hg clone ssh://hg@bitbucket.org/MBradbury/slp-algorithms-tinyos
     ```
     ```bash
     hg clone https://<username>@bitbucket.org/MBradbury/slp-algorithms-tinyos
     ```

2. Clone the tinyos fork 
   ```bash
   git clone -b bradbury_2_1_2 https://github.com/MBradbury/tinyos-main.git
   ```

3. Create ~/tinyos.env with the following contents

   ```bash
   export TOSROOT="<fill in path to tinyos repo here>"
   export TOSDIR="$TOSROOT/tos"
   export CLASSPATH="$CLASSPATH:$TOSROOT/support/sdk/java:$TOSROOT/support/sdk/java/tinyos.jar"
   export MAKERULES="$TOSROOT/support/make/Makerules"
   export PYTHONPATH="$PYTHONPATH:$TOSROOT/support/sdk/python"
   ```

4. Add the following to ~/.bashrc before any interactivity check

   ```bash
   source ~/tinyos.env
   ```

5. Install python libraries

   ```bash
   pip install scipy numpy pandas more_itertools shutilwhich psutil pip --upgrade
   pip install git+git://github.com/MBradbury/python_java_random.git --upgrade
   ```

## Using pyenv (general)

If you do not have python installed, or have an install that requires
admin permissions to use pip install, then pyenv is a good alternative.

```bash
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
MAKE_OPTS=profile-opt pyenv install 2.7.12
pyenv global 2.7.12
```

## Using pyenv (on flux)

To install on flux there is a slightly different procedure:

```bash
module load flux-installers && pyenv-install.sh && source ~/.bashrc
MAKE_OPTS=profile-opt pyenv install 2.7.12
pyenv global 2.7.12
```

## Updating from upstream

Ideally you will have forked the slp-algorithms-tinyos repository.
You will want to pull updates from it by doing the following:

Modify your slp-algorithms-tinyos/.hg/hgrc to contain the following line under default:
"upstream = ssh://hg@bitbucket.org/MBradbury/slp-algorithms-tinyos"

If you are not using SSH keys, then you should use the following:
"upstream = https://<username>@bitbucket.org/MBradbury/slp-algorithms-tinyos"

You can then update from the upstream fork by doing the following:
```bash
hg pull -u upstream
```

You may need to perform a merge:
```bash
hg commit -m "Merge"
```

You will need to push what you have pulled to your fork:
```bash
hg push
```

You can update the tinyos repository by doing the following:
```bash
git pull https://github.com/MBradbury/tinyos-main bradbury_2_1_2
```


# Getting results repositories

Every algorithm should have an individual repository to store its results in.
One repository to be of likely interest is slp-results-protectionless which stores the results for the protectionless algorithm.

You should checkout this repository using something like the following command:

```bash
cd slp-algorithms-tinyos
mkdir results
cd results
hg clone https://MBradbury@bitbucket.org/MBradbury/slp-results-protectionless protectionless
```

The directories in the results directory should have names that match the algorithm name.

# Running on the cluster

In order to run your code on the cluster you will first need to checkout the files as described above.

The available clusters are described by individual files in slp-algorithms-tinyos/data/cluster.

## Safety Periods

The first step is to ensure that you have the correct safety period results on your computer.
If you are using a standard configuration then it is likely the slp-results-protectionless will contain the
necessary safety periods.
If you are using custom configurations, then it would be a good idea to fork the slp-results-protectionless
repository, gather the results and commit them to that repository.

One you have the necessary safety period results you can create the summary file like so:

```bash
./create.py protectionless analyse
```

You can then copy that summary to the desired cluster like so:

```bash
./create.py protectionless cluster <cluster> copy-result-summary
```

The cluster will now have the correct safety periods present to be able to run the simulations.

## Arguments

The next step is to modify the algorithm's CommandLine.py file to contain the correct set of arguments you wish to run.
To aid in testing there exists a dummy cluster driver which will print out the cluster command rather than execute it.

Use this to test that you have set up the correct parameters in CommandLine.py like so:
```bash
./create.py <algorithm> cluster submit dummy
```

## Build

You must now build all the combinations of arguments.
```bash
./create.py <algorithm> cluster build dummy
```

## Copy built binaries to cluster

To copy the built binaries to the cluster you need to execute the following command:
```bash
./create.py <algorithm> cluster copy <cluster>
```

## Submitting jobs to the cluster

To submit jobs to the cluster you will need to modify certain files.


The most important file to modify is Parameters.py, as this defined the parameters combinations
that will be run on the cluster. DO NOT modify Parameters.py.sample unless a new parameter is added.
Custom parameter combinations should only be specified in Parameters.py.


When submitting to the cluster it can be helpful to specify a time limit. It is important to specify a limit that is about
how long you expect the jobs to take, plus a bit extra for safety. If the jobs exceed the time limit they will
be killed. If they take much less time than the time limit they will take longer to be scheduled.

So considering this, I have found that it is best to specify different expected times for different sized networks.
With size 11 having a smaller time limit and size 25 having a larger time limit.

To begin with ensure that your algorithm's CommandLine.py is up-to-date.

You will need to modify slp-algorithms-tinyos/algorithm/<algorithm>/CommandLine.py to override _time_estimater.
Look at CommandLineCommon.py for the defaults.

To keep things simple you could just use a very large request time, but it is likely it will mean your jobs are not
run as often as they could be.


Now submit the jobs using:
```bash
./create.py <algorithm> cluster <cluster> submit
```

## Array Jobs

Alternatively you could use array jobs using the following command. The difference here is that rather than submitting
one job that takes up an entire node, many smaller jobs that only require one processor are submitted instead. This
should improve throughput of results on certain clusters. As the number of repeats performed per job will be smaller
make sure that you divide the walltime by the number of array jobs that will be created.

```bash
./create.py <algorithm> cluster <cluster> submit --array
```

## Copy back from cluster

Once all your jobs have finished you will need to copy them back from the cluster.
```bash
./create.py <algorithm> cluster <cluster> copy-back
```

You can then analyse the results like so:
```bash
./create <algorithm> analyse
```

Which will generate a result summary at "slp-algorithms-tinyos/results/<algorithm>/<algorithm>-results.csv".

## Resubmitting Jobs

If for any reason you need to go back and submit more of the same jobs that you have run before there are a few tricks.

When building or submitting jobs, the results summary file (in slp-algorithms-tinyos/results/<algorithm>/<algorithm>-results.csv)
will be read so that jobs will only be executed if the results show that not enough have been executed so far.

You can copy these result summaries to the cluster using:
```bash
./create.py <algorithm> cluster <cluster> copy-result-summary
```

If you want to ignore any existing results make sure to pass "no-skip-complete" when building or submitting cluster jobs.
Doing so will run all parameter combinations as specified in the <algorithm>/CommandLine.py file.
```bash
./create.py <algorithm> cluster dummy build --no-skip-complete
./create.py <algorithm> cluster <cluster> submit --no-skip-complete
```

## Job Notification

A useful feature is the ability to be notified when a job is completed or cancelled via email.
This can be done in two ways (#2 is recommended, as I tend to forget to do #1):

1. By specifying "--notify=<email address>" when submitting your jobs.

2. By editing your ~/.bashrc to contain "export SLP_NOTIFY_EMAILS=<email address>"