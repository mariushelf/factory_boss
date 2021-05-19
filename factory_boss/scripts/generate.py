from pprint import pprint

import yaml

from factory_boss.generator import Generator
from factory_boss.parser import SpecParser

if __name__ == "__main__":
    with open("../../examples/simple_schema.yaml", "r") as f:
        schema = yaml.safe_load(f)

    parser = SpecParser()
    parsed_spec = parser.parse(schema)
    pprint(parsed_spec)

    generator = Generator(parsed_spec)
    instances = generator.generate()
    print("INSTANCES")
    print("=========")
    pprint(instances)
    #
    # for entity in entities:
    #     for field in entity.fields:
    #         print(field)
    #
    # print("Generated:")
    # for entity in entities:
    #     print(entity.name)
    #     values = entity.generate()
    #     print(values)
