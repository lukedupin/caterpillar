""" Our tests are defined in here """

from caterpillar_api import Cocoon, monarch, util


class TestReq:
    def __init__(self, session={}, get=None, post=None ):
        self.session = session
        self.GET = get if get is not None else {}
        self.POST = post if post is not None else {}

        self.method = 'POST' if post is not None else 'GET'


def test_base():
    assert util.xstr(None) == ""
    assert util.xstr("Test") == "Test"

    assert util.xint(None) == 0
    assert util.xint("8lkajsdf") == 8
    assert util.xint(27) == 27
    assert util.xint("undefined") == None

    assert util.xfloat(None) == 0.0
    assert util.xfloat("8lkajsdf") == 8
    assert util.xfloat("8.17lkajsdf") == 8.17
    assert util.xfloat(27) == 27
    assert util.xfloat(27.2) == 27.2
    assert util.xfloat("undefined") == None

    assert not util.xbool(None)
    assert util.xbool("tRue")
    assert not util.xbool("falSe")
    assert util.xbool(True)


def test_get_opt():
    @Cocoon(
        get_opt=[
            ('test', int),
            ('test2', int)
        ]
    )
    def testy( request, test, test2, **kwargs ):
        assert test == 8
        assert test2 == None

    testy( TestReq(get={'test': 8}) )


def test_post_req():
    @Cocoon(
        post_req=[
            ('test', int),
            ('test2', float)
        ]
    )
    def testy( request, test, test2, **kwargs ):
        assert test == 8
        assert test2 == 9.17

    testy( TestReq(post={'test': "8asdfdfd", "test2": 9.17}) )
