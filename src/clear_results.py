import shutil
import os
import sys

def clear(rel_path, exceptions = []):

    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, rel_path)
    subdirs = os.listdir(results_dir)

    for dir in subdirs:
        if dir in exceptions:
            continue
        dir_path = os.path.join(results_dir, dir)
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        else:
            os.remove(dir_path)



#2023-11-08_15:57:00_;data_2023-11-08_15:57:00_results.json;failed_2023-11-08_15:57:00_results.json