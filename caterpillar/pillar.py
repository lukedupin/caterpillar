from caterpillar import util

import json


# Json response
def resp( request, objs={} ):
    objs['successful'] = True

    # If we have no request, then just return the objects
    if request is None:
        return objs

    callback = request.GET['callback'] if 'callback' in request.GET else None
    return util.raw( json.dumps( objs ), status=200, content='application/json', callback=callback )


# Return an error response
def err( request, reason, code="", extra={} ):
    print( reason )

    objs = { 'successful': False, 'reason': reason, 'code': code }
    objs.update( extra )

    # If we have no request, then just return the objects
    if request is None:
        return objs

    callback = request.GET['callback'] if 'callback' in request.GET else None
    return util.raw( json.dumps( objs ), status=201, content='application/json', callback=callback )