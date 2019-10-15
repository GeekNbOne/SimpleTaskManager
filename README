# Simple Task Manager

Simple Task Manager is a Python library for launching tasks and keep track of them.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install SimpleTaskManager.

```bash
pip install SimpleTaskManager
```

## Usage

```python
from task_manager import TaskManager, Task
from time import sleep

class Wait(Task):
    def target(self,wait):
        self.update_status(f'I will wait for {wait} seconds')
        sleep(wait - 1)
        self.raise_issue(4,f'I did not wait {wait} seconds','Wait has been subtracted by 1')
        self.update_status(f'I will now wait {wait} seconds')        
        sleep(wait)

tm = TaskManager()
tm.run_task(Wait, 2)

while tm.is_running:
    print(tm.tasks)
    sleep(1)

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)