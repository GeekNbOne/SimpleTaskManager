from distutils.core import setup

setup(
    name='SimpleTaskManager',
    version='1.1.1',
    author='Luc Berthiaume',
    author_email='berthiaume.luc@gmail.com',
    packages=['task_manager'],
    #url='http://pypi.python.org/pypi/TowelStuff/',
   #license='LICENSE.txt',
    description='Simple Task Manager is a Python library for launching tasks and keep track of them.',
    long_description=open('README.txt').read(),
)