#!/usr/bin/env python3
"""Convert an Obsidian Markdown document set for an Azure DevOps code Wiki."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote, unquote


def page_slug(stem: str) -> str:
    slug = re.sub(r"\s+", "-", stem.strip())
    slug = re.sub(r"[\\/#]", "-", slug)
    return re.sub(r"-+", "-", slug)


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\r?\n.*?\r?\n---\r?\n?", "", text, count=1, flags=re.S)


def local_target(target: str) -> str:
    return unquote(target.split("#", 1)[0].split("?", 1)[0]).strip().strip("<>")


def resolve_doc(target: str, source: Path, pages: dict[str, Path]) -> Path | None:
    path = local_target(target)
    candidate = (source / path).resolve()
    if candidate.suffix.lower() != ".md":
        candidate = candidate.with_suffix(".md")
    for page in pages.values():
        if candidate == page.resolve() or Path(path).stem.casefold() == page.stem.casefold():
            return page
    return None


def link_path(page: Path, source: Path, pages: dict[str, Path], alias: str = "") -> tuple[str, Path | None]:
    target = alias.split("#", 1)[0]
    resolved = resolve_doc(target, source, pages)
    if resolved is None:
        return "", None
    anchor = f"#{alias.split('#', 1)[1]}" if "#" in alias else ""
    return quote(page_slug(resolved.stem) + ".md", safe="-._") + anchor, resolved


def convert_text(text: str, page: Path, source: Path, pages: dict[str, Path], graph: dict[Path, set[Path]], target: str) -> str:
    text = strip_frontmatter(text)

    def obsidian_image(match: re.Match[str]) -> str:
        body = match.group(1)
        target, separator, alt = body.partition("|")
        target = target.strip()
        candidate = (source / target).resolve()
        if not candidate.is_file():
            raise ValueError(f"Missing embedded image: {target} in {page.name}")
        rel = quote(Path(target).as_posix(), safe="/-._")
        return f"![{alt.strip() if separator else Path(target).stem}]({rel})"

    text = re.sub(r"!\[\[([^\]]+)\]\]", obsidian_image, text)

    def obsidian_link(match: re.Match[str]) -> str:
        target, separator, alias = match.group(1).partition("|")
        target = target.strip()
        link, resolved = link_path(page, source, pages, target)
        if resolved:
            graph[page].add(resolved)
            return f"[{alias.strip() if separator else resolved.stem}]({link})"
        return alias.strip() if separator else ""

    text = re.sub(r"(?<!!)\[\[([^\]]+)\]\]", obsidian_link, text)

    def markdown_link(match: re.Match[str]) -> str:
        image, label, raw_target = match.groups()
        target = raw_target.strip().strip("<>")
        if re.match(r"(?i)^(?:https?:|mailto:|tel:|data:)", target) or target.startswith("#"):
            return match.group(0)
        path = local_target(target)
        if Path(path).suffix.lower() == ".md":
            link, resolved = link_path(page, source, pages, path)
            if resolved:
                graph[page].add(resolved)
                return f"{image}[{label}]({link})"
            return label
        if image:
            candidate = (source / path).resolve()
            if not candidate.is_file():
                raise ValueError(f"Missing linked image: {path} in {page.name}")
            return f"![{label}]({quote(Path(path).as_posix(), safe='/-._')})"
        if Path(path).suffix:
            return label
        return match.group(0)

    text = re.sub(r"(!?)\[([^\]]*)\]\((<[^>]+>|[^)]+)\)", markdown_link, text)
    text = re.sub(r"(?m)^> \[!([A-Z]+)\](?:[ \t]+(.*))?$", lambda m: f"> **{m.group(1)}**" + (f" — {m.group(2)}" if m.group(2) else ""), text)
    if target == "azure-devops":
        text = re.sub(r"(?m)(^#{1,6} Table of Contents[ \t]*\n)(?:[ \t]*[-*+].*\n|[ \t]*\n)+", r"\1\n[[_TOC_]]\n", text)
    text = re.sub(r"(?m)^\*\*Related:\*\*[ \t]*\n", "", text)
    text = re.sub(r"(?m)^\*\*Related:\*\*[ \t]*$", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def make_landing(pages: list[Path], page_names: dict[Path, str]) -> str:
    links = "\n".join(f"- [{page.stem}]({quote(page_names[page], safe='-._')}.md)" for page in sorted(pages, key=lambda p: p.stem.casefold()))
    return """# NATS Setup Documentation

This folder contains the Enterprise Event Hub (EEH) NATS/JetStream planning and design documents converted from an Obsidian source set. The original notes remain maintained in Obsidian.

Use the links below to browse the complete set. Each document also links to related pages in this set.

## Document index

""" + links + "\n"


def publish(source: Path, destination: Path, target: str) -> None:
    source = source.resolve()
    markdown = sorted((p for p in source.glob("*.md") if p.name != "AGENTS.md"), key=lambda p: p.name.casefold())
    if not markdown:
        raise ValueError(f"No planning Markdown files found in {source}")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Destination must be empty: {destination}")

    output = destination / "NATS Setup Documentation"
    output.mkdir(parents=True, exist_ok=True)
    pages = {page.stem.casefold(): page for page in markdown}
    names = {page: page_slug(page.stem) for page in markdown}
    graph = {page: set() for page in markdown}
    converted = {page: convert_text(page.read_text(encoding="utf-8"), page, source, pages, graph, target) for page in markdown}

    for page in markdown:
        (output / f"{names[page]}.md").write_text(converted[page], encoding="utf-8")

    landing = "NATS-Setup-Documentation" if target == "azure-devops" else "README"
    (output / f"{landing}.md").write_text(make_landing(markdown, names), encoding="utf-8")
    if target == "azure-devops":
        (output / ".order").write_text("\n".join([landing, *[names[p] for p in markdown]]) + "\n", encoding="utf-8")

    reverse = {page: set() for page in markdown}
    for page, related in graph.items():
        for other in related:
            reverse[other].add(page)
    summary = next((p for p in markdown if p.stem.casefold() == "eeh nats setup overall summary"), None)
    for page in markdown:
        neighbors = (graph[page] | reverse[page]) - {page}
        if summary and page != summary:
            neighbors.add(summary)
        body_path = output / f"{names[page]}.md"
        body = body_path.read_text(encoding="utf-8").rstrip()
        related_lines = [f"- [NATS Setup Documentation]({landing}.md)"]
        related_lines.extend(f"- [{other.stem}]({quote(names[other], safe='-._')}.md)" for other in sorted(neighbors, key=lambda p: p.stem.casefold()))
        body_path.write_text(body + "\n\n## Related planning documents\n\n" + "\n".join(related_lines) + "\n", encoding="utf-8")

    image_dir = source / "images"
    if image_dir.is_dir():
        shutil.copytree(image_dir, output / "images", dirs_exist_ok=True, ignore=shutil.ignore_patterns(".DS_Store"))


def validate(destination: Path, target: str) -> list[str]:
    errors: list[str] = []
    root = destination / "NATS Setup Documentation"
    if not root.is_dir():
        return [f"Missing published folder: {root}"]
    pages = sorted(root.rglob("*.md"))
    if not pages:
        errors.append("No Markdown pages found")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        rel = page.relative_to(root)
        if text.startswith("---\n"):
            errors.append(f"YAML frontmatter remains: {rel}")
        if re.search(r"!?(?<!\\)\[\[(?!_TOC_\]\])[^\]]+\]\]", text):
            errors.append(f"Obsidian wiki link remains: {rel}")
        if re.search(r"(?m)^> \[![A-Z]+\]", text):
            errors.append(f"Obsidian callout remains: {rel}")
        for image, _label, raw_target in re.findall(r"(!?)\[([^\]]*)\]\((<[^>]+>|[^)]+)\)", text):
            link_target = raw_target.strip().strip("<>")
            if re.match(r"(?i)^(?:https?:|mailto:|tel:|data:)", link_target) or link_target.startswith("#"):
                continue
            if image or Path(local_target(link_target)).suffix:
                if not (page.parent / local_target(link_target)).resolve().is_file():
                    errors.append(f"Broken local asset link in {rel}: {link_target}")
            elif Path(local_target(link_target)).suffix.lower() == ".md":
                if not (page.parent / local_target(link_target)).resolve().is_file():
                    errors.append(f"Broken local page link in {rel}: {link_target}")
    landing = "NATS-Setup-Documentation.md" if target == "azure-devops" else "README.md"
    if not (root / landing).is_file():
        errors.append(f"Missing landing page: {landing}")
    if target == "azure-devops":
        order = root / ".order"
        if not order.is_file() or not order.read_text(encoding="utf-8").splitlines() or order.read_text(encoding="utf-8").splitlines()[0] != "NATS-Setup-Documentation":
            errors.append(".order must place NATS-Setup-Documentation first")
    for page in (p for p in pages if p.name != landing):
        if "## Related planning documents" not in page.read_text(encoding="utf-8"):
            errors.append(f"Missing generated related-document links: {page.relative_to(root)}")
        if target == "github" and "[[_TOC_]]" in page.read_text(encoding="utf-8"):
            errors.append(f"Azure DevOps TOC directive remains in GitHub output: {page.relative_to(root)}")
    return errors


class PublishSelfTest(unittest.TestCase):
    def test_publish_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "source"
            source.mkdir()
            (source / "images").mkdir()
            (source / "images" / "a b.png").write_bytes(b"image")
            (source / "One.md").write_text("---\ntitle: One\n---\n# One\n\n## Table of Contents\n\n- [Two](#two)\n\n## Two\n\n[[Two|two]]\n\n![[images/a b.png]]\n\n[[Outside Note]]\n\n> [!NOTE] Keep this\n", encoding="utf-8")
            (source / "Two.md").write_text("# Two\n", encoding="utf-8")
            destination = base / "output"
            publish(source, destination, "azure-devops")
            one = (destination / "NATS Setup Documentation" / "One.md").read_text(encoding="utf-8")
            self.assertNotIn("title: One", one)
            self.assertIn("[two](Two.md)", one)
            self.assertIn("[[_TOC_]]", one)
            self.assertNotIn("](#two)", one)
            self.assertIn("![a b](images/a%20b.png)", one)
            self.assertNotIn("[[Outside Note]]", one)
            self.assertIn("> **NOTE** — Keep this", one)
            self.assertTrue((destination / "NATS Setup Documentation" / "images" / "a b.png").is_file())
            self.assertEqual(validate(destination, "azure-devops"), [])

            github_destination = base / "github-output"
            publish(source, github_destination, "github")
            github_root = github_destination / "NATS Setup Documentation"
            github_one = (github_root / "One.md").read_text(encoding="utf-8")
            self.assertIn("- [Two](#two)", github_one)
            self.assertNotIn("[[_TOC_]]", github_one)
            self.assertTrue((github_root / "README.md").is_file())
            self.assertFalse((github_root / ".order").exists())
            self.assertEqual(validate(github_destination, "github"), [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--target", choices=("azure-devops", "github"), default="azure-devops")
    parser.add_argument("--check", type=Path, help="validate an existing published directory")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PublishSelfTest))
        return 0 if result.wasSuccessful() else 1
    if args.check:
        errors = validate(args.check, args.target)
        print("\n".join(errors) if errors else "Validation passed")
        return 1 if errors else 0
    if not args.source or not args.destination:
        parser.error("--source and --destination are required unless --check or --self-test is used")
    publish(args.source, args.destination, args.target)
    errors = validate(args.destination, args.target)
    if errors:
        print("\n".join(errors))
        return 1
    print("Published documents and validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
