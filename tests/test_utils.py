# -*- coding: utf-8 -*-
"""
Utils 模块测试 — OpenSpec: cfg-01(ensure_storage)
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from http_server_cli.utils import (
    format_path,
    read_json,
    write_json,
    resolve_path,
    timestamp,
    ensure_storage,
)
import http_server_cli.utils as hs_utils

def _data_dir():
    return hs_utils.DATA_DIR

def _config_path():
    return hs_utils.CONFIG_PATH

def _registry_path():
    return hs_utils.REGISTRY_PATH

def _log_dir():
    return hs_utils.LOG_DIR

class TestFormatPath:
    """路径格式化"""

    def test_expands_home(self):
        path = os.path.expanduser('~') + '/CodeSpace/foo'
        result = format_path(path)
        assert result.startswith('~')

    def test_relative_path(self):
        assert format_path('/tmp/foo') == '/tmp/foo'

    def test_none_path(self):
        assert format_path(None) == 'None'

class TestJsonIO:
    """JSON 安全读写"""

    def test_write_and_read(self):
        path = os.path.join(_data_dir(), 'test.json')
        data = {'key': 'value', 'num': 42}
        write_json(path, data)
        loaded = read_json(path)
        assert loaded == data

    def test_read_missing_file(self):
        loaded = read_json('/nonexistent/path.json')
        assert loaded == {}

    def test_read_corrupted_json(self):
        path = os.path.join(_data_dir(), 'broken.json')
        with open(path, 'w') as f:
            f.write('NOT JSON {{{')
        loaded = read_json(path)
        assert loaded == {}

    def test_write_creates_directory(self):
        deep = os.path.join(_data_dir(), 'a', 'b', 'c', 'deep.json')
        write_json(deep, {'ok': True})
        assert os.path.exists(deep)
        loaded = read_json(deep)
        assert loaded == {'ok': True}

class TestResolvePath:
    """路径解析"""

    def test_resolve_relative(self):
        abs_path = resolve_path('.')
        assert os.path.isabs(abs_path)

    def test_resolve_absolute(self):
        # macOS 上 /tmp 是 /private/tmp 的符号链接，resolve() 会还原
        resolved = resolve_path('/tmp')
        assert resolved == '/private/tmp'

    def test_resolve_home(self):
        resolved = resolve_path('~')
        assert resolved == os.path.expanduser('~')

class TestTimestamp:
    def test_format(self):
        ts = timestamp()
        assert len(ts) == 19
        assert 'T' in ts

class TestEnsureStorage:
    """数据目录初始化"""

    def test_creates_dirs_and_files(self):
        import shutil
        shutil.rmtree(_data_dir(), ignore_errors=True)
        assert not os.path.exists(_data_dir())

        ensure_storage()

        assert os.path.isdir(_log_dir())
        assert os.path.isfile(_config_path())
        assert os.path.isfile(_registry_path())

    def test_creates_valid_default_config(self):
        import shutil
        shutil.rmtree(_data_dir(), ignore_errors=True)
        ensure_storage()

        config = read_json(_config_path())
        assert config['port'] == 8080
        assert config['domain'] == 'localhost'

    def test_creates_empty_registry(self):
        import shutil
        shutil.rmtree(_data_dir(), ignore_errors=True)
        ensure_storage()

        reg = read_json(_registry_path())
        assert reg == {'servers': []}
