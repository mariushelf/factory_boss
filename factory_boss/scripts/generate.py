from pprint import pprint

import yaml

from factory_boss.generator import Generator
from factory_boss.spec_parser.parser import SpecParser


def main():
    with open("examples/simple_schema.yaml", "r") as f:
        schema = yaml.safe_load(f)
    parser = SpecParser()
    parsed_spec = parser.parse(schema)
    generator = Generator(parsed_spec)
    instances = generator.generate(output_with_related_objects=False)
    print("INSTANCES")
    print("=========")
    pprint(instances)


if __name__ == "__main__":
    main()
