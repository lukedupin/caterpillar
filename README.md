# Caterpillar

A light-weight, fast and scalable api solution for Django. Uses a comfy set of functionality that isn't boilerplatey or opinionated.

Don't disregard Caterpillar because its small; It's scrapy to, with built in type conversion, session management, dead simple file handling, self documenting reports and error management. Caterpillar makes writing APIs simple so you can focus on functionality, not CRUD.

# Install Caterpillar

```bash
pip3 install caterpillar-api
```

## Define your API

Inside your django project, create a function with a ~@Cocoon~ wrapper that defines your paramaters. Add your params to your func.

```python
from caterpillar import Cocoon, pillar


@Cocoon(
    post_req=(
            ('a', int),
            ('b', int),
    )
)
def add( request, a, b ):
    return pillar.resp( request, { "c": a + b })
```

## Add your endpoint to Django

Inside url.py.

```python
urlpatterns = [
    path('add/', views.add),
    ...
]
```

## Call your API using curl

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
@Cocoon(
    post_req=(
            ('name', str),
            ('age', int),
    )
)
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

@Cocoon(
    post_req=(
            ('uid', str),
            ('password', str),
    ),
)
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

## Need to call and endpoint directly?

# @Cocoon

Cocoon is a function decorator that defines endpoint arguments and data types.


Caterpillar only knows how to GET and POST data. Either data is sent through the URL, or data is sent through the BODY POST. What you do with the data is obviously up to you. 




