"""Offline checks for the guides: code blocks are valid, JSON parses, every
relative link and anchor resolves, and the request examples obey the documented
Seedance 2.5 limits.

    pip install pytest
    pytest
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.M | re.S)
LINK = re.compile(r"\]\((\./[^)\s]+|docs/[^)\s]+|#[^)\s]+)\)")


def blocks(language):
    for page in PAGES:
        for index, match in enumerate(FENCE.finditer(page.read_text())):
            if match.group(1) == language:
                yield pytest.param(match.group(2), id=f"{page.name}-{index}")


def slug(heading):
    heading = re.sub(r"[`*]", "", heading.strip().lower())
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", heading))


def anchors(page):
    prose = FENCE.sub("", page.read_text())  # comment lines inside code blocks are not headings
    return {slug(line.lstrip("#")) for line in prose.splitlines() if line.startswith("#")}


@pytest.mark.parametrize("code", blocks("python"))
def test_python_blocks_compile(code):
    compile(code, "<guide>", "exec")


@pytest.mark.parametrize("code", blocks("bash"))
def test_bash_blocks_parse(code):
    result = subprocess.run(["bash", "-n"], input=code, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("code", blocks("json"))
def test_json_blocks_parse(code):
    json.loads(code)


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_relative_links_resolve(page):
    for target in LINK.findall(page.read_text()):
        path, _, anchor = target.partition("#")
        file = (page.parent / path).resolve() if path else page
        assert file.exists(), f"{page.name}: {target} points nowhere"
        if anchor and file.suffix == ".md":
            assert anchor in anchors(file), f"{page.name}: no heading for #{anchor} in {file.name}"


def request_examples():
    for code in (param.values[0] for param in blocks("json")):
        body = json.loads(code)
        if body.get("model") == "seedance-2.5" and "prompt" in body:
            yield body


@pytest.mark.parametrize("body", list(request_examples()), ids=lambda b: b["prompt"][:30])
def test_request_examples_follow_the_documented_limits(body):
    edit = body.get("omni_reference_task_type") == "edit"
    frames = "start_image" in body or "end_image" in body
    references = [body.get(name, []) for name in ("reference_images", "reference_videos", "reference_audios")]
    if edit:
        assert "duration" not in body and "aspect_ratio" not in body
        assert len(body["reference_videos"]) == 1 and not frames
    else:
        assert 4 <= body.get("duration", 5) <= 30
    assert body.get("resolution", "720p") in ("480p", "720p", "1080p")
    if frames:
        assert body.get("aspect_ratio", "adaptive") == "adaptive"
        assert not any(references), "frames cannot be combined with references"
    assert len(references[0]) <= 30 and len(references[1]) <= 10 and len(references[2]) <= 10
    assert "seed" not in body


def test_there_is_a_guide_per_endpoint():
    assert {page.name for page in PAGES} >= {
        "media-uploads.md", "video-generations.md", "video-status.md", "video-content.md",
    }

