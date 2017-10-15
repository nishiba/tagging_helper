import os
from glob import glob
from typing import Tuple, List
import re

import MeCab
import pycrfsuite

mecab = MeCab.Tagger('mecabrc')


def get_dir():
    return os.path.dirname(os.path.abspath(__file__))


def tokenize(text: str):
    results = []
    mecab.parse('')
    node = mecab.parseToNode(text)
    while node:
        if len(node.surface) > 0:
            results.append((node.surface, node.feature))
        node = node.next
    return results


def remove(text, start, end) -> str:
    return text[:start] + text[end:]


def extract_annotation(text) -> Tuple[List, str]:
    results = []
    open_pattern = r'<span class="annotation([\d]+)">'
    closed_pattern = r'</span>'
    hit = re.search(open_pattern, text)
    while hit:
        open_position = hit.start()
        kind_index = int(hit.group(1))
        text = remove(text, hit.start(), hit.end())
        hit = re.search(closed_pattern, text)
        closed_position = hit.start()
        text = remove(text, hit.start(), hit.end())
        results.append((open_position, closed_position, kind_index))
        hit = re.search(open_pattern, text)
    return results, text


def add_annotation(tokens, annotations) -> List:
    for i in range(len(tokens)):
        tokens[i] = (tokens[i][0], tokens[i][1] + ',')
    if len(annotations) == 0:
        return tokens

    a = 0
    count = 0
    start, end, kind = annotations[a]
    for i in range(len(tokens)):
        token, feature = tokens[i]
        length = len(token)
        if count <= start < count + length:
            tokens[i] = (tokens[i][0], tokens[i][1] + 'B-%d' % kind)
        elif start < count < end:
            tokens[i] = (tokens[i][0], tokens[i][1] + 'I-%d' % kind)
        if end <= count + length:
            a += 1
            if a >= len(annotations):
                return tokens
            start, end, kind = annotations[a]
        count += length
    return tokens


def append_tag_token_feature(features):
    return '-'.join([x for x in features if x != '*'])


def make_training_data(text: str):
    annotations, text = extract_annotation(text)
    text = re.sub('\s', ' ', text)
    tokens = tokenize(text)
    tokens = add_annotation(tokens, annotations)
    results = []
    for token, feature in tokens:
        features = feature.split(',')
        label = features[-1]
        if len(label) == 0:
            label = 'O'
        results.append([token, append_tag_token_feature(features[:3]), label])
    return results


def make_feature_element(data, prefix=''):
    [word, pos_tag, label] = data[:3]
    return '%sword=%s' % (prefix, word), '%spos_tag=%s' % (prefix, pos_tag), '%slabel=%s' % (prefix, label)


def make_feature(data, position):
    word, pos_tag, _ = make_feature_element(data[position])
    features = ['bias', word, pos_tag]

    if position >= 2:
        word, pos_tag, label = make_feature_element(data[position - 2], '-2')
        features += [word, pos_tag, label]
    else:
        features += ['BOS']

    if position >= 1:
        word, pos_tag, label = make_feature_element(data[position - 1], '-1')
        features += [word, pos_tag, label]
    else:
        features += ['BOS']

    if position < len(data) - 1:
        word, pos_tag, label = make_feature_element(data[position + 1], '+1')
        features += [word, pos_tag, label]
    else:
        features += ['EOS']

    if position < len(data) - 2:
        word, pos_tag, label = make_feature_element(data[position + 2], '+2')
        features += [word, pos_tag, label]
    else:
        features += ['EOS']

    return features, data[position][2]


def text_to_feature_label(text):
    data = make_training_data(text)
    xseq = []
    yseq = []
    for i in range(len(data)):
        x, y = make_feature(data, i)
        xseq.append(x)
        yseq.append(y)
    return xseq, yseq


def train(texts):
    trainer = pycrfsuite.Trainer()
    for text in texts:
        xseq, yseq = text_to_feature_label(text)
        trainer.append(xseq, yseq)

    trainer.set_params({
        'c1': 1.0,  # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 100000000,  # stop earlier
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
    trainer.train(os.path.join(get_dir(), 'model.crfsuite'))


def judge_label(label: str):
    elts = label.split('-')
    if len(elts) == 1:
        return elts[0], None
    return elts[0], elts[1]


def predict_annotation(line, tagger):
    data = make_training_data(line)

    xseq = []
    labels = []
    for i in range(len(data)):
        x, y = make_feature(data, i)
        xseq.append(x)
        labels = tagger.tag(xseq)
        for j, p in enumerate(labels):
            data[j][2] = p
    words = [d[0] for d in data]
    sentence = ''
    current_state = 'O'
    print(''.join(words))
    print(''.join(labels))
    for word, label in zip(words, labels):
        state, annotation = judge_label(label)
        print(state, annotation)
        if current_state != 'O' and state != 'I':
            sentence += '</span>'
        if state == 'B':
            sentence += '<span class="annotation%s">' % annotation
        sentence += word
        current_state = state
    if current_state != 'O':
        sentence += '</span>'
    return sentence


def predict(texts):
    tagger = pycrfsuite.Tagger()
    tagger.open(os.path.join(get_dir(), 'model.crfsuite'))

    results = []
    for text in texts:
        annotated = predict_annotation(text, tagger)
        results.append(annotated)
    return results


if __name__ == '__main__':
    texts = []
    for path in glob('../app/data/annotated_data/*.txt'):
        with open(path, 'r') as f:
            texts += f.readlines()
    train(texts)
    print(get_dir())
    # main()
