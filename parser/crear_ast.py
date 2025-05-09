from tree_sitter import Language, Parser
import json

class GenerarAST:
    def __init__(self, file_path):
        LIB_PATH = 'build/my-languages.so'
        PY_LANGUAGE = Language(LIB_PATH, 'python')
        parser = Parser()
        parser.set_language(PY_LANGUAGE)

        # Lee el archivo de ejemplo
        with open(file_path, 'rb') as f:
            source_code = f.read()

        # Parseo del código fuente
        tree = parser.parse(source_code)
        root_node = tree.root_node

        # Extrae definiciones de funciones
        def extract_functions(node, source):
            funcs = []
            for child in node.children:
                if child.type == "function_definition":
                    name_node = child.child_by_field_name("name")
                    params_node = child.child_by_field_name("parameters")
                    block_node = child.child_by_field_name("body")

                    docstring = None
                    first_stmt = block_node.children[0] if block_node.children else None
                    if first_stmt and first_stmt.type == "expression_statement":
                        expr = first_stmt.child_by_field_name("expression")
                        if expr and expr.type == "string":
                            docstring = source[expr.start_byte:expr.end_byte].decode('utf-8')

                    funcs.append({
                        "name": source[name_node.start_byte:name_node.end_byte].decode('utf-8'),
                        "params": source[params_node.start_byte:params_node.end_byte].decode('utf-8'),
                        "docstring": docstring,
                        "calls": extract_calls(block_node, source)
                    })
            return funcs

        # Extrae llamadas a funciones dentro de un bloque
        def extract_calls(node, source):
            calls = []

            def visit(n):
                if n.type == "call":
                    func_node = n.child_by_field_name("function")
                    if func_node:
                        name = source[func_node.start_byte:func_node.end_byte].decode('utf-8')
                        calls.append(name)
                for child in n.children:
                    visit(child)

            visit(node)
            return calls

        # Extrae variables
        def extract_variables(node, source):
            vars = []
            for child in node.children:
                if child.type == "assignment":
                    var_node = child.child_by_field_name("left")
                    if var_node:
                        var_name = source[var_node.start_byte:var_node.end_byte].decode('utf-8')
                        vars.append(var_name)
                for sub_child in child.children:
                    vars.extend(extract_variables(sub_child, source))
            return vars

        # Extrae comentarios
        def extract_comments(node, source):
            comments = []
            for child in node.children:
                if child.type == "comment":
                    comment = source[child.start_byte:child.end_byte].decode('utf-8')
                    comments.append(comment)
                comments.extend(extract_comments(child, source))
            return comments

        # Extrae clases
        def extract_classes(node, source):
            classes = []
            for child in node.children:
                if child.type == "class_definition":
                    class_name_node = child.child_by_field_name("name")
                    if class_name_node:
                        class_name = source[class_name_node.start_byte:class_name_node.end_byte].decode('utf-8')
                        methods = extract_functions(child, source)
                        classes.append({
                            "name": class_name,
                            "methods": methods
                        })
                for sub_child in child.children:
                    classes.extend(extract_classes(sub_child, source))
            return classes


        # Resumen final
        summary = {
            "functions": extract_functions(root_node, source_code),
            "variables": extract_variables(root_node, source_code),
            "comments": extract_comments(root_node, source_code),
            "classes": extract_classes(root_node, source_code)
        }

        # Escribe a JSON
        with open("../ast_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print("✅ AST simplificado exportado a 'ast_summary.json'")
