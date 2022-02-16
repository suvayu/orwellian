from dataclasses import dataclass, field

import pytest

from orwellian.laws import OneOf


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
