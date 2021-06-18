import os
import tempfile
from fastapi import UploadFile

from daemon import daemon_logger
from daemon.models import DaemonID
from daemon.files import DaemonFile
from daemon.files import workspace_files
from daemon.excepts import Runtime400Exception

import pytest

cur_dir = os.path.dirname(os.path.abspath(__file__))
cur_filename = os.path.basename(__file__)


@pytest.mark.parametrize(
    'workdir, expected_response',
    [
        ('good_ws', ('devel', '3.7', 'echo Hello', [12345, 12344])),
        ('good_ws_filename', ('gpu', '3.9', '', [12345, 123456])),
        ('good_ws_nofile', ('devel', '3.8', '', [])),
        ('good_ws_emptyfile', ('devel', '3.8', '', [])),
        ('good_ws_multiple_files', ('devel', '3.7', 'echo Hello', [12345, 123456])),
        ('good_ws_wrong_values', ('devel', '3.8', '', [])),
    ],
)
def test_jinad_good_ws(workdir, expected_response):
    d = DaemonFile(workdir=f'{cur_dir}/{workdir}')
    assert d.build == expected_response[0]
    assert d.python == expected_response[1]
    assert d.run == expected_response[2]
    assert d.ports == expected_response[3]


@pytest.mark.parametrize('workdir', ['bad_ws_multiple_files'])
def test_jinad_bad_ws(workdir):
    with pytest.raises(Runtime400Exception):
        DaemonFile(workdir=f'{cur_dir}/{workdir}')


def _test_workspace_files():
    with tempfile.NamedTemporaryFile() as fp1, tempfile.NamedTemporaryFile() as fp2:
        fp1.write(b'Hello world1!')
        fp2.write(b'Hello world2!')
        fp1.flush()
        fp2.flush()
        fp1.seek(0, 0)
        fp2.seek(0, 0)
        id = DaemonID('jworkspace')
        print(fp1.read())
        files = [UploadFile(filename='a.txt'), UploadFile(filename='b.txt', file=fp2)]
        workspace_files(id, files, daemon_logger)
