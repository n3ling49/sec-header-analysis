import os
import shutil

results_dir = "../../../ba_data/ba_dataset_clean"
rescan_dir = "../../../ba_data/rescan_data"

this_dir = os.path.dirname(os.path.abspath(__file__))

rescan_subdirs = os.listdir(rescan_dir)
for subdir in rescan_subdirs:
    print(subdir)
    folders = os.listdir(os.path.join(rescan_dir, subdir))
    for folder in folders:
        print(folder)
        files = os.listdir(os.path.join(rescan_dir, subdir, folder))
        for file in files:
            shutil.copy(os.path.join(rescan_dir, subdir, folder, file), os.path.join(results_dir, subdir, folder, file))
