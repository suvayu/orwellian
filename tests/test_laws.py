from dataclasses import asdict, dataclass, field

import pytest

from orwellian.laws import Base, OneOf


@dataclass
class choice:
    opt: str = field(default=OneOf(["foo", "bar", "baz"]))


class mystr(str):
    pass


@pytest.mark.parametrize("opt", ["foo", mystr("foo")])
def test_validation_pass(opt):
    data = choice(opt=opt)
    assert data.opt == "foo"


@pytest.mark.parametrize("opt, exc", [("fo", ValueError), (3, TypeError)])
def test_validation_failure(opt, exc):
    with pytest.raises(exc):
        choice(opt=opt)


def test_missing_default():
    with pytest.raises(ValueError, match="'opt': missing value.+"):
        choice()


def test_default():
    @dataclass
    class choice2:
        opt: str = field(default=OneOf("abc", default="a"))

    assert choice2().opt == "a"


def test_nested():
    @dataclass
    class options:
        opta: str = field(default=OneOf("abc", default="a"))
        optb: int = field(default=OneOf([1, 2, 3], default=1))

    @dataclass
    class nested(Base):
        val: int
        opts: options

    inner = {"opta": "c", "optb": 2}
    initialised = nested(val=42, opts=inner)
    assert asdict(initialised.opts) == inner
    assert isinstance(initialised.opts, options)

    with pytest.raises(ValueError):
        inner["opta"] = "d"
        nested(val=42, opts=inner)

    with pytest.raises(TypeError):
        inner["opta"] = 1
        nested(val=42, opts=inner)
