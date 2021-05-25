# Factory Boss

Fake entire data schemas. Easily.

Original repository: [https://github.com/mariushelf/factory_boss](https://github.com/mariushelf/factory_boss)

# Generation Process

```mermaid
graph TB
    YAML -- load --> Dict --> P
    ES[Entity and Value specifications]
    P(SpecParser) -- generates --> ES
    ES -- "make_instances()" --> Instances
    IR[Instances with Relations]
    Instances --> make_relations("make_relations()")
    make_relations --> IR
    make_relations -- can result in --> NI[New Instances]
    NI --> make_relations
    IR --> |"resolve_references()"|DAG[DAG / 'Plan']
    DAG -->|"execute_plan()"| IV[Instances with Values]
    IV -->|"to_dict()"| DICT[Output Dictionary]
```

## Entity Specification
```mermaid
classDiagram
Entity *-- Field : contains
FakerField --|> Field
Constant --|> Field
DynamicField --|> Field
DynamicField ..> Field : references
```

# TODO

Much much, above all documentation.


# License

MIT -- see [LICENSE](LICENSE)

Author: Marius Helf ([helfsmarius@gmail.com](mailto:helfsmarius@gmail.com))

