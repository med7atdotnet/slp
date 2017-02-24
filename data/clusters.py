from __future__ import print_function, division

import os
import math
import subprocess

class ClusterCommon(object):
    def __init__(self, kind, url, ssh_auth, ppn, tpp, rpn):
        self.kind = kind
        self.url = url
        self.ssh_auth = ssh_auth
        self.ppn = ppn
        self.threads_per_processor = tpp
        self.ram_per_node = rpn

    def submitter(self, notify_emails=None): raise NotImplementedError
    def array_submitter(self, notify_emails=None): raise NotImplementedError

    def name(self):
        return type(self).__name__

    def builder(self):
        from data.run.driver.cluster_builder import Runner as Builder
        return Builder()

    def copy_to(self, dirname, user=None):
        username = self._get_username(user)
        subprocess.check_call("rsync -avz -e \"{0}\" cluster/__init__.py cluster/{3} {1}@{2}:~/slp-algorithms-tinyos/cluster".format(
            self.ssh_auth, username, self.url, dirname), shell=True)

    def copy_file(self, results_directory_path, filename, user=None):
        username = self._get_username(user)
        subprocess.check_call("rsync -avz -e \"{0}\" --rsync-path=\"mkdir -p ~/slp-algorithms-tinyos/{results_directory_path} && rsync\" {results_directory_path}/{filename} {1}@{2}:~/slp-algorithms-tinyos/{results_directory_path}/{filename}".format(
            self.ssh_auth, username, self.url, results_directory_path=results_directory_path, filename=filename), shell=True)

    def copy_back(self, dirname, user=None):
        username = self._get_username(user)
        subprocess.check_call("rsync -avz -e \"{0}\" {1}@{2}:~/slp-algorithms-tinyos/cluster/{3}/*.txt results/{3}".format(
            self.ssh_auth, username, self.url, dirname), shell=True)

    def _get_username(self, user):
        if user is not None:
            return user

        # Check in the ssh config for the user for this cluster
        try:
            import paramiko

            ssh_config = paramiko.SSHConfig()

            with open(os.path.expanduser("~/.ssh/config"), "r") as ssh_config_file:
                ssh_config.parse(ssh_config_file)

            lookup = ssh_config.lookup(self.name())

            user = lookup['user']

            print("Using the username '{}' from your '~/.ssh/config'. Rerun with the --user option to override this.".format(user))

            return user

        except (ImportError, KeyError):
            pass

        # Just ask them for their username
        return raw_input("Enter your {} username: ".format(self.name().title()))


    def _ram_to_ask_for(self, ram_for_os_mb=2 * 1024):
        return int(math.floor(((self.ram_per_node * self.ppn) - ram_for_os_mb) / self.ppn)) * self.ppn

    def _pbs_submitter(self, notify_emails=None):
        from data.run.driver.cluster_submitter import Runner as Submitter

        ram_to_ask_for_mb = self._ram_to_ask_for()

        # The -h flags causes the jobs to be submitted as held. It will need to be released before it is run.
        # Don't provide a queue, as the job will be routed to the correct place.
        cluster_command = "qsub -j oe -h -l nodes=1:ppn={} -l walltime={{}} -l mem={}mb -N \"{{}}\"".format(
            self.ppn, ram_to_ask_for_mb)

        if notify_emails is not None and len(notify_emails) > 0:
            print("Warning: flux does not currently have email notification setup")
            cluster_command += " -m ae -M {}".format(",".join(notify_emails))

        prepare_command = "cd $PBS_O_WORKDIR"

        return Submitter(cluster_command, prepare_command, self.ppn, job_repeats=1)

    def _pbs_array_submitter(self, notify_emails=None):
        from data.run.driver.cluster_submitter import Runner as Submitter

        ram_per_node_mb = self._ram_to_ask_for() / self.ppn

        num_jobs = 1
        num_array_jobs = self.ppn

        # The -h flags causes the jobs to be submitted as held. It will need to be released before it is run.
        # Don't provide a queue, as the job will be routed to the correct place.
        cluster_command = "qsub -j oe -h -t 1-{}%1 -l nodes=1:ppn={} -l walltime={{}} -l mem={}mb -N \"{{}}\"".format(
            num_array_jobs, num_jobs, num_jobs * ram_per_node_mb)

        if notify_emails is not None and len(notify_emails) > 0:
            print("Warning: flux does not currently have email notification setup")
            cluster_command += " -m ae -M {}".format(",".join(notify_emails))

        prepare_command = "cd $PBS_O_WORKDIR"

        return Submitter(cluster_command, prepare_command, num_jobs, job_repeats=num_array_jobs, array_job_variable="$PBS_ARRAYID")

    def _sge_submitter(self, notify_emails=None):
        from data.run.driver.cluster_submitter import Runner as Submitter

        # There is only 24GB available and there are 48 threads that can be used for execution.
        # There is no way that all the TOSSIM instances will not run over the memory limit!
        # Previous jobs have used about 16.8GB maximum with 12 jobs running on a 25x25 network, that is 1450MB per job.
        # So lets define the number of jobs to run with respect to an amount of RAM slightly greater than
        # that per job.
        # Expect this to need revision if larger networks are requested.
        #
        # TODO: Optimise this, so less RAM is requested per job for smaller network sizes.
        # This means that more threads can run and the smaller jobs finish even quicker!

        ram_for_os_mb = 512
        ram_per_job_mb = 1700
        jobs = int(math.floor(((self.ram_per_node * self.ppn) - ram_for_os_mb) / ram_per_job_mb))

        cluster_command = "qsub -cwd -V -j yes -h -S /bin/bash -pe smp {} -l h_rt={{}} -l h_vmem={}M -N \"{{}}\"".format(
            self.ppn, ram_per_job_mb)

        if notify_emails is not None and len(notify_emails) > 0:
            cluster_command += " -m ae -M {}".format(",".join(notify_emails))

        prepare_command = ""

        return Submitter(cluster_command, prepare_command, jobs, job_repeats=1)


class dummy(ClusterCommon):
    def __init__(self):
        super(dummy, self).__init__("dummy", None, None,
            ppn=12,
            tpp=1, # HT is disabled
            rpn=(32 * 1024) / 12 # 32GB per node
        )

    def copy_to(self, dirname, user=None):
        raise RuntimeError("Cannot copy to the dummy cluster")

    def copy_file(self, results_directory_path, filename, user=None):
        raise RuntimeError("Cannot copy to the dummy cluster")

    def copy_back(self, dirname, user=None):
        raise RuntimeError("Cannot copy back from the dummy cluster")

    def submitter(self, notify_emails=None):
        from data.run.driver.cluster_submitter import Runner as Submitter

        class DummySubmitter(Submitter):
            """Don't submit, just print the command"""
            def _submit_job(self, command):
                print(command)

        ram_to_ask_for_mb = self._ram_to_ask_for()

        cluster_command = "qsub -q serial -j oe -h -l nodes=1:ppn={} -l walltime={{}} -l mem={}mb -N \"{{}}\"".format(
            self.ppn, ram_to_ask_for_mb)

        if notify_emails is not None and len(notify_emails) > 0:
            cluster_command += " -m ae -M {}".format(",".join(notify_emails))

        prepare_command = " <prepare> "

        return DummySubmitter(cluster_command, prepare_command, self.ppn)

    def array_submitter(self, notify_emails=None):
        from data.run.driver.cluster_submitter import Runner as Submitter

        class DummySubmitter(Submitter):
            """Don't submit, just print the command"""
            def _submit_job(self, command):
                print(command)

        ram_per_job_mb = self.ram_per_node
        num_jobs = 1
        num_array_jobs = self.ppn

        cluster_command = "qsub -q serial -j oe -h -t 1-{}%1 -l nodes=1:ppn={} -l walltime={{}} -l mem={}mb -N \"{{}}\"".format(
            num_array_jobs, num_jobs, num_jobs * ram_per_job_mb)

        if notify_emails is not None and len(notify_emails) > 0:
            cluster_command += " -m ae -M {}".format(",".join(notify_emails))

        prepare_command = " <prepare> "

        return DummySubmitter(cluster_command, prepare_command, num_jobs, job_repeats=num_array_jobs, array_job_variable="$DUMMY_ARRAYID")

class flux(ClusterCommon):
    def __init__(self):
        super(flux, self).__init__("pbs", "flux.dcs.warwick.ac.uk", "ssh",
            ppn=12,
            tpp=1, # HT is disabled
            rpn=(32 * 1024) / 12 # 32GB per node
        )

    def submitter(self, notify_emails=None):
        return self._pbs_submitter(notify_emails=notify_emails)

    def array_submitter(self, notify_emails=None):
        return self._pbs_array_submitter(notify_emails=notify_emails)

class apocrita(ClusterCommon):
    def __init__(self):
        super(apocrita, self).__init__("sge", "frontend1.apocrita.hpc.qmul.ac.uk", "ssh",
            ppn=12,
            tpp=4,
            rpn=2 * 1024
        )

    def submitter(self, notify_emails=None):
        return self._sge_submitter(notify_emails=notify_emails)

class tinis(ClusterCommon):
    def __init__(self):
        super(tinis, self).__init__("pbs", "tinis.csc.warwick.ac.uk", os.path.expanduser("ssh -i ~/.ssh/id_rsa"),
            ppn=16,
            tpp=1,
            rpn=(64 * 1024) / 16 # 64GB per node
        )

    def submitter(self, notify_emails=None):
        return self._pbs_submitter(notify_emails=notify_emails)

def available():
    """A list of the names of the available clusters."""
    return ClusterCommon.__subclasses__()  # pylint: disable=no-member

def available_names():
    return [cls.__name__ for cls in available()]

def create(name):
    return [cls for cls in available() if cls.__name__ == name][0]()