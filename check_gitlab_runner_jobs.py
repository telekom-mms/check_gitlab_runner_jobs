#!/usr/bin/env python3
import httpx
import argparse
import sys

"""
Copyright 2023 Deutsche Telekom MMS GmbH
Maintainer: Julian Mühmelt
This script is an icinga2 monitoring check to check how many jobs are in a given state per runner
"""

def runner_string_to_dict(string):
    runner = {}
    if string.find(",") != -1:
        string_split = string.split(",")
        for a in string_split:
            name_id = a.split(":")
            runner.update({name_id[0].strip(): name_id[1].strip()})
    else:
        string_split = string.split(":")
        runner.update({string_split[0]: string_split[1]})
    return runner

# script
if __name__ == "__main__":
    # argparse configuration
    parser = argparse.ArgumentParser(description="This script is an icinga2 monitoring check to check how many jobs are in a given state per runner")
    parser.add_argument("-u", "--url", help="gitlab base url", required=True)
    parser.add_argument("-s", "--jobstate", help="job state (which jobs should be counted) default=running", default="running")
    parser.add_argument("-t", "--token", help="gitlab access token", required=True)
    parser.add_argument("-r", "--runner", help="runner name:id (multiple separated by comma) format: name:id,name:id", required=True)
    args = parser.parse_args()

    # argpars variables
    base_url = args.url
    job_state = args.jobstate
    gitlab_access_token = args.token
    runner = runner_string_to_dict(args.runner)

    # global variables
    api_path = "api/v4/runners/"
    header = {'PRIVATE-TOKEN': gitlab_access_token}
    output = []
    performance_data = []

    for name, id in runner.items():
        url = f'{base_url}{api_path}{id}/jobs?status={job_state}'
        r = httpx.get(url, headers=header)
        output.append(f"{name}: {len(r.json())}")
        performance_data.append(f"{name}={len(r.json())}")

    if output != [] and performance_data != []:
        output_string = ', '.join(output)
        performance_data_string = '; '.join(performance_data)
        print(f"ok - {output_string} | {performance_data_string}")
        sys.exit(0)
    else:
        print("unknown - no data found, please check gitlab url, gitlab access token and gitlab runner id")
        sys.exit(3)

