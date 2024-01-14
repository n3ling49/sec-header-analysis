import os

def sortfunc(s):
    return int(s.split('-')[0])

results_folder = "ba_dataset/"
this_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(this_dir, '../../results/'+results_folder)

subdirs = os.listdir(results_dir)
subdirs.sort(key=sortfunc)
for dir in subdirs:
    print('====================')
    print(dir)
    print('====================')
    sub_subdirs = os.listdir(os.path.join(results_dir, dir))
    sub_subdirs.sort(key=sortfunc)
    for i in range(0, len(sub_subdirs)):
        start_nr = int(sub_subdirs[i].split('-')[0])
        if i == 0:
            dir_start_nr = int(dir.split('-')[0])
            print(start_nr)
            if start_nr != dir_start_nr and start_nr != dir_start_nr+1:
                raise Exception('Start nr. does not match dir nr.')
        else:
            prev_start_nr = int(sub_subdirs[i-1].split('-')[0])
            if start_nr != prev_start_nr+1000:
                print(start_nr)
                print(prev_start_nr)
                print(sub_subdirs)
                raise Exception('Start nr. does not match previous start nr. + 1000')

        print(sub_subdirs[i])