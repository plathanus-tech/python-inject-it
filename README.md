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

## Conditional arguments to Provider

Sometimes you will want to create a service dinamically, using some attributes for the current context of your application. For example, on a HTTP view passing the current user to the provider, the state of a object on the database. `inject-it` allows you to give this parameters to the provider on the fly using `additional_kwargs_to_provider` context manager. That will apply `functools.partial` into your provider for the given kwargs. Example:

First, let's define the provider like usual:

```python
# client.py
from inject_it import provider


class Client:
    def __init__(self, key):
        self.key


@provider
def client_provider(api_key: str) -> Client:
    return Client(key=api_key)
```

Notice that if we don't inject the `api_key` argument, `inject_it` won't be able to call the `client_provider` function, since it will be missing the `api_key` parameter. To solve this let's continue the example:

```python
# services.py
from client import Client
from inject_it import requires


@requires(Client)
def make_request(client: Client):
    print(client.key)
```

So let's say you use the api_key for each user. And you receive an HTTP request into your view. Using django views, migth look like this:

```python
# views.py
from client import Client
from services import make_request
from inject_it import additional_kwargs_to_provider


def some_view(request):
    user = request.user

    with additional_kwargs_to_provider(Client, api_key=user.some_service_key):
        make_request()  # client will be injected for the given user.some_service_key

    ...
```

Two things is happening when you call the `additional_kwargs_to_provider` function:
1- You will be patch the `Client` provider function to receive the kwargs you given.
2- The kwargs must match the `client_provider` arguments.

This helps if you are using some design patterns like the Strategy Pattern, swapping a service implementation for your current application state.

## Depending on abstract classes

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

When one defines a `provider` this provider function requires to be imported so that inject-it is aware of this provider. Usually, you can do this on your application entrypoint, a `main.py` file for example. However, it may feel weird importing a module only for registering purposes, and your IDE will tell you that you imported a module, but never used it. For example:

```python
# main.py
from your_application import providers  # <- Imported, but unused in this scope

def main():
    print("Do stuff")
    ...

main()
```

`inject-it` allows you to register your providers in a more fashion way. It's similar to what's Django does with applications.

## Register Providers Modules

Since importing a provider file in runtime just for registering may feel ackward, as mentioned above, `inject-it` exposes a `register_provider_modules` function that one can use to register all its providers on a single call. Using the same example from above, it will look like:

```python
from inject_it import register_provider_modules

def main():
    print("Do stuff")
    ...

register_provider_modules(
    "your_application.providers",
    "your_application.another_module.my_providers",
)
main()
```

`register_provider_modules` any number of providers modules, it will look for any function decorated with `provider` in those modules. If no provider is found an exception is raised.

## Limitations

For the moment, you can only have one dependency for each type. So you can't have like two different `str` dependencies. When you register the second `str` you will be overriding the first. You can work around this by using specific types, instead of primitive types.
In the moment, you can't use functions as dependencies.

## Testing

Testing is made easy with `inject-it`, you just have to register your `mock`, `fake`, `stub` before calling your function. If you are using pytest, use fixtures.
