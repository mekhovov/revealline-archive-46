#!/usr/bin/env python3
"""Configure the dedicated archive-46 inventory from v0.80.1's original metadata."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "v0.80.1"
SOURCE = "b810521a53af7be145acb8dedce0a01a747339cf"
TREE = "237dd46da3c0b98261997c13bc3a8fb5faac6bd0"
TAG = "9649852a5555b34687cbe5c9556952c0346bc55c"
ZIP = "e9193a3e3087f72c013a2ba75dc5f55315a3a2fa7c047a762a8f7dc7adf67c2c"
ZIP_BYTES = 423417713
TOOLING = "1222454049ea411b29c8822f77283f2109cafbd3"
EXTRACTOR = "38081b1791b49cb7328d18b4d4325c2876bb3bc8d7db03f4610f8d8a7c4bf91b"

def sha(data): return hashlib.sha256(data).hexdigest()
def json_bytes(value): return (json.dumps(value, indent=2) + "\n").encode()

def main():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import verify
    metadata = ROOT / "metadata" / VERSION
    record = json.loads((metadata / "release.json").read_bytes())
    manifest = json.loads((metadata / "manifest.json").read_bytes())
    checksum = (metadata / "distribution.zip.sha256").read_bytes()
    qualification = metadata / "source-qualification.json"
    assert record["version"] == manifest["version"] == VERSION
    assert record["sourceRevision"] == manifest["sourceRevision"] == SOURCE
    assert record["distributionSha256"] == ZIP == checksum.decode().split()[0]
    release = {
        "version": VERSION, "sourceRevision": SOURCE, "sourceTree": TREE, "tagObject": TAG,
        "distributionSha256": ZIP, "distributionBytes": ZIP_BYTES,
        "metadata": {name: sha((metadata / name).read_bytes()) for name in ("release.json", "manifest.json", "distribution.zip.sha256")},
        "sourceQualification": {"bytes": qualification.stat().st_size, "sha256": sha(qualification.read_bytes())},
    }
    lock = {
        "format": "revealline-archive-originals.v2", "archiveId": "archive-46", "repository": "mekhovov/revealline-archive-46",
        "sourceRepository": "mekhovov/revealline", "toolingCommit": TOOLING,
        "extractorPath": "publishing/pages-controller/extract-current.py", "extractorSha256": EXTRACTOR,
        "budgetBytes": 800000000, "releases": [release],
    }
    (ROOT / "source-lock.json").write_bytes(json_bytes(lock))
    rows = verify.metadata_inventory(ROOT, release)
    rows.extend([
        {"path": ".nojekyll", "bytes": 0, "sha256": sha(b"")},
        {"path": "index.html", "bytes": (ROOT / "index.html").stat().st_size, "sha256": sha((ROOT / "index.html").read_bytes())},
        {"path": "releases/index.html", "bytes": (ROOT / "releases/index.html").stat().st_size, "sha256": sha((ROOT / "releases/index.html").read_bytes())},
    ])
    rows.sort(key=lambda row: row["path"])
    inventory = {"base": "https://mekhovov.github.io/revealline-archive-46/", "files": rows}
    inventory_bytes = json_bytes(inventory)
    (ROOT / "expected-inventory.json").write_bytes(inventory_bytes)
    lock.update({"expectedInventorySha256": sha(inventory_bytes), "expectedFiles": len(rows), "expectedBytes": sum(row["bytes"] for row in rows)})
    (ROOT / "source-lock.json").write_bytes(json_bytes(lock))
    (ROOT / "input-authority.json").write_bytes(json_bytes({
        "version": VERSION, "releaseId": 393336400, "source": SOURCE, "tree": TREE, "tagObject": TAG,
        "donorCommit": TOOLING, "donorDeploymentMerge": None, "priorAcceptedPaths": 0,
        "mainPublisherRun": 35664144678, "archivePublicAcceptance": False,
    }))

if __name__ == "__main__": main()
