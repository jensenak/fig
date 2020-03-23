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

class PCValueError(Exception):
    pass

class PCRefError(Exception):
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
        if isinstance(val, dict):
            raise PCPathError("Path contains more than one value")
    except NameError:
        raise PCValueError("Path does not contain a value")

    try:
        if val[:5] == "#REF:":
            if iteration > iter_limit:
                raise PCRefError("Too many references")
            val = get_val(val[5:], iteration+1)
    except TypeError:
        pass # TypeError happens when val is not a string, so it definitely isn't a ref
    
    log.info(f"{path} resolved to {val}")
    return val


def list_path(path):
    '''
    Lists keys under a certain path
    '''
    log.debug(f"list_path called with {path}")
    prefix = path.split("/")[1:]
    tmpdata = dict(data)
    for p in prefix:
            if p: # Ignore empty fields              
                tmpdata = tmpdata[p]

    return list(tmpdata.keys())

def get_path_vals(path, recursive=False):
    '''
    Returns values for all keys under a certain path (has a recursive option)
    Debate: Should this flatten the values? Or should it preserve the nested hierarchy somehow?
    Going with flatten for now... we'll see if that turns out to be a bad call.
    '''
    log.debug(f"get_path_vals called with {path} with recursion set to {recursive}")
    keys = list_path(path)
    out = {}
    for key in keys:
        try:
            out[key] = get_val(f"{path}/{key}")
        except PCPathError:
            if recursive:
                for k, v in get_path_vals(f"{path}/{key}", True).items():
                    out[k] = v

    return out

def test_regular_path_resolution():
    assert get_val("/global") == "one"
    assert get_val("/dev/app/name") == "myapp"
    assert get_val("/qa/app/count") == 10
    with pytest.raises(PCValueError):
        get_val("/qa/app/db_pass")
    with pytest.raises(PCPathError):
        get_val("/dev")

def test_path_overlap():
    assert get_val("/dev/app/count") == 7

def test_references():
    assert get_val("/dev/app/db_pass") == "thepassword"
    assert get_val("/dev/app/url") == "dev.internal"

def test_reference_overlap():
    assert get_val("/qa/app/url") == "www.com"

def test_recursive_refs():
    assert get_val("/prod/app/url") == "www.com"
    with pytest.raises(PCRefError):
        get_val("/too/much/recursion")

def test_list_path():
    assert list_path("/dev").sort() == ["app","db"].sort()

def test_get_path_vals():
    assert get_path_vals("/dev/app") == {"name": "myapp", "db_pass": "thepassword"}
    assert get_path_vals("/dev", recursive=True) == {"name": "myapp", "db_pass": "thepassword", "password": "thepassword"}