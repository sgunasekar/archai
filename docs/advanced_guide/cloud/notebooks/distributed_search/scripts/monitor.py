# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import time
import argparse
import json
import os
from typing import List, Dict
from azure.ai.ml.identity import AzureMLOnBehalfOfCredential
from azure.identity import DefaultAzureCredential
from store import ArchaiStore
from azure.ai.ml import MLClient


class JobCompletionMonitor:
    def __init__(self, store : ArchaiStore, ml_client : MLClient, pipeline_id=None, timeout=3600):
        self.store = store
        self.ml_client = ml_client
        self.timeout = timeout
        self.pipeline_id = pipeline_id

    def wait(self, model_ids: List[str]) -> List[Dict[str, str]]:
        """ wait for all the training jobs to finish and return the validation accuracies """
        completed = {}
        waiting = list(model_ids)
        start = time.time()
        failed = 0
        while len(waiting) > 0:
            for i in range(len(waiting) - 1, -1, -1):
                id = waiting[i]
                e = self.store.get_status(id)
                if self.pipeline_id is None and 'pipeline_id' in e:
                    self.pipeline_id = e['pipeline_id']
                if e is not None and 'status' in e and (e['status'] == 'completed' or e['status'] == 'failed'):
                    del waiting[i]
                    completed[id] = e
                    if e['status'] == 'failed':
                        error = e['error']
                        print(f'Training job {id} failed with error: {error}')
                        failed += 1
                    else:
                        msg = f"{e['val_acc']}" if 'val_acc' in e else ''
                        print(f'Training job {id} completed with validation accuracy: {msg}')
                    self.store.update_status_entity(e)

            # check the overall pipeline status just in case training jobs failed to even start.
            pipeline_status = None
            try:
                if self.pipeline_id is not None:
                    train_job = self.ml_client.jobs.get(self.pipeline_id)
                    if train_job is not None:
                        pipeline_status = train_job.status
            except:
                pass

            if pipeline_status is not None:
                if pipeline_status == 'Completed':
                    # ok, all jobs are done, which means if we still have waiting tasks then they failed to
                    # even start.
                    break
                elif pipeline_status == 'Failed':
                    for id in waiting:
                        e = self.store.get_status(id)
                        if 'error' not in e:
                            e['error'] = 'Pipeline failed'
                        if 'status' not in e or e['status'] != 'completed':
                            e['status'] = failed
                        self.store.update_status_entity(e)
                    raise Exception('Partial Training Pipeline failed')

            if len(waiting) > 0:
                if time.time() > self.timeout + start:
                    break
                print("AmlTrainingValAccuracy: Waiting 20 seconds for partial training to complete...")
                time.sleep(20)

        # awesome - they all completed!
        if len(completed) == 0:
            if time.time() > self.timeout + start:
                raise Exception(f'Partial Training Pipeline timed out after {self.timeout} seconds')
            else:
                raise Exception('Partial Training Pipeline failed to start')

        if failed == len(completed):
            raise Exception('Partial Training Pipeline failed all jobs')

        # stitch together the models.json file from our status table.
        print('Top model results: ')
        models = []
        for id in model_ids:
            row = {'id': id}
            e = completed[id] if id in completed else {}
            for key in ['nb_layers', 'kernel_size', 'hidden_dim', 'val_acc', 'job_id', 'status', 'error', 'epochs']:
                if key in e:
                    row[key] = e[key]
            models += [row]

        results = {
            'models': models
        }

        timespan = time.strftime('%H:%M:%S', time.gmtime(time.time() - start))
        print(f'Training: Distributed training completed in {timespan} ')
        print(f'Training: returning {len(results)} results:')
        print(json.dumps(results, indent=2))
        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='bin hexed config json info for MLClient')
    parser.add_argument('--timeout', type=int, help='pipeline timeout in seconds (default 1 hour)', default=3600)
    parser.add_argument('--job_names', required=True, help='comma separated list of job ids to monitor in the status table)')
    parser.add_argument('--output', required=True, help='folder to write the results to)')

    args = parser.parse_args()
    output = args.output
    timeout = args.timeout
    job_names = [x.strip() for x in args.job_names.split(',')]

    identity = AzureMLOnBehalfOfCredential()
    if args.config:
        print("Using AzureMLOnBehalfOfCredential...")
        workspace_config = str(bytes.fromhex(args.config), encoding='utf-8')
        print(f"Config: {workspace_config}")
        config = json.loads(workspace_config)
    else:
        print("Using DefaultAzureCredential...")
        config_file = "../.azureml/config.json"
        print(f"Config: {config_file}")
        config = json.load(open(config_file, 'r'))
        identity = DefaultAzureCredential()

    subscription = config['subscription_id']
    resource_group = config['resource_group']
    workspace_name = config['workspace_name']
    storage_account_key = config['storage_account_key']
    storage_account_name = config['storage_account_name']

    ml_client = MLClient(
        identity,
        subscription,
        resource_group,
        workspace_name
    )

    store = ArchaiStore(storage_account_name, storage_account_key)

    monitor = JobCompletionMonitor(store, ml_client, timeout=timeout)
    results = monitor.wait(job_names)
    if output is not None:
        with open(os.path.join(output, 'models.json'), 'w') as f:
            f.write(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()