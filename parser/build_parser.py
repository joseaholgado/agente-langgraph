# build_parser.py
from tree_sitter import Language

Language.build_library(
  'build/my-languages.so',  # output
  ['tree_sitter_parsers/tree-sitter-python']  # input
)
