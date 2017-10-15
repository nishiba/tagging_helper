import os
import re
from glob import glob

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render

from engine.crf_helper import train
from engine.crf_helper import predict
from tagging_helper.settings import BASE_DIR
from django.shortcuts import redirect


def _get_texts(file_id: str):
    file_path = os.path.join(BASE_DIR, 'app/data/raw_data/%s.txt') % file_id
    if not os.path.exists(file_path):
        return []
    with open(file_path) as f:
        texts = f.readlines()
    return texts


def _get_file_ids():
    ids = []
    for file_paths in glob(os.path.join(BASE_DIR, 'app/data/raw_data/*.txt')):
        regex = re.compile('([\w]+)\.txt$')
        m = regex.findall(file_paths)
        if len(m) > 0:
            ids.append(m[0])
    return ids


def _get_next_file_id(file_id: str):
    file_ids = _get_file_ids()
    if file_id not in file_ids:
        return None

    index = file_ids.index(file_id) + 1
    if index >= len(file_ids):
        return None

    return file_ids[index]


def _save_result(file_id: str, result: str):
    file_path = os.path.join(BASE_DIR, 'app/data/annotated_data/%s.txt') % file_id
    texts = result.split('\n')
    new_texts = []
    for text in texts:
        text = text.strip()
        if len(text) == 0:
            continue
        new_texts.append(text)

    text = '\n'.join(new_texts)
    if len(text) == 0:
        return
    with open(file_path, 'w') as f:
        f.write(text)


def raw_data_list(request):
    ids = _get_file_ids()
    params = request.GET
    # message = params['message'] if 'message' in params else ''
    message = ""
    return render(request, 'app/raw_data_list.html', {'file_paths': ids, 'message': message})


def _show_annotation(request, file_id: str):
    texts = _get_texts(file_id)
    return render(request, 'app/annotation.html', {'texts': texts, 'id': file_id})


def annotation_page(request: WSGIRequest):
    if len(request.GET) > 0:
        params = request.GET
        return _show_annotation(request, params['id'])
    return save_and_next(request)


def save_and_next(request: WSGIRequest):
    params = request.POST
    file_id = params['id']
    text = params['result']
    _save_result(file_id, text)
    next_file_id = _get_next_file_id(file_id)
    return _show_annotation(request, next_file_id)


def train_model(request: WSGIRequest):
    texts = []
    for path in glob('%s/app/data/annotated_data/*.txt' % BASE_DIR):
        with open(path, 'r') as f:
            texts += f.readlines()
    train(texts)
    return redirect('raw_data_list')


def apply_model(request: WSGIRequest):
    for path in glob('%s/app/data/raw_data/*.txt' % BASE_DIR):
        with open(path, 'r') as f:
            texts = f.readlines()
        annotated_texts = predict(texts)
        with open(path, 'w') as f:
            f.write('\n'.join(annotated_texts))
    return redirect('raw_data_list')

