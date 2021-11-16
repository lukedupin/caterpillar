from caterpillar_api import monarch, util


# Request args wrapper class
class Cocoon:
    def __init__(self, auth=None, sess_req=[], sess_opt=[], get_req=[], get_opt=[], post_req=[], post_opt=[], file_req=[], file_opt=[], files=None, meta=None ):
        def _args( args ):
            return args if isinstance( args, tuple) or isinstance( args, list ) else (args,)

        self.auth = auth
        self.sess_req = _args( sess_req )
        self.get_req = _args( get_req )
        self.post_req = _args( post_req )
        self.file_req = file_req

        self.sess_opt = _args( sess_opt )
        self.get_opt = _args( get_opt )
        self.post_opt = _args( post_opt )
        self.file_opt = file_opt

        self.files = files

        self.meta = meta

    def __call__(self, func):
        def wrapper( *args, **kwargs ):
            # Get my request object
            request = kwargs['request'] if 'request' in kwargs else args[0]

            # If we don't have a request, or json_api is False/None just call the function directly
            if request is None or 'json_api' in kwargs and not kwargs['json_api']:
                return func(*args, **kwargs)

            # Uncomment if application/json content-type
            #request.POST = json.loads( request.body.decode('utf-8'))

            #print(kwargs)
            #print( request.POST )
            #print( request.GET )
            #print( request.body.decode('utf-8') )

            req_args = {}
            get_missing = []
            post_missing = []
            sess_missing = []
            file_missing = []
            #print(request.POST)

            # Required args
            err = util.proc_args( kwargs, req_args, self.sess_req, request.session, sess_missing )
            if err is not None:
                return monarch.fail( request, err )
            err = util.proc_args( kwargs, req_args, self.post_req, request.POST, post_missing )
            if err is not None:
                return monarch.fail( request, err )
            err = util.proc_args( kwargs, req_args, self.get_req, request.GET, get_missing )
            if err is not None:
                return monarch.fail( request, err )

            # Optional args, no missing accumulation
            err = util.proc_args( kwargs, req_args, self.sess_opt, request.session, None )
            if err is not None:
                return monarch.fail( request, err )
            err = util.proc_args( kwargs, req_args, self.post_opt, request.POST, None )
            if err is not None:
                return monarch.fail( request, err )
            err = util.proc_args( kwargs, req_args, self.get_opt, request.GET, None )
            if err is not None:
                return monarch.fail( request, err )

            # Files are simple, just check if they exist, the type is always a string filename
            if request.method == 'POST':
                for file in self.file_req:
                    if file in request.FILES:
                        kwargs[file] = util.ApiFile( request.FILES[file] )
                    else:
                        file_missing.append(file)

                for file in self.file_opt:
                    if file in request.FILES:
                        kwargs[file] = util.ApiFile( request.FILES[file] )
                    else:
                        kwargs[file] = None

                # If we have a "files" then load it, but skip all listed files
                if self.files is not None:
                    skip = self.file_req + self.file_opt
                    kwargs[self.files] = []

                    # Attempt to keep the order of files
                    file_keys = list(request.FILES.keys())
                    file_keys.sort()
                    for file in file_keys:
                        if file not in skip:
                            kwargs[self.files].append( util.ApiFile( request.FILES[file] ))
            else:
                file_missing = self.file_req

            # Did we miss any constraints?
            if (len(get_missing) + len(post_missing)) + len(sess_missing) + len(file_missing) > 0:
                return monarch.fail( request, 'Missing required argument(s): GET%s POST%s SESS%s FILE%s' % (str(get_missing), str(post_missing), str(sess_missing), str(file_missing)))

            # Does the user want meta data?
            if self.meta is not None:
                kwargs[self.meta] = util.CaterpillarMeta(
                    self.meta,
                    req_args,
                    self.sess_req,
                    self.sess_opt,
                    self.post_req,
                    self.post_opt,
                    self.get_req,
                    self.get_opt,
                    self.file_req,
                    self.file_opt,
                    self.files,
                )

            # Auth check?
            if self.auth is not None:
                # True for check authentication with default system auth
                if isinstance( self.auth, bool ):
                    if self.auth:
                        if not request.user.is_authenticated():
                            return monarch.fail( request, "Not logged in")

                # Custom user authentication, we just just need a true/false
                elif hasattr( self.auth, '__call__'):
                    if not self.auth( *args, **kwargs ):
                        return monarch.fail( request, "Not logged in")

            return func( *args, **kwargs)

        return wrapper
