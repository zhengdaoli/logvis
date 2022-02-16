import os
import glob
import re
import json
import time

dt = time.strftime("%Y%m%d%H%M", time.localtime())


log_base_dir = '/li_zhengdao/github/EEG/logs/'
log_file_regex = '*.log'
store_json_file = f'/li_zhengdao/github/seizure_metrics_DB.json'

m1 = 'micro f1'
m2 = 'macro f1'
m3 = 'weighted f1'

def update_DB():
    r1 = re.compile(f'{m1}:\s*(\d+\.\d+),.*{m2}:\s*(\d+\.\d+),.*{m3}:\s*(\d+\.\d+).*')

    metrics = load_DB()

    def need_skip_empty(d):
        if len(d[m1]) == 0:
            return True
        return False


    def need_skip_file(n):
        return n in metrics


    for file_path in glob.glob(os.path.join(log_base_dir, log_file_regex)):
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print('file name:', file_name)
        
        if need_skip_file(file_name):
            continue
        
        runs = {m1:[], m2:[], m3:[]}
        with open(file_path, 'r+') as f:
            for line in f.readlines():
                if line.__contains__('weighted f1'):
                    matched = r1.match(line.strip())
                    runs[m1].append(float(matched.group(1)))
                    runs[m2].append(float(matched.group(2)))
                    runs[m3].append(float(matched.group(3)))
        if need_skip_empty(runs):
            continue
        metrics[file_name] = runs

    with open(store_json_file, 'w') as f:
        json.dump(metrics, f)
        print('stored')`
        
def draw_metrics_from_DB(metrics):
    print(metrics)
    
def load_DB():
    metrics = dict()
    if os.path.exists(store_json_file):
        with open(store_json_file, 'r') as f:
            metrics = json.load(f)
        print('loaded previous DB', metrics)
    return metrics

if __name__ == '__main__':
    # update_DB()
    draw_metrics_from_DB(load_DB())
    

    

                
    
    