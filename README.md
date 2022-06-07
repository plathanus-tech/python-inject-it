# Inject-It

Simple dependency injection facility using python decorators.
`inject_it` aims to:

- Keep dependencies creation separated from usage;
- Keep dependencies swappable for test environments;

## How to use

You can inject dependencies in two main ways:

1- Creating it first, in a main.py like style;
2- Using a function to create the dependency.

### Creating the dependency first aproach

Say you have a dependency for a object of type `SomeService`. Then before you start your application, you create a instance
of this object and want to inject it to a function. So you can have:

```python
# service.py
class SomeService:
    # Your service stuff
    def do_stuff(self):
        print("Doing stuff")


# main.py
from service import SomeService
from inject_it import register_dependency

service = SomeService()
register_dependency(service)
# More code later...
```

The code above will register the type of `service` and bound this to the `service` instance.
So in another file that requires `SomeService` we will use the `requires` decorator, like:

```python
# worker.py
from service import SomeService
from inject_it import requires

@requires(SomeService)
def your_function(some_argument: str, another_argument: int, s: SomeService):
    s.do_stuff()

# main.py
from service import SomeService
from inject_it import register_dependency

service = SomeService()
register_dependency(service)

from worker import your_function
your_function("abc", another_argument=1)
```

By using the `reguires` decorator on `your_function` passing `SomeService` as a dependency, inject_it will inject the `service` instance
into the function for you.

## How injection works

`inject_it` `requires` decorator instropects the signature of the decorated function to inject the dependencies. So it does some checks to see if the decorated function is correctly annotated. We also check if you also not given the dependency that will be injected, so we dont override for some reason your call.

## The requires decorator

The `requires` decorator also accepts more than one dependency for function. So you can do:

```python

from inject_it import requires


@requires(str, int, float)
def totally_injected_function(a: int, b: str, c: float):
    pass

# In this case you can call the function like this
totally_injected_function()
```

The code above works, but in the snippet above for simplicity we didn't called `register_dependency`, so this snippet as is will raise an `inject_it.exceptions.DependencyNotRegistered`.

## Creating the dependency on a provider function

You can also define a dependency `provider`. That is a function that will return the dependency object. This is useful if you need a different instance everytime. Using the same example from before:

```python
# main.py
from service import SomeService
from inject_it import provider


@provider(SomeService)
def some_service_provider():
    # On a real example,on this approach you probably would load some env-variables, config, etc.
    return SomeService()

```

In this example, everytime a function `requires` for `SomeService` this function will be called. If it's expensive to create the object, you can cache it. You do it like:

```python
# main.py
from service import SomeService
from inject_it import provider


@provider(SomeService, cache_dependency=True)  # <-
def some_service_provider():
    # On a real example,on this approach you probably would load some env-variables, config, etc.
    return SomeService()

```

This will have the same effect as calling `register_dependency` after creating the object.

Your provider can also `requires` a dependency, but it must be registered before it.

# Depending on abstract classes

`inject-it` allows you to `register_dependency` to another `bound_type`. This is useful if you don't really care about the concrete implementation, only the abstract one.
Consider this example:

```python
# main .py
from inject_it import register_dependency

class AbcService:
    def do_work(self):
        print("Working")


class ConcreteService:
    def do_work(self):
        print("I'm really working")


service = ConcreteService()
register_dependency(service, bound_type=AbcService)


# other_file.py
from main import AbcService
from inject_it import requires


@requires(AbcService)
def your_function(s: AbcService):
    print(s)


# Calling this function will return:
your_function()
"I'm really working"
```

The same is true for the `provider` decorator. You can pass to it the abstract class and return from it the concrete one.
Using the same classes from the above example, consider:

```python
from inject_it import provider
from main import AbcService, ConcreteService


@provider(AbcService)
def provider_func():
    return ConcreteService()

```

## Limitations

For the moment, you can only have one dependency for each type. So you can't have like two different `str` dependencies. When you register the second `str` you will be overriding the first. You can work around this by using specific types, instead of primitive types.

# Testing

Testing is made easy with `inject-it`, you just have to register your `mock`, `fake`, `stub` before calling your function. If you are using pytest, use fixtures.
