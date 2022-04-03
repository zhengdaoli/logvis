import os
import glob
import re
import json
import time
from collections import defaultdict
import numpy as np

dt = time.strftime("%Y%m%d%H%M", time.localtime())


log_base_dir = '/li_zhengdao/github/EEG/logs/'
log_file_regex = '*.log'
store_json_file = f'/li_zhengdao/github/data/seizure_metrics_DB.json'

m1 = 'micro f1'
m2 = 'macro f1'
m3 = 'weighted f1'

MAX_RUNS = 10
    
def load_DB():
    metrics = dict()
    if os.path.exists(store_json_file):
        with open(store_json_file, 'r') as f:
            metrics = json.load(f)
        print('loaded previous DB!!')
    return metrics

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
        print('stored')
        
def fill_empty(l, pad=0):
    len_l = len(l)
    if pad == "mean":
        pad = np.array(l).mean()
    for _ in range(MAX_RUNS-len_l):
        l.append(pad)


def exclude_log_name(name, without_list, and_with_list, or_with_list):
    patterns = []

    for pt in patterns:
        if re.match(pt, name) is not None:
            return False
    
    for s in without_list:
        if s in name:
            return True
    
    for s in and_with_list:
        if s not in name:
            return True
        
    for s in or_with_list:
        if s in name:
            return False
        
    return True
    
def exclude_log_data(data):
    d = np.array(data)
    if np.min(d) > 0.1 and np.min(d) < 0.6:
        return True
    return False


def skip(name, data,without_list, and_with_list, or_with_list):
    # skip = exclude_log_data(data)
    skip = exclude_log_data(data) or exclude_log_name(name,without_list, and_with_list, or_with_list)
    return skip

def topk_data(datas, K=5):
    topk = []
    top_mean = dict()
    for i, ms in enumerate(datas):
        for file_name, values in ms.items():
            top_mean[i] = np.array(values).mean()
    
    sorted_data = sorted(top_mean.items(), key=lambda x: x[1], reverse=True)
    K = len(datas) if len(datas) < K else K
    for i in range(K):
        id = sorted_data[i][0]
        topk.append(datas[id])
    
    return topk

def filter_data(db, topK, without_list, and_with_list, or_with_list):
    datas = []
    for file_name, v in db.items():
        data = dict()
        data[m1] = v[m1]
        data[m2] = v[m2]
        data[m3] = v[m3]
        if skip(file_name, data[m1],without_list, and_with_list, or_with_list):
            continue
        datas.append({file_name:data})
    
    metrics = defaultdict(list)
    for d in datas:
        for file_name, data in d.items():
            for m_name, v in data.items():
                metrics[m_name].append({file_name:v})
    # print(metrics)
    K = topK
    for m_name, data in metrics.items():
        K = len(data) if len(data) < K else topK
        topk = topk_data(data, K=K)
        for m in topk:
            for _, d in m.items():
                fill_empty(d, pad="mean")
        metrics[m_name] = topk
    return metrics, K
    
    
    

if __name__ == "__main__":
    update_DB()
