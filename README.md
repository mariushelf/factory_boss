# Factory Boss

Fake entire data schemas. Easily.

Original repository: [https://github.com/mariushelf/factory_boss](https://github.com/mariushelf/factory_boss)

# Usage

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


# TODO

Much much, above all documentation:

1. documentation
2. finalize the schema specification
3. support dynamic fields (generate fields via a Python function with other
   fields as input)


# License

MIT -- see [LICENSE](LICENSE)

Author: Marius Helf ([helfsmarius@gmail.com](mailto:helfsmarius@gmail.com))

