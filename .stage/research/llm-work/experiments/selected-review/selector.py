"""같은 모듈의 정적 참조를 따라 원문을 선택합니다. 불확실하면 전체를 돌려줍니다."""

import ast

DYNAMIC_NAMES = {"globals", "locals", "vars", "eval", "exec", "getattr", "setattr", "__import__"}


def loaded_names(node: ast.AST) -> set[str]:
    return {item.id for item in ast.walk(node)
            if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)}


def select_source(source: str, entry: str) -> dict:
    def full(reason: str) -> dict:
        return {"source": source, "mode": "full", "reason": reason, "symbols": []}

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return full("syntax_error")
    definitions = [node for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    functions = {node.name: node for node in definitions}
    if len(functions) != len(definitions):
        return full("duplicate_definition")
    if entry not in functions:
        return full("missing_entry")
    if any(node.decorator_list for node in definitions):
        return full("decorator")
    if loaded_names(tree) & DYNAMIC_NAMES:
        return full("dynamic_lookup")
    retained = [node for node in tree.body if node not in definitions]
    pending = {entry}
    for node in retained:
        pending.update(loaded_names(node) & functions.keys())
    selected: set[str] = set()
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        selected.add(name)
        pending.update((loaded_names(functions[name]) & functions.keys()) - selected)
    if selected == functions.keys():
        return full("all_functions_referenced")
    retained.extend(functions[name] for name in selected)
    lines = source.splitlines(keepends=True)
    chunks = ["".join(lines[node.lineno - 1:node.end_lineno])
              for node in sorted(retained, key=lambda node: node.lineno)]
    narrowed = "\n\n".join(chunk.rstrip("\r\n") for chunk in chunks) + "\n"
    return {"source": narrowed, "mode": "selected", "reason": "static_names",
            "symbols": sorted(selected)}
