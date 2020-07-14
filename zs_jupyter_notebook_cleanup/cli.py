import argparse
import copy
import difflib
import json
import os
import shutil
import sys
import tempfile
import uuid
from collections import OrderedDict


def parse_args():
    psr = argparse.ArgumentParser()
    psr.add_argument("files", nargs="*", help="ipynb files")
    psr.add_argument("--diff", action="store_true", default=False, 
        help="Show modification difference")
    psr.add_argument("--inplace", "--in-place", action="store_true", default=False, 
        help="Save changes inplace in ipynb files.")
    psr.add_argument("--pin-patterns", default="[pin]", 
        help="Semicolon-separated patterns (wildcards are not supported)")
    psr.add_argument("--exit-zero", action="store_true", default=False,
        help="Exit with status code \"0\" even if there are errors.")
    psr.add_argument("--remove-kernel-metadata", action="store_true", default=False,
        help="Remove blocks with kernel metadata.")
    psr.add_argument("--remove-execution-count", action="store_true", default=False,
        help="Remove blocks with execution count.")
    psr.add_argument("--remove-outputs", action="store_true", default=False,
        help="Remove blocks with output.")
    psr.add_argument("--remove-cell-metadata-all", action="store_true", default=False,
        help="Remove blocks with cell metadata, clear all metadata.")
    psr.add_argument("--remove-cell-metadata-patterns", nargs="+", default="", 
        help="Semicolon-separated patterns (wildcards are not supported)")
    psr.add_argument("--remove-empty-cell", action="store_true", default=False,
        help="Remove empty cells.")
    psr.add_argument("--remove-spaces-cell", action="store_true", default=False,
        help="Remove cells which contain only spaces/tabs/newlines.")

    args = psr.parse_args()
    #args.remove_cell_metadata_patterns = args.remove_cell_metadata_patterns.split(";")

    return args


def main():
    diff_files_count = 0
    args = parse_args()
    patterns = args.pin_patterns.split(";")
    for path in args.files:
        diff_files_count += remove_output_file(path, patterns=patterns, args=args)
    if diff_files_count != 0 and not args.exit_zero:
        sys.exit(1)
    return sys.exit(0)

def check_if_unremovable(source, patterns):
    """comment annotation must be the first line and started with #"""
    for s in source:
        ss = s.strip()
        if ss.startswith("#") and any(x in ss for x in patterns):
            return True
    return False


def remove_output_file(path, patterns, args):
    """Base function to modify files"""
    dump_args = {"ensure_ascii": False, "separators": (",", ": "), "indent": 1}
    # to preserve timestamps, making temporal copy
    with tempfile.TemporaryDirectory() as tdir:
        tpath = os.path.join(tdir, "jupyter-notebook-cleanup-" + str(uuid.uuid1()))
        shutil.copy2(path, tpath)
        with open(path, "rt", encoding="utf8") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
        new_data = remove_output_object(data, patterns, args)
        before_j = json.dumps(data, **dump_args)
        after_j = json.dumps(new_data, **dump_args)
        if before_j != after_j:
            if args.diff:
                before_l, after_l = before_j.splitlines(), after_j.splitlines()
                print("\n".join(difflib.unified_diff(before_l, after_l, fromfile="before", tofile="after")))
            if args.inplace: # overwrite to the original file
                with open(path, "wt", encoding="utf-8") as fo:
                    json.dump(new_data, fo, **dump_args)
                    fo.write("\n")
            shutil.copystat(tpath, path)  # copy original timestamps
            return 1
    return 0


def remove_output_object(data, patterns, args):
    new_data = copy.deepcopy(data)
    if args.remove_kernel_metadata:
        kernelspec = new_data.get("metadata", {}).get("kernelspec", {})
        if "display_name" in kernelspec:
            kernelspec["display_name"] = ""
        if "name" in kernelspec:
            kernelspec["name"] = ""

    new_cells = []
    for cell in list(new_data["cells"]):
        if args.remove_empty_cell:
            if len(cell["source"]) == 0:
                continue

        if args.remove_spaces_cell:
            is_spaces_cell = True
            for x in cell["source"]:
                if x.strip() != "":
                    is_spaces_cell = False
                    break
            if is_spaces_cell:
                continue

        if "execution_count" in cell:
            if args.remove_execution_count:
                cell["execution_count"] = None

        if "metadata" in cell:
            if args.remove_cell_metadata_all:
                cell["metadata"] = {}
            else:
                for pat in args.remove_cell_metadata_patterns:
                    if pat in cell["metadata"]:
                        del cell["metadata"][pat]

        if "outputs" in cell and "source" in cell:
            source = cell["source"]
            if not isinstance(source, list):
                pass
            if not check_if_unremovable(source, patterns):
                if args.remove_outputs:
                    cell["outputs"] = []

        new_cells.append(cell)
    new_data["cells"] = new_cells
    return new_data


if __name__ == "__main__":
    main()
