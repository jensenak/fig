import pytest
import logging
import os
from fig import main as fig

log = logging.getLogger(__name__)
log.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))

data = {
    # Global values
    "global": "one",
    "count": 7,
    "url": "#REF:/internal/domain",
    # Values used to test references
    "external":{
        "domain": "www.com"
    },
    "internal":{
        "domain": "dev.internal"
    },
    # Environment structure tests
    "dev":{
        "app":{
            "name":"myapp",
            "db_pass": "#REF:/dev/db/password"
        },
        "db":{
            "password":"thepassword"
        }
    },
    "qa":{
        "app":{
            "count":10,
            "name":"myapp",
            "url":"#REF:/external/domain"
        }
    },
    "prod":{
        "app":{
            "url":"#REF:/qa/app/url"
        }
    },
    # Too much recursion test
    "too":{"much":{"recursion":"#REF:/too/much/recursion"}}
}

tree = fig.TreeReader(data)

def test_regular_path_resolution():
    assert tree.get_val("/global") == "one"
    assert tree.get_val("/dev/app/name") == "myapp"
    assert tree.get_val("/qa/app/count") == 10
    with pytest.raises(fig.PCValueError):
        tree.get_val("/qa/app/db_pass")
    with pytest.raises(fig.PCPathError):
        tree.get_val("/dev")

def test_path_overlap():
    assert tree.get_val("/dev/app/count") == 7

def test_references():
    assert tree.get_val("/dev/app/db_pass") == "thepassword"
    assert tree.get_val("/dev/app/url") == "dev.internal"

def test_reference_overlap():
    assert tree.get_val("/qa/app/url") == "www.com"

def test_recursive_refs():
    assert tree.get_val("/prod/app/url") == "www.com"
    with pytest.raises(fig.PCRefError):
        tree.get_val("/too/much/recursion")

def test_list_path():
    assert tree.list_path("/dev").sort() == ["app","db"].sort()

def test_get_flat_vals():
    assert tree.get_path_vals("/dev/app", recursive=False) == {"name": "myapp", "db_pass": "thepassword"}

def test_get_path_vals():
    assert tree.get_path_vals("/dev/app") == {"name": "myapp", "db_pass": "thepassword", "global":"one", "url": "dev.internal", "count":7}
    assert tree.get_path_vals("/dev") == {"global":"one", "url": "dev.internal", "count":7}