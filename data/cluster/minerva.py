import subprocess

def builder():
    from data.run.driver.cluster_builder import Runner
    return Runner()

def copy_to():
    username = raw_input("Enter your Minerva username: ")
    subprocess.check_call("rsync -avz -e ssh --delete cluster {}@minerva.csc.warwick.ac.uk:~/slp-algorithm-tinyos".format(username), shell=True)

def copy_back(dirname):
    username = raw_input("Enter your Minerva username: ")
    subprocess.check_call("rsync -avz -e ssh {0}@caffeine.dcs.warwick.ac.uk:~/slp-algorithm-tinyos/cluster/{1}/*.txt data/results/{1}".format(username, dirname), shell=True)

def submitter():
    from data.run.driver.cluster_submitter import Runner as Submitter

    cluster_command = "msub -q smp -j oe -V -l nodes=1:ppn=4 -l walltime=20:00:00 -N {}"

    prepare_command = "module swap oldmodules minerva-2.0 ; module load iomkl/13.1.3/ScientificPython/2.8-python-2.7.6"
    
    return Submitter(cluster_command, prepare_command)
