import subprocess
import shutil

import pytest


def test_bysykkel_command_is_installed():
    assert shutil.which("bysykkel")


def test_bysykkel_list_command_returns_zero_exit_code():
    # NOTE: This queries the prod API. Might be better to instead replay previous responses or something similar.
    subprocess.check_call("bysykkel list", shell=True)
