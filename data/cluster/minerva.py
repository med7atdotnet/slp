import os, subprocess

def name():
    return __name__

def url():
    return "minerva.csc.warwick.ac.uk"

def ppn():
    return 12

def threads_per_processor():
    return 1

def builder():
    from data.run.driver.cluster_builder import Runner as Builder
    return Builder()

def copy_to():
    username = raw_input("Enter your {} username: ".format(name().title()))
    subprocess.check_call("rsync -avz -e \"ssh -i {0}/.ssh/id_rsa\" --delete cluster {1}@{2}:~/slp-algorithm-tinyos".format(
        os.environ['HOME'], username, url()), shell=True)

def copy_back(dirname):
    username = raw_input("Enter your {} username: ".format(name().title()))
    subprocess.check_call("rsync -avz -e \"ssh -i {0}/.ssh/id_rsa\" {1}@{2}:~/slp-algorithm-tinyos/cluster/{3}/*.txt results/{3}".format(
        os.environ['HOME'], username, url(), dirname), shell=True)

def submitter(notify_emails=None):
    from data.run.driver.cluster_submitter import Runner as Submitter

    # Size 25 network seem to take ~500mb per instance, so use 1500mb per instance to be safe
    ram_per_job_mb = 1500

    cluster_command = "msub -j oe -h -l nodes=1:ppn={} -l walltime=10:00:00 -l mem={}mb -N \"{{}}\"".format(ppn(), ppn() * ram_per_job_mb)

    if notify_emails is not None and len(notify_emails) > 0:
        cluster_command += " -m ae -M {}".format(",".join(notify_emails))

    prepare_command = "cd $PBS_O_WORKDIR ; module swap oldmodules minerva-2.0 ; module load iomkl/13.1.3/ScientificPython/2.8-python-2.7.6"

    return Submitter(cluster_command, prepare_command, ppn() * threads_per_processor())
