import time, threading
import os, shutil
from os.path import isfile, join
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import queue
import pprint
pp = pprint.PrettyPrinter(indent=4)

file_src = os.getcwd() + '/old'
file_dest = os.getcwd() + '/new'

try:
    os.mkdir('new')
    os.mkdir('old')
except Exception as e: print(e)
 
my_queue = queue.Queue()
def storeInQueue(f):
  def wrapper(*args):
    my_queue.put(f(*args))
  return wrapper

@storeInQueue
def process_file(filename):
    if filename.endswith('PDF'):
        from script3 import pdf_processing
        events = pdf_processing(filename)

    elif filename.endswith('CSV'):
        from csv_processing import csv_to_json
        events = csv_to_json(filename)

    return events

def on_created(event):
    get_files = os.listdir(file_src)
    onlyfiles = [f for f in get_files if isfile(join(file_src,f))]
    print("Files:", onlyfiles)
    try:
        if os.path.isdir(file_dest):
            for filenm in onlyfiles:
                if not isfile(file_dest+'/'+filenm) and (filenm.endswith('PDF') or filenm.endswith('CSV')):
                    print("Filename:",file_dest+'/'+filenm)
                    t1 = threading.Thread(target=process_file, args=(filenm,))
                    t1.start()
                    t1.join()
                    my_data = my_queue.get()
                    print(my_data)
                try:
                    shutil.move(file_src+'/'+filenm, file_dest)
                except: pass
    except Exception as e: print(e)

if __name__ == '__main__':
    ignore_patterns = ["filewatcher.py", ".DS_Store"]
    patterns = ['*.PDF', '*.txt', '*.CSV']
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
            for thread in threading.enumerate(): 
                print(thread.name)
            time.sleep(1)
    finally:
        observer_obj.join()
        observer_obj.stop()
