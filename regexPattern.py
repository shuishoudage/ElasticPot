import re

ROOT = re.compile(r'^/\?(pretty)?')
ROOT_PRETTY = re.compile(r'/\?pretty$')
INDICES = r'_cat/indices'
INDICES_PRETTY = re.compile(r'.*\?v$')
ERROR_PRETTY = re.compile(r'.*\?pretty$')
DELETE_ERROR_PRETTY = ROOT_PRETTY
