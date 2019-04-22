import ast
import os
import sys
from typing import List, Tuple, Optional

from unidiff import PatchSet


PatchInfo = List[Tuple[str, List[Tuple[int, int]]]]
PyFileInfo = List[Tuple[str, ast.AST]]


def extract_patch_info_from(
        diff_filepath: str,
        project_path: str,
        allowed_files_extensions: List[str],
) -> PatchInfo:
    patch_info = [
        # в файле changed_file_path.py изменены строки 33-36 и 40-46 (после применения дифа)
        # ('changed_file_path.py', [(33, 36), (40, 46)]),
    ]

    patch = PatchSet.from_filename(diff_filepath, encoding='utf-8')
    for patched_file in patch:
        if os.path.splitext(patched_file.path)[1] not in allowed_files_extensions:
            continue

        file_changes_info = (
            os.path.join(project_path, patched_file.path),
            [],
        )
        for changed_file_part_info in patched_file:
            file_changes_info[1].append(
                (
                    changed_file_part_info.target_start,
                    changed_file_part_info.target_start + changed_file_part_info.target_length,
                ),
            )
        patch_info.append(file_changes_info)
    return patch_info


def parse_changed_files(changed_files: List[str], project_path: str) -> PyFileInfo:
    trees_info = []
    for file_name in changed_files:
        full_path = os.path.join(project_path, file_name)
        with open(full_path, 'r') as file_handler:
            file_content = file_handler.read()
        tree = ast.parse(file_content, filename=full_path)
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        trees_info.append(
            (full_path, tree),
        )
    return trees_info


def extract_changed_python_objects_info(patch_info: PatchInfo, ast_trees_info: PyFileInfo) -> List[str]:
    changed_python_objects: List[str] = []
    path_to_ast_tree_map = dict(ast_trees_info)
    for filepath, changed_file_part_info in patch_info:
        ast_tree = path_to_ast_tree_map[filepath]
        for line_from, line_to in changed_file_part_info:
            target_node = get_any_node_at_line(line_from, ast_tree)
            def_node = get_closet_meaning_parent(target_node)
            if target_node is None or def_node is None:
                continue
            changed_python_objects.append(get_repr_for_node(def_node))
    return list(set(changed_python_objects))


def get_any_node_at_line(line: int, ast_tree: ast.AST) -> Optional[ast.AST]:
    for node in ast.walk(ast_tree):
        if hasattr(node, 'lineno') and node.lineno == line:
            return node


def get_closet_meaning_parent(target_node: ast.AST) -> Optional[ast.AST]:
    result_node = None
    while result_node is None:
        if not hasattr(target_node, 'parent'):
            return None
        target_node = target_node.parent
        if isinstance(target_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return target_node


def get_repr_for_node(node: ast.AST) -> str:
    if isinstance(node, ast.FunctionDef):
        parent_node = get_closet_meaning_parent(node)
        if parent_node is not None:
            return '{0}.{1}'.format(
                get_repr_for_node(parent_node),
                node.name,
            )
        return node.name
    if isinstance(node, ast.ClassDef):
        return node.name
    return str(node)


if __name__ == '__main__':
    diff_filepath = sys.argv[1]
    project_path = '/Users/ilebedev/projects/python-unidiff/'

    patch_info = extract_patch_info_from(diff_filepath, project_path, allowed_files_extensions=['.py'])
    changed_files = [c[0] for c in patch_info]
    print('patch_info', patch_info)

    ast_trees_info = parse_changed_files(changed_files, project_path)
    print('ast_trees_info', ast_trees_info)

    changed_python_objects_pathes = extract_changed_python_objects_info(patch_info, ast_trees_info)
    print('changed_python_objects_pathes', changed_python_objects_pathes)
