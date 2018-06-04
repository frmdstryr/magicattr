# Magicattr

[![Build Status](https://travis-ci.org/frmdstryr/magicattr.svg?branch=master)](https://travis-ci.org/frmdstryr/magicattr)
[![codecov](https://codecov.io/gh/frmdstryr/magicattr/branch/master/graph/badge.svg)](https://codecov.io/gh/frmdstryr/magicattr)


A getattr and setattr that works on nested objects, lists, 
dictionaries, and any combination thereof without resorting to eval.


### Example

Say we have a person class as follows:

```python


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


bob = Person(name="Bob", age=31, friends=[])
jill = Person(name="Jill", age=29, friends=[bob])
jack = Person(name="Jack", age=28, friends=[bob, jill])

```

With magicattr we can do this

```python

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
```

You can also delete like this too.

```python

# Deletion
magicattr.delete(jill, 'friends[0]')
assert len(jill.friends) == 0

magicattr.delete(jill, 'age')
assert not hasattr(jill, 'age')

magicattr.delete(bob, 'friends[0].age')
assert not hasattr(jack, 'age')

```

What if someone tries to mess with you?

```python

# Unsupported
with pytest.raises(NotImplementedError) as e:
    assert magicattr.get(bob, 'friends[0+1]') == jill

# Nice try, function calls are not allowed
with pytest.raises(ValueError):
    assert magicattr.get(bob, 'friends.pop(0)') == bob.friends.pop

```

Did I miss anything? Let me know!



#### What it can't do?

Slicing, expressions, function calls, append/pop from lists, eval stuff, etc...


#### How does it work?

Parses the attr string into an ast node and manually evaluates it.
  

### Installing

`pip install magicattr`


### License

MIT

Hope it helps, cheers!