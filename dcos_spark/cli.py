"""Run and manage Spark jobs

Usage:
    dcos spark --help
    dcos spark --info
    dcos spark --version
    dcos spark --config-schema
    dcos spark run --help
    dcos spark run --submit-args=<spark-args> [--docker-image=<docker-image> --verbose]
    dcos spark status <submissionId> [--verbose]
    dcos spark log <submissionId> [--follow --lines_count=<lines_count> --file=<file>]
    dcos spark kill <submissionId> [--verbose]
    dcos spark webui

Options:
    --help                  Show this screen
    --info                  Show info
    --version               Show version
"""
from __future__ import print_function
import docopt
from dcos import mesos
from dcos_spark import constants, discovery, spark_submit, log


def master():
    return discovery.get_spark_dispatcher()


def run_spark_job(args):
    docker_image = args.get('--docker-image', constants.spark_mesos_image)
    if docker_image is None:
        docker_image = constants.spark_mesos_image
    return spark_submit.submit_job(master(), args['--submit-args'], docker_image, args['--verbose'])

def show_spark_submit_help():
    return spark_submit.show_help()


def job_status(args):
    return spark_submit.job_status(master(), args['<submissionId>'], args['--verbose'])


def kill_job(args):
    return spark_submit.kill_job(master(), args['<submissionId>'], args['--verbose'])

def log_job(args):
     dcos_client = mesos.DCOSClient()
     task = mesos.get_master(dcos_client).task(args['<submissionId>'])
     log_file = args.get('--file', "stdout")
     if log_file is None:
         log_file = "stdout"
     mesos_file = mesos.MesosFile(log_file, task=task, dcos_client=dcos_client)
     lines_count = args.get('--lines_count', "10")
     if lines_count is None:
         lines_count = "10"
     return log.log_files([mesos_file], args['--follow'], int(lines_count))

def print_webui(args):
    print(discovery.get_spark_webui())
    return 0

def print_schema():
    print("{}")

def main():
    args = docopt.docopt(
        __doc__,
        version='dcos-spark version {}'.format(constants.version), help=False)

    if args['--info']:
        print(__doc__.split('\n')[0])
    elif args['--config-schema']:
        print_schema()
    elif args['run'] and args['--help']:
        return show_spark_submit_help()
    elif args['run']:
        return run_spark_job(args)
    elif args['status']:
        return job_status(args)
    elif args['kill']:
        return kill_job(args)
    elif args['webui']:
        return print_webui(args)
    elif args['log']:
        return log_job(args)
    else:
        print(__doc__)
        return 1

    return 0
