"""This module has functions to do with task related calls
to the KMD Nova api."""
import uuid

import requests

from itk_dev_shared_components.kmd_nova.authentication import NovaAccess
from itk_dev_shared_components.kmd_nova.nova_objects import Task
from itk_dev_shared_components.kmd_nova.util import datetime_from_iso_string, datetime_to_iso_string


def attach_task_to_case(case_uuid: str, task: Task, nova_access: NovaAccess) -> None:
    """Attach a Task object to a case in Nova.

    The Task object must have the following values set:
    uuid, title, statusCode, deadline.

    Args:
        case_uuid: The id of the case to attach the task to.
        task: A Task object describing the task.
        nova_access: The NovaAccess object used to authenticate.

    Raises:
        requests.exceptions.HTTPError: If the request failed.
    """
    url = f"{nova_access.domain}/api/Task/Import?api-version=1.0-Task"

    payload = {
        "common": {
            "transactionId": str(uuid.uuid4()),
            "uuid": task.uuid
        },
        "caseUuid": case_uuid,
        "title": task.title,
        "description": task.description,  # Optional
        "caseworkerPersonId": task.case_worker_uuid,  # Optional
        "statusCode": task.status_code,
        "deadline": datetime_to_iso_string(task.deadline),
        "startDate": datetime_to_iso_string(task.started_date),  # Optional
        "closeDate": datetime_to_iso_string(task.closed_date),  # Optional
        "taskTypeName": "Aktivitet"
    }

    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {nova_access.get_bearer_token()}"}
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()


def get_tasks(case_uuid: str, nova_access: NovaAccess, limit: int = 100) -> list[Task]:
    """Get tasks attached to a case.

    Args:
        case_uuid: The id of the case.
        nova_access: The NovaAccess object used to authenticate.
        limit: The max number of tasks to get. Defaults to 100.

    Returns:
        A list of Task objects.

    Raises:
        requests.exceptions.HTTPError: If the request failed.
    """
    url = f"{nova_access.domain}/api/Task/GetList?api-version=1.0-Task"

    payload = {
        "common": {
            "transactionId": str(uuid.uuid4())
        },
        "caseUuid": case_uuid,
        "paging": {
            "startRow": 1,
            "numberOfRows": limit
        }
    }

    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {nova_access.get_bearer_token()}"}
    response = requests.put(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    if 'taskList' not in response.json():
        return []

    tasks = []
    for task_dict in response.json()['taskList']:
        task = Task(
            uuid = task_dict['taskUuid'],
            title = task_dict['taskTitle'],
            description = task_dict.get('taskDescription'),
            case_worker_ident = task_dict['caseWorker']['ident'],
            case_worker_uuid = task_dict['caseWorker']['id'],
            status_code = task_dict['taskStatusCode'],
            deadline = datetime_from_iso_string(task_dict.get('taskDeadline')),
            created_date = datetime_from_iso_string(task_dict.get('taskCreateDate')),
            started_date = datetime_from_iso_string(task_dict.get('taskStartDate')),
            closed_date = datetime_from_iso_string(task_dict.get('taskCloseDate'))
        )
        tasks.append(task)

    return tasks


def update_task(task: Task, case_uuid: str, nova_access: NovaAccess):
    """Update a task that already exists in KMD Nova with new
    information.

    Args:
        task: The Task object describing the updated task.
        case_uuid: The id of the case the task belongs to.
        nova_access: The NovaAccess object used to authenticate.

    Raises:
        requests.exceptions.HTTPError: If the request failed.
    """
    url = f"{nova_access.domain}/api/Task/Update?api-version=1.0-Task"

    payload = {
        "common": {
            "transactionId": str(uuid.uuid4())
        },
        "uuid": task.uuid,
        "caseUuid": case_uuid,
        "title": task.title,
        "description": task.description,
        "caseworkerPersonId": task.case_worker_uuid,
        "statusCode": task.status_code,
        "deadline": datetime_to_iso_string(task.deadline),
        "startDate": datetime_to_iso_string(task.started_date),
        "closeDate": datetime_to_iso_string(task.closed_date),
        "taskType": "Aktivitet"
    }

    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {nova_access.get_bearer_token()}"}
    response = requests.put(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
