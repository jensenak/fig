import pytest
import logging
import os

data = {
    "global": "one",
    "count": 7,
    "url": "#REF:/internal/domain",
    "external":{
        "domain": "www.com"
    },
    "internal":{
        "domain": "dev.internal"
    },
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
    "too":{"much":{"recursion":"#REF:/too/much/recursion"}}
}
iter_limit = 5
log = logging.getLogger(__name__)
log.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))

class PCPathError(Exception):
    pass

def get_val(path, iteration=0):
    '''
    Given a path to a specific value, return that value, after resolving references
    :param path: string of "/" delimited path elements
    :return: value at path
    :raises: NameError 
    '''
    log.debug(f"get_val called with {path} on iteration {iteration}")
    prefix = path.split("/")[1:-1]
    key = path.split("/")[-1]
    tmpdata = dict(data)

    # Try the global level first
    if key in data:
        val = data.get(key)

    # Then search the path
    for p in prefix:
        if p: # Ignore empty fields              
            tmpdata = tmpdata[p]
        if key in tmpdata: # If a more specific key exists, use that value
            val = tmpdata[key]
    
    try:
        if val[:5] == "#REF:":
            if iteration > iter_limit:
                raise PCPathError("Too many references")
            val = get_val(val[5:], iteration+1)
    except NameError:
        raise PCPathError("Path does not contain a value")
    except TypeError:
        pass # TypeError happens when val is not a string, so it definitely isn't a ref
    
    log.info(f"{path} resolved to {val}")
    return val


def list_path(path):
    '''
    Lists keys under a certain path
    '''
    pass

def get_path_vals(path):
    '''
    Returns values for all keys under a certain path (single level)
    '''
    pass

def get_rpath_vals(path):
    '''
    Returns values for all keys under a certain path (recursive)
    '''
    pass

def test_regular_path_resolution():
    assert get_val("/global") == "one"
    assert get_val("/dev/app/name") == "myapp"
    assert get_val("/qa/app/count") == 10
    with pytest.raises(PCPathError):
        get_val("/qa/app/db_pass")

def test_path_overlap():
    assert get_val("/dev/app/count") == 7

def test_references():
    assert get_val("/dev/app/db_pass") == "thepassword"
    assert get_val("/dev/app/url") == "dev.internal"

def test_reference_overlap():
    assert get_val("/qa/app/url") == "www.com"

def test_recursive_refs():
    assert get_val("/prod/app/url") == "www.com"
    with pytest.raises(PCPathError):
        get_val("/too/much/recursion")