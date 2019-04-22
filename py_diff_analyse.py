import sys

from unidiff import PatchSet

if __name__ == '__main__':
    filepath = sys.argv[1]

    patch_info = [
        # в файле changed_file_path.py изменены строки 33-36 и 40-46 (после применения дифа)
        # ('changed_file_path.py', [(33, 36), (40, 46)]),
    ]

    patch = PatchSet.from_filename(filepath, encoding='utf-8')
    for patched_file in patch:
        file_changes_info = (patched_file.path, [])
        for changed_file_part_info in patched_file:
            file_changes_info[1].append(
                (
                    changed_file_part_info.target_start,
                    changed_file_part_info.target_start + changed_file_part_info.target_length,
                ),
            )
        patch_info.append(file_changes_info)
    print(patch_info)
