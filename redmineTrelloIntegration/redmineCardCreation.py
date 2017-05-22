#!/usr/bin/env python
"""Script that will create the Tello cards from a Redmine task."""

import requests

__author__ = "Javier Grande Pérez"
__version__ = "1.0.0"
__maintainer__ = "Javier Grande Pérez"
__email__ = "raven.berserk@gmail.com"
__status__ = "Production"

# API Keys constants for connecting to Trello and Redmine
REDMINE_API_KEY = 'XXXXXXX'
TRELLO_API_KEY = 'XXXXXXX'
TRELLO_TOKEN = 'XXXXXXX'

# URL constants from Trello API and Redmine.
URL_REMINE = 'http://redmine.org/redmine/issues/'
URL_API_REMINE = 'http://redmine.org/redmine/issues/{0}.json?key={1}'
URL_TRELLO = 'https://api.trello.com/1/{0}?key={1}&token={2}'


class RedmineTask:
    pass


def create_dashboard(task_id: str, task_name: str)-> str:
    """ Create a new dashboard in Trello. """

    json_datos = {"name": '{0} - {1}'.format(task_id, task_name)}

    resp = requests.post(URL_TRELLO.format('boards', TRELLO_API_KEY,
                                           TRELLO_TOKEN), json=json_datos)

    return resp.json()['id'] if resp.ok else resp.raise_for_status()


def get_default_list_dashboard(dashboard_id: str)-> str:
    """ Get de first list of the dashboard. """

    resp = requests.get(URL_TRELLO.format('boards/{0}/lists'
                                          .format(dashboard_id),
                                          TRELLO_API_KEY, TRELLO_TOKEN))

    return resp.json()[0]['id'] if resp.ok else resp.raise_for_status()


def create_new_trello_card(task: RedmineTask, dash_list_id: str):
    """ Create a new card with task information. """

    card_name = 'HU#{0} - {1}'.format(task.id, task.name)
    card_description = 'HU#{0}: {1}/{0}'.format(task.id, URL_REMINE)
    end_date = '&due={0}'.format(task.endDate) if task.endDate else ''

    json_datos = {"name": card_name,
                  "idList": dash_list_id,
                  "desc": card_description,
                  "due": end_date}

    requests.post(URL_TRELLO.format('cards', TRELLO_API_KEY, TRELLO_TOKEN),
                  json=json_datos)


def get_redmine_task_info(task_id: str)-> dict:
    """ Get the Redmine Task information. """

    url_get_children = URL_API_REMINE + '&include=children'
    resp = requests.get(url_get_children.format(task_id, REDMINE_API_KEY))

    return resp.json()['issue'] if resp.ok else resp.raise_for_status()


def check_task_is_open(task: dict)-> bool:
    """ Check if the Redmine task is Open. """
    return 'closed_on' not in task or not task['closed_on']


def parse_task(redmine_task: dict)-> RedmineTask:
    """ Create a new RedmineTask from a json. """

    task = RedmineTask()
    task.id = redmine_task['id']
    task.name = redmine_task['subject']
    task.endDate = redmine_task.get('due_date')
    return task


def get_children_tasks(parent_task: dict)-> list:
    """ Get the information from the children task of the task. """

    children_list = []

    for child in parent_task['children']:
        child_task = get_redmine_task_info(child['id'])

        if check_task_is_open(child_task):
            if 'children' not in child_task:
                # The task has not children, so it is added to the list.
                children_list.append(parse_task(child_task))
            else:
                # The task has children, so the method is
                # called again to pick his children.
                children_list += get_children_tasks(child_task)

    return children_list


def main():
    """ Main method, will be responsible for creating the task cards. """

    try:
        task_id = input('Indicate the task you want to migrate: ')
        main_task = get_redmine_task_info(task_id)

        if 'children' in main_task:
            list_children_tasks = get_children_tasks(main_task)

            if list_children_tasks:
                print('There are {0} sub-task.'
                      .format(len(list_children_tasks)),
                      'The creation of the dashboard and cards begins')

                print('--- The creation of the dashboard begins.')
                dashboard_id = create_dashboard(main_task['id'],
                                                main_task['subject'])

                print('--- The default list is retrieved.')
                list_id = get_default_list_dashboard(dashboard_id)

                print('--- The creation of the cards begins.')
                for task in list_children_tasks:
                    try:
                        create_new_trello_card(task, list_id)
                    except Exception as error:
                        print('--- Error creating the card of the task {0} '
                              .format(task.id), error)
            else:
                print('The task {0} has not open sub-tasks'.format(task_id))
        else:
            print('The task {0} has not sub-task.'.format(task_id))

        input('The process completed successfully. :)')
    except Exception as error:
        print("Error {0}".format(error))
        input('Process not completed. :(')


if __name__ == '__main__':
    main()
