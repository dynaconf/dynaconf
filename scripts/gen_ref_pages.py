"""Generate the code reference pages and navigation.

From the mkdocstrings recipe: https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages
"""
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

# The template for this script made the assumption that the package files lived in
# a src/ folder, so some of the paths here needed to change.
root = Path(__file__).parent.parent
src = Path(__file__).parent.parent / "dynaconf"

for path in sorted(src.rglob("*.py")):
    # We get the paths relative to the project root, rather than the src.
    module_path = path.relative_to(root).with_suffix("")
    doc_path = path.relative_to(root).with_suffix(".md")
    # Needed to make sure the path here is relative to this file because
    # mkdocs_gen_files defaulted to creating things in the temp folder for some reason.
    # Caused git errors because files were outside the repo.
    full_doc_path = Path(root, "docs", "reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

    # Followed the advice in the note in this section of the mkdocstrings recipe:
    # https://mkdocstrings.github.io/recipes/#generate-pages-on-the-fly
    # Not doing this resulted in a 404 error.
    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

# Similar comment to above, needed to make sure the path was relative.
with mkdocs_gen_files.open(Path(root, "docs", "reference/SUMMARY.md"), "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
