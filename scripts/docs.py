import os
import shutil
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import mkdocs.commands.build
import mkdocs.commands.serve
import mkdocs.config
import mkdocs.utils
import typer
import yaml

app = typer.Typer()

mkdocs_name = "mkdocs.yml"

docs_path = Path("docs")

en_docs_path = Path("docs/en")

en_config_path: Path = en_docs_path / mkdocs_name

missing_translation_snippet = """
<div style="border-color: #bea925;border: 0.05rem solid #bea925;border-radius: 0.2rem;
box-shadow: 0 0.2rem 0.5rem rgba(0,0,0,.2),0 0 0.05rem rgba(0,0,0,.1);display: flow-root;font-size: .64rem;
margin: 1.5625em 0; padding: 0 0.6rem;page-break-inside: avoid;"> 
<p style="background-color: #be6725;color: #be2525"> <span style="color: #be2525">&#9888;</span> Warning </p>
<p>The current page still doesn't have a translation for this language.</p>
<p> But you can help translating it: <a href="https://github.com/dynaconf/dynaconf/blob/9f91e0dc1c96c9dcbc2feca6bd29f898a157b9a9/CONTRIBUTING.md" target="_blank">Contributing</a></p>
</div>
"""


def get_en_config() -> dict:
    return mkdocs.utils.yaml_load(en_config_path.read_text(encoding="utf-8"))


def get_lang_paths():
    return sorted(docs_path.iterdir())


def lang_callback(lang: Optional[str]):
    if lang is None:
        return

    if not lang.isalpha() or len(lang) > 5:
        typer.echo("Use a 2 or 5 letter language code, like: es, pt_BR")
        raise typer.Abort()
    return lang


def complete_existing_lang(incomplete: str):
    lang_path: Path
    for lang_path in get_lang_paths():
        if lang_path.is_dir() and lang_path.name.startswith(incomplete):
            yield lang_path.name


def get_base_lang_config(lang: str):
    en_config = get_en_config()
    dynaconf_url_base = "https://dynaconf.com/"
    new_config = en_config.copy()
    new_config["site_url"] = en_config["site_url"] + f"{lang}/"
    new_config["theme"]["logo"] = dynaconf_url_base + en_config["theme"]["logo"]
    new_config["theme"]["favicon"] = dynaconf_url_base + en_config["theme"]["favicon"]
    new_config["theme"]["language"] = lang if len(lang) == 2 else ''.join([k for k in "pt_BR"][:2])
    new_config["theme"]["locale"] = lang
    new_config["nav"] = en_config["nav"][:2]

    return new_config


@app.command()
def new_lang(lang: str = typer.Argument(..., callback=lang_callback)):
    """
    Generate a new docs translation directory for the language LANG.
    LANG should be a 2 or 5 letter language code, like: en, es, de, pt, pt_BR, etc.
    """
    new_path: Path = Path("docs") / lang
    if new_path.exists():
        typer.echo(f"The language was already created: {lang}")
        raise typer.Abort()
    new_path.mkdir()
    new_config = get_base_lang_config(lang)
    new_config_path: Path = Path(new_path) / mkdocs_name
    new_config_path.write_text(
        yaml.dump(new_config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )
    new_config_docs_path: Path = new_path / "docs"
    new_config_docs_path.mkdir()
    en_index_path: Path = en_docs_path / "docs" / "index.md"
    new_index_path: Path = new_config_docs_path / "index.md"
    en_index_content = en_index_path.read_text(encoding="utf-8")
    new_index_content = f"{missing_translation_snippet}\n\n{en_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    shutil.copytree(en_docs_path / "docs" / "img", new_config_docs_path / "img")
    new_overrides_gitignore_path = new_path / "overrides" / ".gitignore"
    new_overrides_gitignore_path.parent.mkdir(parents=True, exist_ok=True)
    new_overrides_gitignore_path.write_text("")
    typer.secho(f"Successfully initialized: {new_path}", color=typer.colors.GREEN)
    update_languages(lang=None)


def _remove_and_copytree(build_lang_path, language_path):
    shutil.rmtree(build_lang_path, ignore_errors=True)
    shutil.copytree(language_path, build_lang_path)


def _build_paths(language: str) -> Tuple[Path, Path, Path, Path]:
    lang_path: Path = Path("docs") / language
    if not lang_path.is_dir():
        typer.echo(f"The language translation doesn't seem to exist yet: {language}")
        raise typer.Abort()
    typer.echo(f"Building docs for: {language}")
    build_dir_path = Path("docs_build")
    build_dir_path.mkdir(exist_ok=True)
    build_lang_path = build_dir_path / language
    en_lang_path = Path("docs/en")
    site_path = Path("site").absolute()
    if language == "en":
        dist_path = site_path
    else:
        dist_path: Path = site_path / language

    return build_lang_path, en_lang_path, dist_path, lang_path


def _generate_language_nav():
    pass


def _update_new_lang_nav(key_to_section: Dict[Tuple, List]) -> List[Dict[str, Any]]:
    new_nav = []
    for i in key_to_section[()]:
        for k, v in i.items():
            if type(v) is list and len(v) == 1:
                new_nav.append({k: v[0]})
            elif type(v) is list and len(v) > 1:
                new_nav.append({k: v})
            elif type(v) is str:
                new_nav.append({k: v})

    return new_nav


def _generate_key__to_section(
        file_to_nav: Dict[str, Tuple[str, ...]],
        use_lang_file_to_nav: Dict[str, Tuple[str, ...]]) -> Dict[Tuple, List]:
    key_to_section = {(): []}

    for file, orig_file_key in file_to_nav.items():
        if file in use_lang_file_to_nav:
            file_key = use_lang_file_to_nav[file]
        else:
            file_key = orig_file_key
        section = get_key_section(key_to_section=key_to_section, key=file_key)
        section.append(file)

    return key_to_section


def _update_use_lang_file_to_nav(language_nav: List,
                                 file_to_nav: Dict[str, Tuple[str, ...]],
                                 build_lang_path: Path,
                                 en_lang_path: Path) -> Dict[str, Tuple[str, ...]]:
    use_lang_file_to_nav = get_file_to_nav_map(language_nav[2:])

    for file in file_to_nav:
        file_path = Path(file)
        lang_file_path: Path = build_lang_path / "docs" / file_path
        en_file_path: Path = en_lang_path / "docs" / file_path
        lang_file_path.parent.mkdir(parents=True, exist_ok=True)
        if not lang_file_path.is_file():
            en_text = en_file_path.read_text(encoding="utf-8")
            lang_text = get_text_with_translate_missing(en_text)
            lang_file_path.write_text(lang_text, encoding="utf-8")
            file_key = file_to_nav[file]
            use_lang_file_to_nav[file] = file_key

    return use_lang_file_to_nav


def _save_new_lang_nav(lang_config, lang_nav, nav, new_nav, build_lang_path):
    export_lang_nav = [lang_nav[0], nav[1]] + new_nav
    lang_config["nav"] = export_lang_nav
    build_lang_config_path: Path = build_lang_path / mkdocs_name
    build_lang_config_path.write_text(
        yaml.dump(lang_config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


def _load_lang_nav_and_en_nav(en_lang_path: Path, lang_path: Path) -> Tuple:
    en_lang_config_path: Path = en_lang_path / mkdocs_name
    en_config: dict = mkdocs.utils.yaml_load(en_lang_config_path.read_text(encoding="utf-8"))
    nav = en_config["nav"]
    lang_config_path: Path = lang_path / mkdocs_name
    lang_config: dict = mkdocs.utils.yaml_load(
        lang_config_path.read_text(encoding="utf-8")
    )

    return nav, lang_config


@app.command()
def build_lang(
        lang: str = typer.Argument(
            ..., callback=lang_callback, autocompletion=complete_existing_lang
        )
):
    """
    Build the docs for a language, filling missing pages with translation notifications.
    """
    build_lang_path, en_lang_path, dist_path, lang_path = _build_paths(language=lang)

    _remove_and_copytree(build_lang_path, lang_path)

    nav, lang_config = _load_lang_nav_and_en_nav(en_lang_path=en_lang_path, lang_path=lang_path)

    lang_nav = lang_config["nav"]

    file_to_nav = get_file_to_navigate_to_as_map(nav[2:])

    use_lang_file_to_nav = _update_use_lang_file_to_nav(
        language_nav=lang_nav,
        file_to_nav=file_to_nav,
        build_lang_path=build_lang_path,
        en_lang_path=en_lang_path)

    key_to_section = _generate_key__to_section(file_to_nav=file_to_nav, use_lang_file_to_nav=use_lang_file_to_nav)

    new_nav = _update_new_lang_nav(key_to_section=key_to_section)

    _save_new_lang_nav(lang_config=lang_config, lang_nav=lang_nav, nav=nav, new_nav=new_nav,
                       build_lang_path=build_lang_path)

    current_dir = os.getcwd()
    os.chdir(build_lang_path)
    subprocess.run(["mkdocs", "build", "--site-dir", dist_path, "--clean"], check=True)
    os.chdir(current_dir)
    typer.secho(f"Successfully built docs for: {lang}", color=typer.colors.GREEN)


@app.command()
def build_all():
    """
    Build mkdocs site for en, and then build each language inside, end result is located
    at directory ./site/ with each language inside.
    """
    site_path = Path("site").absolute()
    update_languages(lang=None)
    current_dir = os.getcwd()
    os.chdir(en_docs_path)
    typer.echo("Building docs for: en")
    subprocess.run(["mkdocs", "build", "--site-dir", site_path], check=True)
    os.chdir(current_dir)
    langs = []
    for lang in get_lang_paths():
        if lang == en_docs_path or not lang.is_dir():
            continue
        langs.append(lang.name)
    cpu_count = os.cpu_count() or 1
    with Pool(cpu_count * 2) as p:
        p.map(build_lang, langs)


def update_single_lang(lang: str):
    lang_path = docs_path / lang
    typer.echo(f"Updating {lang_path.name}")
    update_config(lang_path.name)


@app.command()
def update_languages(
        lang: str = typer.Argument(
            None, callback=lang_callback, autocompletion=complete_existing_lang
        )
):
    """
    Update the mkdocs.yml file Languages section including all the available languages.
    The LANG argument is a 2-letter language code. If it's not provided, update all the
    mkdocs.yml files (for all the languages).
    """
    if lang is None:
        for lang_path in get_lang_paths():
            if lang_path.is_dir():
                update_single_lang(lang_path.name)
    else:
        update_single_lang(lang)


@app.command()
def serve():
    """
    A quick server to preview a built site with translations.
    For development, prefer the command live (or just mkdocs serve).
    This is here only to preview a site with translations already built.
    Make sure you run the build-all command first.
    """
    typer.echo("Warning: this is a very simple server.")
    typer.echo("For development, use the command live instead.")
    typer.echo("This is here only to preview a site with translations already built.")
    typer.echo("Make sure you run the build-all command first.")
    os.chdir("site")
    server_address = ("", 8008)
    server = HTTPServer(server_address, SimpleHTTPRequestHandler)
    typer.echo(f"Serving at: http://127.0.0.1:8008")
    server.serve_forever()


@app.command()
def live(
        lang: str = typer.Argument(
            None, callback=lang_callback, autocompletion=complete_existing_lang
        )
):
    """
    Serve with livereload a docs site for a specific language.
    This only shows the actual translated files, not the placeholders created with
    build-all.
    Takes an optional LANG argument with the name of the language to serve, by default
    en.
    """
    if lang is None:
        lang = "en"
    lang_path: Path = docs_path / lang
    os.chdir(lang_path)
    mkdocs.commands.serve.serve(dev_addr="127.0.0.1:8008")


def update_config(lang: str):
    lang_path: Path = docs_path / lang
    config_path = lang_path / mkdocs_name
    current_config: dict = mkdocs.utils.yaml_load(
        config_path.read_text(encoding="utf-8")
    )
    if lang == "en":
        config = get_en_config()
    else:
        config = get_base_lang_config(lang)
        config["nav"] = current_config["nav"]
        config["theme"]["language"] = current_config["theme"]["language"]
    languages = [{"en": "/"}]
    alternate: List[Dict[str, str]] = config["extra"].get("alternate", [])
    alternate_dict = {alt["link"]: alt["name"] for alt in alternate}
    new_alternate: List[Dict[str, str]] = []
    for lang_path in get_lang_paths():
        if lang_path.name == "en" or not lang_path.is_dir():
            continue
        name = lang_path.name
        languages.append({name: f"/{name}/"})
    for lang_dict in languages:
        name = list(lang_dict.keys())[0]
        url = lang_dict[name]
        if url not in alternate_dict:
            new_alternate.append({"link": url, "name": name})
        else:
            use_name = alternate_dict[url]
            new_alternate.append({"link": url, "name": use_name})
    config["nav"][1] = {"Languages": languages}
    config["extra"]["alternate"] = new_alternate
    config_path.write_text(
        yaml.dump(config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


def get_key_section(
        *, key_to_section: Dict[Tuple[str, ...], list], key: Tuple[str, ...]
) -> list:
    if key in key_to_section:
        return key_to_section[key]
    super_key = key[:-1]
    title = key[-1]
    super_section = get_key_section(key_to_section=key_to_section, key=super_key)
    new_section = []
    super_section.append({title: new_section})
    key_to_section[key] = new_section
    return new_section


def get_text_with_translate_missing(text: str) -> str:
    lines = text.splitlines()
    lines.insert(1, missing_translation_snippet)
    new_text = "\n".join(lines)
    return new_text


def get_file_to_nav_map(nav: list) -> Dict[str, Tuple[str, ...]]:
    file_to_nav = {}
    for item in nav:
        if type(item) is str:
            file_to_nav[item] = tuple()
        elif type(item) is dict:
            item_key = list(item.keys())[0]
            sub_nav = item[item_key]
            sub_file_to_nav = get_file_to_nav_map(sub_nav)
            for k, v in sub_file_to_nav.items():
                file_to_nav[k] = (item_key,) + v
    return file_to_nav


def get_file_to_navigate_to_as_map(nav: list) -> Dict[str, Tuple[str, ...]]:
    file_to_nav = {}

    for i in nav:
        for k, v in i.items():
            file_to_nav[v] = (k,)

    return file_to_nav


def get_sections(nav: list) -> Dict[Tuple[str, ...], str]:
    sections = {}

    for i in nav:
        for k, v in i.items():
            sections[v] = (k,)

    # for item in nav:
    #     if type(item) is str:
    #         continue
    #     elif type(item) is dict:
    #         item_key = list(item.keys())[0]
    #         sub_nav = item[item_key]
    #         sections[(item_key,)] = sub_nav[0]
    #         sub_sections = get_sections(sub_nav)
    #         for k, v in sub_sections.items():
    #             new_key = (item_key,) + k
    #             sections[new_key] = v
    return sections


if __name__ == "__main__":
    app()
