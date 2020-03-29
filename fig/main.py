import logging

class PCPathError(Exception):
    pass

class PCValueError(Exception):
    pass

class PCRefError(Exception):
    pass

class TreeReader:
    def __init__(self, treeData, iter_limit=5):
        self.data = treeData
        self.log = logging.getLogger(__name__)
        self.iter_limit = iter_limit

    def get_val(self, path, iteration=0):
        '''
        Given a path to a specific value, return that value, after resolving references
        :param path: string of "/" delimited path elements
        :return: value at path
        :raises: NameError 
        '''
        self.log.debug(f"get_val called with {path} on iteration {iteration}")
        prefix = path.split("/")[1:-1]
        key = path.split("/")[-1]
        tmpdata = dict(self.data)

        # Try the global level first
        if key in self.data:
            val = self.data.get(key)

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
                if iteration > self.iter_limit:
                    raise PCRefError("Too many references")
                val = self.get_val(val[5:], iteration+1)
        except TypeError:
            pass # TypeError happens when val is not a string, so it definitely isn't a ref
        
        self.log.info(f"{path} resolved to {val}")
        return val


    def list_path(self, path):
        '''
        Lists keys under a certain path
        '''
        self.log.debug(f"list_path called with {path}")
        prefix = path.split("/")[1:]
        tmpdata = dict(self.data)
        for p in prefix:
                if p: # Ignore empty fields              
                    tmpdata = tmpdata[p]

        return list(tmpdata.keys())

    def get_path_vals(self, path, recursive=True):
        '''
        Returns values for all keys under a certain path (has a non-recursive option to get variables only from this level)
        May want to have a way to trace the values back to their origins? Maybe a flag for that?
        '''
        self.log.debug(f"get_path_vals called with {path} with recursion set to {recursive}")
        
        out = {}

        p = path.split("/")
        if recursive and len(p) > 1:
            out = self.get_path_vals("/".join(p[:-1])) # Ok, obviously it was a poor choice to make the functions work on a string...

        keys = self.list_path(path)

        for key in keys:
            try:
                out[key] = self.get_val(f"{path}/{key}")
            except PCPathError:
                continue # This error happens when the key contains another level of hierarchy instead of a single value

        return out