# Factory Boss

Fake entire data schemas. Easily.

Original repository:
[https://github.com/mariushelf/factory_boss](https://github.com/mariushelf/factory_boss)

# Use case

Factory Boss can help you whenever you need to mock data schemas, for example when
you cannot work or develop with the original data for privacy, GDPR related issues
and security concerns.

# Features

Factory Boss can mock entire data schemas, including relationships and dependencies
between features and objects.

Schema specifications are read from a simple yaml format.
The generated output is a list of dictionaries for each mocked entity, which can
easily be written to a database, converted to pandas DataFrames etc.


# Installation

This package is available on PyPI and can be installed with `pip install factory_boss`.


# Usage

Mocking a data schema consists of two steps:

1. Specify the schema.
2. Generate data.


## Specify a schema

Schemas are specified in yaml, including relationships between entities and mock
rules.

See [simple_schema.yaml](examples/simple_schema.yaml) for an example.


## Generate mock data


```python
from pprint import pprint
import yaml
from factory_boss.generator import Generator
from factory_boss.spec_parser.parser import SpecParser

with open("examples/simple_schema.yaml", "r") as f:
    schema = yaml.safe_load(f)

parser = SpecParser()
parsed_spec = parser.parse(schema)

generator = Generator(parsed_spec)
instances = generator.generate()
print("INSTANCES")
print("=========")
pprint(instances)
```

See [factory_boss/scripts/generate.py](factory_boss/scripts/generate.py) for
the full script.


# Roadmap

Many much, above all documentation.

Here are biggest "milestones":

1. documentation
2. finalize the schema specification
3. support dynamic fields (generate fields via a Python function with other
   fields as input)

In the [issues section](https://github.com/mariushelf/factory_boss/issues)
there are some more tickets.


# Contributing

I'm more than happy to accept help in the form of bug reports, feature requests,
or pull requests, even though there is no formal "contribution guideline" yet.

If you want to help just reach out to me :)


# Acknowledgements

This work wouldn't be possible without the amazing
[faker](https://github.com/joke2k/faker) package.

Factory Boss is also heavily inspired by
[factory_boy](https://github.com/FactoryBoy/factory_boy),
but has a different focus. While factory_boy excels at generating single objects
and test fixtures, Factory Boss aims at faking entire data schemas. In that sense
it offers both a subset and a superset of factory_boy's features.


# License

MIT -- see [LICENSE](LICENSE)

Author: Marius Helf ([helfsmarius@gmail.com](mailto:helfsmarius@gmail.com))
