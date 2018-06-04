import pytest
import magicattr


class Test:
    l = [1, 2]
    a = [0, [1, 2, [3,4]]]
    b = {'x': {'y': 'y'}, 'z': [1, 2]}
    z = 'z'


class Person:
    settings = {
        'autosave': True,
        'style': {
            'height': 30,
            'width': 200
        },
        'themes': ['light', 'dark']
    }
    def __init__(self, name, age, friends):
        self.name = name
        self.age = age
        self.friends = friends


@pytest.mark.parametrize('key, value', [
    ('l', Test.l),
    ('t.t.t.t.z', 'z'),
    ('a[0]', 0),
    ('a[1][0]', 1),
    ('a[1][2]', [3,4]),
    ('b["x"]', {'y': 'y'}),
    ('b["x"]["y"]', 'y'),
    ('b["z"]', [1,2]),
    ('b["z"][1]', 2),
    ('b["w"].z', 'z'),
    ('b["w"].t.l', [1, 2]),
    ('a[-1].z', 'z'),
    ('l[-1]', 2),
    ('a[2].t.a[-1].z', 'z'),
    ('a[2].t.b["z"][0]', 1),
    ('a[-1].t.z', 'z')
])
def test_magicattr_get(key, value):
    obj = Test()
    # Create some circular circular references
    obj.t = obj
    obj.a.append(obj)
    obj.b['w'] = obj

    assert magicattr.get(obj, key) == value


def test_person_example():
    bob = Person(name="Bob", age=31, friends=[])
    jill = Person(name="Jill", age=29, friends=[bob])
    jack = Person(name="Jack", age=28, friends=[bob, jill])

    # Nothing new
    assert magicattr.get(bob, 'age') == 31

    # Lists
    assert magicattr.get(jill, 'friends[0].name') == 'Bob'
    assert magicattr.get(jack, 'friends[-1].age') == 29

    # Dict lookups
    assert magicattr.get(jack, 'settings["style"]["width"]') == 200

    # Combination of lookups
    assert magicattr.get(jack, 'settings["themes"][-2]') == 'light'
    assert magicattr.get(jack, 'friends[-1].settings["themes"][1]') == 'dark'

    # Setattr
    magicattr.set(bob, 'settings["style"]["width"]', 400)
    assert magicattr.get(bob, 'settings["style"]["width"]') == 400

    # Nested objects
    magicattr.set(bob, 'friends', [jack, jill])
    assert magicattr.get(jack, 'friends[0].friends[0]') == jack

    magicattr.set(jill, 'friends[0].age', 32)
    assert bob.age == 32

    # Deletion
    magicattr.delete(jill, 'friends[0]')
    assert len(jill.friends) == 0

    magicattr.delete(jill, 'age')
    assert not hasattr(jill, 'age')

    magicattr.delete(bob, 'friends[0].age')
    assert not hasattr(jack, 'age')

    # Unsupported
    with pytest.raises(NotImplementedError) as e:
        magicattr.get(bob, 'friends[0+1]')

    # Nice try, function calls are not allowed
    with pytest.raises(ValueError):
        magicattr.get(bob, 'friends.pop(0)')

    # Must be an expression
    with pytest.raises(ValueError):
        magicattr.get(bob, 'friends = []')

    # Must be an expression
    with pytest.raises(SyntaxError):
        magicattr.get(bob, 'friends..')

    # Must be an expression
    with pytest.raises(KeyError):
        magicattr.get(bob, 'settings["DoesNotExist"]')

    # Must be an expression
    with pytest.raises(IndexError):
        magicattr.get(bob, 'friends[100]')
