# -*- coding: utf-8 -*-
# Repository Reporter
#
# Copyright (C) 2018
# Author: Eugenii Maksimenko <eugene.maksimenko@gmail.com>
# URL: https://github.com/evmaksimenko/reporeport
# For license information, see LICENSE.TXT

import ast
import os
import collections
import argparse
import logging

from nltk import pos_tag

log_format = '%(filename)s[LINE:%(lineno)3d]# %(levelname)-8s %(message)s'

logging.basicConfig(format=log_format, level=logging.INFO)

verb_tags = ['VB', 'VBZ', 'VBN', 'VBG', 'VBD', 'BE', 'BEG',
             'BEM', 'BER', 'BEZ', 'BEN', 'BED', 'BEDZ', 'VERB']


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t',
        '--topsize',
        action='store',
        type=int, default=10,
        help='set the number of common records to show (default 10)')
    return parser


def parse_parameters():
    parser = create_parser()
    params = parser.parse_args()
    return params


def flatten_list(list_to_flat):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in list_to_flat], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] in verb_tags


def is_name(node):
    return isinstance(node, ast.Name)


def is_function(node):
    return isinstance(node, ast.FunctionDef)


def is_system_name(name):
    return (name.startswith('__') and name.endswith('__'))


def split_snake_case_name(name):
    return [n for n in name.split('_') if n]


def get_verbs_from_name(name):
    return [w for w in split_snake_case_name(name) if is_verb(w)]


def get_python_filenames_in_path(path):
    filenames = []
    for dirname, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
    return filenames


def build_ast_tree_for_file(filename):
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        main_file_content = attempt_handler.read()
    try:
        tree = ast.parse(main_file_content)
    except SyntaxError as e:
        logging.ERROR(e)
        tree = None
    return tree


def build_ast_trees(path):
    trees = []
    filenames = get_python_filenames_in_path(path)
    logging.info('total %s files' % len(filenames))
    for filename in filenames:
        tree = build_ast_tree_for_file(filename)
        if tree:
            trees.append(tree)
    return trees


def get_all_names_from_ast(tree):
    names = [node.id for node in ast.walk(tree) if is_name(node)]
    return names


def get_function_names_from_ast(tree):
    function_names = [n.name.lower() for n in ast.walk(tree) if is_function(n)]
    return function_names


def get_all_words_in_path(path):
    trees = build_ast_trees(path)
    all_names = flatten_list([get_all_names_from_ast(t) for t in trees])
    user_def_names = [n for n in all_names if not is_system_name(n)]
    words = flatten_list([split_snake_case_name(n) for n in user_def_names])
    return words


def get_function_names_in_path(path):
    trees = build_ast_trees(path)
    func_names = flatten_list([get_function_names_from_ast(t) for t in trees])
    user_func_names = [n for n in func_names if not is_system_name(n)]
    return user_func_names


def get_top_verbs_in_path(path, top_size=10):
    func_names = get_function_names_in_path(path)
    verbs = flatten_list([get_verbs_from_name(n) for n in func_names])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    function_names = get_function_names_in_path(path)
    return collections.Counter(function_names).most_common(top_size)


if __name__ == "__main__":
    params = parse_parameters()
    top_size = params.topsize

    words = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]

    for project in projects:
        path = os.path.join('.', project)
        words += get_top_verbs_in_path(path, top_size)
    logging.info('total %s words, %s unique' % (len(words), len(set(words))))
    for word, occurence in collections.Counter(words).most_common(top_size):
        logging.info('%s %s' % (word, occurence))
