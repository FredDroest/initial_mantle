#!/usr/local/bin/python3

import argparse
import os
import sys
import subprocess
from mantlebio import client as mantle


def login_to_mantle(run_id: str, env=None, tenant=None):
    """
    Authenticates with mantle and loads the pipeline.
    """
    client = mantle.MantleClient(
        env=env, tenant_id=tenant)
    return client.load_pipeline(run_id)


def pull_entities(run):
    entities = run.pull_entities_input("fastqs")
    # Get their data from S3 into the current directory.
    for entity in entities:
        entity.download_s3("read1", "./" + entity.get_name() + ".R1-Sequences.fastq.gz")
        entity.download_s3("read2", "./" + entity.get_name() + ".R2-Sequences.fastq.gz")


def stage_input_entities(pipeline_id: str, stage_dir: str, env=None, tenant=None):
    """
    Function to download/stage entities for the given pipeline_id into output_dir.
    You need to implement the logic here based on your specific requirements.
    """
    run = login_to_mantle(pipeline_id, env, tenant)
    pull_entities(run)


def upload_outputs(pipeline_id, directory):
    """
    Upload all output files in the given directory to the given pipeline_id.
    """
    run = login_to_mantle(pipeline_id)
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                run.add_file_output(filename, file_path)


def main():
    parser = argparse.ArgumentParser(
        description="Download files for a given pipeline_id into a specified directory.")
    parser.add_argument("pipeline_id", type=str, help="The ID of the pipeline")
    parser.add_argument("stage_dir", type=str, default=".",
                        help="The directory where files should be downloaded")
    parser.add_argument("results_dir", type=str,
                        help="The directory of results")
    parser.add_argument(
        '--mantle_env', help='Mantle environment', default=None, required=False)
    parser.add_argument('--tenant', help='Mantle tenant', default=None, required=False)
    parser.add_argument('run_id', type=str, help='The run id of the pipeline')
    # Add any additional arguments here
    args = parser.parse_args()

    pipeline = login_to_mantle(args.run_id)

    # Call the download function
    stage_input_entities(args.pipeline_id, args.stage_dir,
                         args.mantle_env, args.tenant)

    upload_outputs(args.pipeline_id, args.results_dir, args.mantle_env, args.tenant)

    # Add your code here


if __name__ == '__main__':
    main()
