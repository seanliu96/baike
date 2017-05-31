#!/usr/bin/env python3
# coding:utf-8

import gensim
import jieba.analyse
import os
import logging
from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')

HTMLDIR = 'data/baike_html'
# DIRNOS = range(0, 1585)
DIRNOS = 1584


class MySentences(object):
    def __init__(self, dirpath, dirnos):
        self.dirpath = dirpath
        self.dirnos = dirnos
        self.dirno = 0
        self.dirpath_now = ''
        self.log_file = 'baike_word2vec_log'
        self.html_cleaner = Cleaner(scripts=True, javascript=True, comments=True,
                                    style=True, links=True, meta=False, add_nofollow=True,
                                    page_structure=False, processing_instructions=True, embedded=False,
                                    frames=True, forms=False, annoying_tags=False, remove_tags=None,
                                    remove_unknown_tags=False, safe_attrs_only=False)

    def __iter__(self):
        while self.dirno <= self.dirnos:
            self.dirpath_now = os.path.join(self.dirpath, str(self.dirno))
            with open(self.log_file, 'w') as f:
                f.write(self.dirpath_now)
            print(self.dirpath_now)
            for file_name in os.listdir(self.dirpath_now):
                # print(self.dirpath_now, file_name)
                soup = BeautifulSoup(self.html_cleaner.clean_html(open(os.path.join(self.dirpath_now, file_name), 'rb').read()), 'lxml')
                contents = soup.find_all(attrs={'class': 'para'})
                for content in contents:
                    words = jieba.cut(content.text)
                    '''
                    for word in words:
                        yield word
                    '''
                    yield list(words)
            self.dirno +=1


word2vec_sentences = MySentences(HTMLDIR, DIRNOS)
'''
for x in word2vec_sentences:
    print(x)
'''
model = gensim.models.Word2Vec(sentences=word2vec_sentences, workers=12)
model.save('baike_word2vec_model')