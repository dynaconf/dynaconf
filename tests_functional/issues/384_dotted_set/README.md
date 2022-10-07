# Issue

NoamGraetz2 commented on Aug 6
you cannot set a deeper entry with the same key as higher entry.

```py
settings.set('a.b', 1)
settings.set('a.c', 2)
settings.set('a.c.k', 22)

--> {'c': {'k': 22}, 'b': 1}

settings.set('a.c.b', 3)

--> {'c': {'b': 3, 'k': 22}}
```

the higher entry 'a.b' was removed

the problem lie within _dotted_set and the use of 'tail' and merge

tries to find a quick solution, but i a don't have the time now, will bypass by using different keys :(


## comments

I figured out the problem now and it is a real bug.

We are passing tail to object_merge as a keyname and it is wrong, we should change that to accumulate the whole path.

for a.b.c instead of passing tail=c we really need to recursively accumulate it and compare whole path a on first call, a.b on second, a.b.c on the tail call.

Also we should invert the order that dicts are merged on object_merge and instead of taking the new as the definitive object use the old which will keep all existing keys.


## Think Box


If I have a setting:

settings.FOO = {
  "a": {
    "b": {"a": 1}
  }
}

The full path for the value `1` is: `foo.a.b.a`

settings.get('foo.a.b.a')

If I want to include a new value `b` under b can I do:

settings.set('foo.a.b.b', 2)

in order to have

settings.FOO = {
  "a": {
    "b": {"a": 1, "b": 2},
  }
}

or even

settings.set('foo.a.b', "reset") to have

settings.FOO = {
  "a": {
    "b": "reset"
  }
}


## How to merge dictionaries?

### Contributing:

takes existing called `old`

{"a": {"b": {"a": 1}}}

takes `new`

{"a": {"b": {"b": 2}}}

For each key, value in `old`
