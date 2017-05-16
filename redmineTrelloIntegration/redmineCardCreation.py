"""
Author: Javier Grande Perez
Description: Script that will create the Tello cards from a Redmine task.
"""
import requests

# API Keys constants for connecting to Trello and Redmine
redmineKey = 'XXXXXXX'
trelloKey = 'XXXXXXX'
trelloToken = 'XXXXXXX'

# URL constants from Trello API and Redmine.
urlRedmine = 'http://redmine.org/redmine/issues/'
urlAPIRedmine = 'http://redmine.org/redmine/issues/{0}.json?key={1}'
urlTrello = 'https://api.trello.com/1/{0}?key={1}&token={2}'

class RedmineTask:
    pass

def create_dashboard(taskId:str,taskName:str) -> str:
    """ Create a new dashboard in Trello. """
    
    jsonDatos = {"name":'{0} - {1}'.format(taskId,taskName)}
    response = requests.post(urlTrello.format('boards',trelloKey,trelloToken),json=jsonDatos)
    return response.json()['id'] if response.ok else response.raise_for_status()

def get_default_list_dashboard(dashboardId:str) -> str:
    """ Get de first list of the dashboard. """
    
    response = requests.get(urlTrello.format('boards/{0}/lists'.format(dashboardId),trelloKey,trelloToken))
    return response.json()[0]['id'] if response.ok else response.raise_for_status()

def create_new_trello_card(redmineTask:RedmineTask, dashListId:str):
    """ Create a new card with task information. """

    cardName = 'HU#{0} - {1}'.format(redmineTask.id, redmineTask.name)
    cardDescription = 'HU#{0}: {1}/{0}'.format(redmineTask.id, urlRedmine)
    endDate = '&due={0}'.format(redmineTask.endDate) if redmineTask.endDate else ''

    jsonDatos = {"name":cardName,
            "idList":dashListId,
            "desc":cardDescription,
            "due":endDate}
    requests.post(urlTrello.format('cards',trelloKey,trelloToken),json=jsonDatos)

def get_redmine_task_info(taskId:str) -> dict:
    """ Get the Redmine Task information. """

    response = requests.get(urlAPIRedmine.format(taskId,redmineKey)+'&include=children')
    return response.json()['issue'] if response.ok else response.raise_for_status()

def check_task_is_open(task:dict) -> bool:
    """ Check if the Redmine task is Open. """
    return 'closed_on' not in task or not task['closed_on']

def parse_task(redmineTask:dict) -> RedmineTask:
    """ Create a new RedmineTask from a json. """
    
    task = RedmineTask()
    task.id = redmineTask['id']
    task.name = redmineTask['subject']
    task.endDate = redmineTask.get('due_date')
    return task

def get_children_tasks(parentTask:dict) -> list:
    """ Get the information from the children task of the task. """

    childrenList = []

    for child in parentTask['children']:
        childTask = get_redmine_task_info(child['id'])

        if check_task_is_open(childTask):
            if 'children' not in childTask:
                # The task has not children, so it is added to the list.
                childrenList.append(parse_task(childTask))
            else:
                # The task has children, so the method is called again to pick his children.
                childrenList = childrenList + get_children_tasks(childTask)

    return childrenList

def main():
    """ Main method, will be responsible for creating the task cards. """
    
    try:
        taskId = input('Indicate the task you want to migrate: ')
        mainTask = get_redmine_task_info(taskId)

        if 'children' in mainTask:
            listChildrenTasks = get_children_tasks(mainTask)

            if listChildrenTasks:
                print('There are {0} sub-task. The creation of the dashboard and cards begins')

                print('--- The creation of the dashboard begins.')
                dashboardId = create_dashboard(mainTask['id'],mainTask['subject'])

                print('--- The default list is retrieved.')
                listId = get_default_list_dashboard(dashboardId)

                print('--- The creation of the cards begins.')
                for task in listChildrenTasks:
                    try:
                        create_new_trello_card(task,listId)
                    except Exception as error:
                        print('--- There was an error creating the card of the task {0}: {1}'.format(task.id, error))
            else:
                print('The task {0} has not open sub-tasks'.format(taskId))
        else:
            print('The task {0} has not sub-task.'.format(taskId))

        input('The process completed successfully. :)')
    except Exception as error:
        print("Error {0}".format(error))
        input('Process not completed. :(')
        
main()
