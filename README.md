# Factory Boss

Fake entire data schemas. Easily.

Original repository: [https://github.com/mariushelf/factory_boss](https://github.com/mariushelf/factory_boss)

# Generation Process

```mermaid
flowchart TB
    P(Parser) -- generates --> ES[Entity specification]
    ES --> FR(Field Resolver)
    FR --> DG(DAGGenerator)
    DG --> IG(Instance Generator)
    IG -- produces --> I[Instance]
    
    G -.->|uses|R(Resolver)
    R -.->|knows|Context
    Context -.->|contains|C[Constants]
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

## Instances

An instance is represented as a dictionary from field name to value.

# License

MIT -- see [LICENSE](LICENSE)

Author: Marius Helf ([helfsmarius@gmail.com](mailto:helfsmarius@gmail.com))

