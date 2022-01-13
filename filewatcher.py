import time
import os, shutil
from os.path import isfile, join
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

file_src = os.getcwd() + '/old'
file_dest = os.getcwd() + '/new'

try:
    os.mkdir('new')
except Exception as e: print(e)

def on_created(event):
    get_files = os.listdir(file_src)
    onlyfiles = [f for f in get_files if isfile(join(file_src,f))]
    try:
        if os.path.isdir(file_dest):
            for filenm in onlyfiles:
                try:
                    shutil.move(file_src+'/'+filenm, file_dest)
                except: continue
    except Exception as e: print(e)

if __name__ == '__main__':


    ignore_patterns = ["filewatcher.py"]
    patterns = ['*.PDF', '*.txt']
    ignore_directories = False
    case_sensitive = True
    handling_event = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    handling_event.on_created = on_created
    path = '.'
    observer_obj = Observer()
    observer_obj.schedule(handling_event, path, recursive=True)

    observer_obj.start()
    try:
        while observer_obj.is_alive():
            time.sleep(1)
    finally:

        observer_obj.join()
        observer_obj.stop()
