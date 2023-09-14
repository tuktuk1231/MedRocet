import requests
import os
import datetime


def get_request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Ошбика при полученни данных:{e}")
        return None


def contact_information(url, i):
    try:
        for item in get_request(url):
            if item.get("id") == i:
                return item.get("name"), item.get("username"), item.get("email")
    except Exception as e:
        print(f"Ошбика при полученни контактных данных: {e}")
        return None


def max_id(url):
    try:
        max_num = max(item.get('id', 0) for item in get_request(url))
        return max_num
    except (requests.RequestException, ValueError) as e:
        print(f"Ошбика при полученни числа ид:{e}")
        return None


def tasks(url, i):
    try:
        current_tasks, completed_tasks = [], []
        summ_current, summ_completed = 0, 0
        for item in get_request(url):
            if item.get("userId") == i:
                if not item.get("completed"):
                    if len(item.get("title")) > 46:
                        current_tasks.append(item.get("title")[:46] + "...")
                    else:
                        current_tasks.append(item.get("title"))
                    summ_current += 1
                else:
                    if len(item.get("title")) > 46:
                        completed_tasks.append(item.get("title")[:46] + "...")
                    else:
                        completed_tasks.append(item.get("title"))
                    summ_completed += 1
        return summ_current, current_tasks, summ_completed, completed_tasks
    except Exception as e:
        print(f"Не удалось получить задачи пользователя: {e}")
        return None


url_task = 'https://json.medrocket.ru/todos'
url_name = 'https://json.medrocket.ru/users'
text = '''# Отчёт для {username}.
{name} <{email}> {data}
Всего задач: {summ}

## Актуальные задачи ({summ_current}):
{current_task}

## Завершённые задачи ({summ_completed}):
{completed_task}'''
directory_path = 'tasks'

if not os.path.exists(directory_path):
    os.makedirs(directory_path)

for i in range(max_id(url_name)):
    try:
        information = contact_information(url_name, i + 1)
        username, name, email = information
        task = tasks(url_task, i + 1)
        summ_current = task[0]
        current_task = "\n".join(["- " + str(task) for task in task[1]])
        summ_completed = task[2]
        summ = summ_current + summ_completed
        completed_task = "\n".join(["- " + str(task) for task in task[3]])
        data = datetime.datetime.today().strftime("%d.%m.%Y %H.%M")
        file_path = os.path.join(directory_path, name + ".txt")

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    second_line = lines[1].strip()
                    log_date = second_line.split()
                    new_name = name + log_date[2] + 'T' + log_date[3]
                    file.close()
                    new_file_path = os.path.join(os.path.dirname(file_path), new_name + ".txt")
                    os.rename(file_path, new_file_path)
        except OSError as e:
            if e.winerror == 183:
                new_file_path = os.path.join(os.path.dirname(file_path),
                                             new_name + datetime.datetime.today().strftime(".%S") + '.txt')
                os.rename(file_path, new_file_path)
        try:
            with open(file_path, "w") as file:
                file.write(text.format(username=username, name=name, email=email, data=data, summ=summ,
                                       summ_current=summ_current, current_task=current_task,
                                       summ_completed=summ_completed, completed_task=completed_task))

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            os.remove(file_path)
            os.rename(new_file_path, file_path)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
