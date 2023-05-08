from django.http import HttpResponse
import json, re, math, hashlib


class ApiFile:
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return str(self.file)

    def data(self):
        # Load data
        by = bytes()
        for chunk in self.file.chunks(chunk_size=0x100000):
            by += chunk

        return by

    def hash(self, sha=None):
        if sha is None:
            sha = hashlib.sha256()

        for chunk in self.file.chunks(chunk_size=0x1000):
            sha.update( chunk )

        return "".join("%02X" % x for x in sha.digest())


class CaterpillarMeta:
    def __init__(self, name, args, sess_req, sess_opt, post_req, post_opt,
                 get_req, get_opt, param_req, param_opt, file_req, file_opt,
                 files ):
        self.name = name

        self.args = args

        self.sess_req = sess_req
        self.sess_opt = sess_opt

        self.post_req = post_req
        self.post_opt = post_opt

        self.get_req = get_req
        self.get_opt = get_opt

        self.param_req = param_req
        self.param_opt = param_opt

        self.file_req = file_req
        self.file_opt = file_opt
        self.files = files

    def __str__(self):
        return self.name


# Value conversion
def convert_data( key, typ, raw, default ):
    val = None
    err = "Unknown type for %s" % key

    if issubclass( typ, str ):
        val = xstr( raw, default )
        err = None if val is not None else "Couldn't parse %s as string" % key
    elif issubclass( typ, bool ):
        val = xbool( raw, none=default, undefined=default)
        err = None if val is not None else "Couldn't parse %s as bool" % key
    elif issubclass( typ, int ):
        val = xint( raw, default )
        err = None if val is not None else "Couldn't parse %s as int" % key
    elif issubclass( typ, float ):
        val = xfloat( raw, default )
        err = None if val is not None else "Couldn't parse %s as float" % key
    elif issubclass( typ, dict ):
        contains = tuple() if default is None else default
        err = None

        # Testing cases mostly, we already have a dict of data
        if isinstance(raw, dict):
            return (raw, None)

        try:
            # Convert the string
            val = json.loads( raw )
            if val is None:
                return ( None, "Error, couldn't load valid json for %s" % key )

            #If json, check for contain keys, if the format is invalid, quit
            if len(contains) > 0 and not all(k in val for k in contains):
                missing = []
                for k in contains:
                    if k not in val:
                        missing.append( k )
                        val = None

                if len(missing) > 0:
                    err = "Invalid %s format. Required %s missing %s" % ( key, contains, missing)

        except json.decoder.JSONDecodeError as e:
            print(raw)
            return ( None, "Error processing json object %s [%s]" % (key, str(e)) )

    elif issubclass(typ, list):
        contains = tuple() if default is None else default
        err = None

        # Testing cases mostly, we already have a dict of data
        if isinstance(raw, list):
            return (raw, None)

        try:
            # Convert the string
            val = json.loads(raw)
            if val is None:
                return (None, "Error, couldn't load valid json for %s" % key)

        except json.decoder.JSONDecodeError as e:
            val = raw.split(',')

    return ( val, err )


# Internal function which runs the assignment action
def proc_args( kwargs, req_args, request_args, req_dict_ary, missing ):
    for x in request_args:
        if len(x) < 2:
            return "Invalid json value, must have at least key and type"

        # Pull my info out
        key = x[0]
        type = x[1]
        default = None if len(x) <= 2 else x[2]

        # Don't allow args that already exist to be overwritten!
        if key in kwargs:
            req_args[key] = kwargs[key]
            continue

        # Parse the key
        val, err = (default, None)
        for req_dict in req_dict_ary:
            if key in req_dict:
                val, err = convert_data( key, type, req_dict[key], default)
                if err is not None:
                    return err
                break

        # Store the data
        if val is not None:
            kwargs[key] = req_args[key] = val
        elif missing is not None:
            missing.append( key )
        else:
            kwargs[key] = None

    return None


def xstr( s, none='' ):
    return str(s) if s is not None else none


def xint( s, none=0, undefined=None ):
    try:
        if s == "undefined":
            return undefined
        return int(s) if s is not None and s != 'NaN' else none

    except ValueError:
        # Floating points and trailing letters wont fool me!!!
        m = re.search('^[-+]?[0-9]+', s)
        if m:
            return int(m.group(0))

        # can't go any further
        return none

    except TypeError:
        return none


def xfloat( s, none=0.0, undefined=None ):
    try:
        if s == "undefined":
            return undefined

        f = float(s) if s is not None and s != 'NaN' else none
        if math.isnan(f):
            return none

        return f

    except ValueError:
        # trailing letters wont fool me!!!
        m = re.search('^[-+]?[0-9]*\.?[0-9]+', s )
        if m:
            return float(m.group(0))

        # Can't go any further
        return none

    except TypeError:
        return none


def xbool( s, none=False, undefined=False ):
    # Are we string? try to figure out what that means
    if isinstance( s, str ):
        s = s.lower()
        if s == 'true':
            return True
        elif s == 'none' or s == 'null':
            return none
        elif s == 'undefined':
            return undefined
        else:
            return False

    # Special case none
    elif s is None:
        return none

    else:
        return bool(s)


# Raw response Info
def raw( objs, status, content, callback=None ):
    if callback:
        return HttpResponse( "%s(%s)" % (callback, objs),
                             status=status, content_type=content )
    else:
        return HttpResponse( objs, status=status, content_type=content )
