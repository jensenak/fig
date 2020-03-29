import pytest
import logging
import os

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

def get_path_vals(path, recursive=True):
    '''
    Returns values for all keys under a certain path (has a non-recursive option to get variables only from this level)
    May want to have a way to trace the values back to their origins? Maybe a flag for that?
    '''
    log.debug(f"get_path_vals called with {path} with recursion set to {recursive}")
    
    out = {}

    p = path.split("/")
    if recursive and len(p) > 1:
        out = get_path_vals("/".join(p[:-1])) # Ok, obviously it was a poor choice to make the functions work on a string...

    keys = list_path(path)

    for key in keys:
        try:
            out[key] = get_val(f"{path}/{key}")
        except PCPathError:
            continue # This error happens when the key contains another level of hierarchy instead of a single value

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

def test_get_flat_vals():
    assert get_path_vals("/dev/app", recursive=False) == {"name": "myapp", "db_pass": "thepassword"}

def test_get_path_vals():
    assert get_path_vals("/dev/app") == {"name": "myapp", "db_pass": "thepassword", "global":"one", "url": "dev.internal", "count":7}
    assert get_path_vals("/dev") == {"global":"one", "url": "dev.internal", "count":7}