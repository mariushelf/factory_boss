""" Work in progress for a proper grammar for dynamic field specifications.

Not in use yet."""

value_grammar = r"""
start : expression
expression : (reference | literal)+
reference.10 : "$" _reference_body
          | "${" _WS* _reference_body _WS* "}"
_reference_body : ref_element ("." ref_element)*
ref_element.10 : element_name [element_access]
element_name.10 : CNAME
element_access.10 :  "[" _WS* _element_accessor _WS* "]"
_element_accessor : slice | index
slice : [[SIGNED_INT ":"] SIGNED_INT] ":" [SIGNED_INT]
index : SIGNED_INT

literal.-1: (/[^$\\]+/ | _escape DOLLAR | _escaped_backslash )+
DOLLAR: "$"
_escape : _BACKSLASH
_escaped_backslash : _BACKSLASH BACKSLASH
BACKSLASH : "\\"
_BACKSLASH : "\\"

_WS: WS

%import common.WS
%import common.NUMBER
%import common.SIGNED_NUMBER
%import common.INT
%import common.SIGNED_INT
%import common.CNAME
"""

if __name__ == "__main__":
    from lark import Lark

    parser = Lark(value_grammar, parser="earley")

    code = r"$a[-56: ].b${ this.is.a.ref}fgds gfd $FIRST.x[1] \$test \\$test2 \\\$test3 \\\\$test4"
    print(parser.parse(code))
    print(parser.parse(code).pretty())
