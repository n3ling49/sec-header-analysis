import os
import eval_utils

results_folder = "ba_dataset/"
this_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(this_dir, '../../results/'+results_folder)

subdirs = os.listdir(results_dir)

CHUNK_SIZE = 4

success_percentage = []
counter = 0
chunk_files = 0

subdirs.sort(key=eval_utils.sortfunc)

for dir in subdirs:
    sub_subdirs = os.listdir(os.path.join(results_dir, dir))
    sub_subdirs.sort(key=eval_utils.sortfunc)
    for subdir in sub_subdirs:
        files = os.listdir(os.path.join(results_dir, dir, subdir))
        counter += 1
        chunk_files += len(files)
        if counter == CHUNK_SIZE:
            success_percentage.append(round(chunk_files/(CHUNK_SIZE*1000),4))
            chunk_files = 0
            counter = 0
for i in range(0, len(success_percentage)):
    success_percentage[i]=round(success_percentage[i]*100,2)
print(success_percentage)