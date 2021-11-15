# Caterpillar

A light-weight, fast and scalable api solution for Django. Uses a comfy set of functionality that isn't boilerplatey or opinionated.

Don't disregard Caterpillar because its small; It's scrapy to, with built in type conversion, session management, dead simple file handling, self documenting reports and error management. Caterpillar makes writing APIs simple so you can focus on functionality, not CRUD.

# Install Caterpillar

```bash
pip3 install caterpillar-api
```

### Define your API

Inside your django project, create a function with a *@Cocoon* wrapper that defines your paramaters. Add your params to your func.

```python
from caterpillar import Cocoon, pillar

@Cocoon( post_req=(
            ('a', int),
            ('b', int),
))
def add( request, a, b ):
    return pillar.resp( request, { "c": a + b })
```

### Add your endpoint to Django

Inside url.py.

```python
urlpatterns = [
    path('add/', views.add),
    ...
]
```

### Call your API using curl

Now using curl, you can post data to the API, and get a JSON response.

```bash
curl -d "a=17&b=35" -X POST http://127.0.0.1:8000/add/; echo
{"c": 52, "successful": true}
```

# Why Caterpillar?

* Minimum boiler-plate
* Readable syntax
* Crazy fast
* Easy to use
* Unopnionated


# Recipes

## Required POST arguments
post_req takes a tuple of tuples. The tuple entries define variable name, python type. If a parameter is missing from a post_req, Caterpillar will respond with an error before the endpoint is called.


```python
@Cocoon( post_req=(
            ('name', str),
            ('age', int),
))
def add_user( request, name, age ):
    usr = User.objects.create( name=name, age=age )
    return pillar.resp( request, { id: usr.id })
```

## Optional POST arguments
post_opt uses the same format as post_req. Fields can exist or not. If a field isn't present, the default paramater value or None is used.

```python
@Cocoon(
    post_req=(
            ('uid', str),
    ),
    post_opt=(
        ('name', str),
        ('age', int),
        ('type', str, 'ADMIN'),
    )
)
def modify_user( request, uid, name, age, type ):
    usr = User.objects.get(uid=uid)
    if name is not None:
        usr.name = name
    if age is not None:
        usr.age = age
    usr.type = type
    usr.save()
    
    return pillar.resp( request, {})
```

## Optional POST using kwargs
post_opt argument checking works fine, but its a little ugly. It also creates a lot of code. The same operation can be done with kwargs.

```python
@Cocoon(
    post_req=(
            ('uid', str),
    ),
    post_opt=(
            ('name', str),
            ('age', int),
            ('type', str, 'ADMIN'),
    )
)
def modify_user( request, uid, **kwargs ):
    usr = User.objects.get(uid=uid)

    for key in ('name', 'age', 'type'):
        if kwargs[key] is not None:
            usr.__setattr__( key, kwargs[key] )
    usr.save()

    return pillar.resp( request, {})
```

## Meta data
A @Coccon can also provide all the meta data as an argument. This is handy because it can further reduce duplicate logic. Take the above example, using meta data.

```python
@Cocoon(
    post_req=(
            ('uid', str),
    ),
    post_opt=(
            ('name', str),
            ('age', int),
            ('type', str),
    ),
    meta="meta"
)
def modify_user( request, uid, meta, **kwargs ):
    usr = User.objects.get(uid=uid)

    for key, _ in meta.post_opt:
        if kwargs[key] is not None:
            usr.__setattr__( key, kwargs[key] )
    usr.save()

    return pillar.resp( request, {})
```

## Authenticate user and check login status
Caterpillar also helps you work with session information. Session data can be used to authenticate a user and confirm their login state.

```python
from django.forms import model_to_dict

@Cocoon( post_req=(
            ('uid', str),
            ('password', str),
))
def login( request, uid, password ):
    if (usr := getByUid(User, uid)) is None:
        return pillar.err("Couldn't find user")

    if usr.password != password:
        return pillar.err("Invalid password")

    # Store the user's id into the session, this effectively logs the user in
    request.session['usr'] = model_to_dict(usr)
    return pillar.resp( request, {})


@Cocoon(
    sess_req=[('usr', dict)]
)
def logout( request, usr ):
    del request.session['usr']
    return pillar.resp( request, {})


# sess_req['usr'] will only allow this endpoint to be called by users that are logged in
@Cocoon(
    sess_req=[('usr', dict)]
)
def user_details( request, usr ):
    usr = getByUid(User, usr['uid'])
    return pillar.resp( request, model_to_dict(usr))
```

If optional session checking is required, you can always use sess_opt

```python
@Cocoon(
    sess_opt=[('usr', dict)]
)
def is_online( request, usr ):
    return pillar.resp( request, { 'online': usr is not None })
```

## GET data from the URL
The same way POST can have required and optional arguments, GET variables can be accessed through a @Cocoon.

```python
@Cocoon(
    get_req=[('video_code', str)]
)
def get_video( request, usr, video_code ):
    #http://server.com/?video_code=XXX
    print(video_code) # Prints XXX
    return pillar.resp( request, {'video_info': 'info'})
```

## Read a file
Caterpillar seamlessly handles file uploads as parameters. Files, like GET/POST, can be required or optional. The contents of the uploaded file can be read by calling .data(). If a hash of the data is required .hash() will return a sha256 hash.

```python
@Cocoon(
    sess_req=[('usr', dict)],
    file_req=["logo"]
)
def upload_logo( request, usr, logo ):
    if not s3.put_data(logo.data(), usr['uid']):
        return errResponse(request, "Couldn't upload to S3")

    return pillar.resp( request, {})
```

## Need to call an endpoint directly?
Not a problem. Caterpillar will happy to get out of your way. Passing None for the request parameter will tell Caterpillar you are using the functions directly. Instead of a HttpResponse, you'll get the dict of the response.

```python
@Cocoon(
    post_req=(
            ('a', int),
            ('b', int),
    )
)
def add( request, a, b ):
    return pillar.resp( request, { "c": a + b })

add( None, 4, 3) # Returns { "c": 12 }
add( None, "cat", "fish") # Returns { "c": "catfish" } # Type checking isn't done when calling directly
```

# @Cocoon

Cocoon is a function decorator that defines endpoint arguments and data types. 

* **sess_opt** - Optional session parameters. Array/Tuple of tuples. ('name', type) or ('name', type, default)
* **sess_req** - Required session parameters. Array/Tuple of tuples. ('name', type).
* **post_opt** - Optional POST parameters. Array/Tuple of tuples. ('name', type) or ('name', type, default).
* **post_req** - Required POST parameters. Array/Tuple of tuples. ('name', type).
* **get_opt** - Optional GET parameters. Array/Tuple of tuples. ('name', type) or ('name', type, default).
* **get_req** - Required GET parameters. Array/Tuple of tuples. ('name', type).
* **file_opt** - Optional file parameters. Returns the ApiFile object with helper functions data() and hash() Array/Tuple of names. ('name').
* **file_req** - Required file parameters. Returns the ApiFile object with helper functions data() and hash() Array/Tuple of names. ('name').
* **files** - 'name' which recieves an array of Apifile classes. Handy for uploading arrays of unnamed filess.
* **meta** - 'name' which recieves a CaterpillarMeta object. All of the Cocoon parameters are represented along with an 'args' dictionary which holds all data passed to this endpoint.

### @Cocoon Types

* str
* int
* float
* bool - Can take true/false strings or true/false values or ints, 0 !0
* dict - A dictionary of key value pairs. JSON
* list - An array of parameters. Can take a string of delenated elements.

# pillar functions
Pillar functions provide handy success failed responses. If the standard response format isn't flexible enough, you can create your own using util.raw()

```python
from caterpillar import Cocoon, pillar
```

## pillar.resp
A successful response. 'successful' = true is added to the response and then an HttpResponse is generated.

* request - The request variable passed by Django.
* response - A dict key/value pair.

```python
return pillar.resp( request, { 'key': 'value' })
```

## pillar.err
A fail response. 'successful' = false is added to the response and then an HttpResponse is generated.

* request - The request variable passed by Django.
* reason - A string "reason" why the error occurred.
* code="" - An optional error code.
* extra={} - A dict of any other information that should be passed.

## util.raw
util.raw provides HttpResponse logic pillar.resp and pillar.err use to communicate with Django.

* objs - String of response.
* status - Status code
* content - content_type of response
* callback=None - Optional JSON-P support

# JSON-P support?
Yes. Caterpillar provides JSON-P support out of the box by passing a GET variable callback=xxx. If the data is passed as POST or cannot use the name 'callback' to pass the callback name, a custom resp/err function set should be created.

# Common errors
No one likes bugs in their code, but Caterpillar is a bug and sometimes it encounters other bugs.

## TypeError: xxx() got an unexpected keyword argument 'xxx'
Caterpillar works by injecting variables directly into functions. If the variable name doesn't exist in the paramaters of the function, you'll see a TypeError.

```python
@Cocoon( post_req=(
            ('a', int),
            ('b', int),
))
def add( request, a ): # TypeError Missing variable 'b'
    return pillar.resp( request, { "c": a })
```

There are two possible solutions. Add all variables or add **kwargs at the end of your parameters.
```python
# Solution of adding all variables
@Cocoon( post_req=(
            ('a', int),
            ('b', int),
))
def add( request, a, b):
    return pillar.resp( request, { "c": a + b })

# Solution adding **kwargs
@Cocoon( post_req=(
            ('a', int),
            ('b', int),
))
def add( request, a, **kwargs ):
    return pillar.resp( request, { "c": a + kwargs['b'] })
```

### {"successful": false, "reason": "Missing required argument(s): GET[] POST['b'] SESS[] FILE[]", "code": ""}
If a required parameter is missing, the endpoint will not be called. A message similar to the above will be sent instead. Caterpillar attempts to provide detailed information for any GET / POST / SESS / FILE data that is required and missing.

# Testing
...

# Contribute
If you're using Caterpillar and want to help, thank you. There are many ways to get involved.