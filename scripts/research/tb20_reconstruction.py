#!/usr/bin/env python3
"""Reproduce the E1' and EE-08 measurements from public Terminal-Bench 2.0 artifacts.

This is a read-only research script, not part of the Eval Evidence package or its
distribution. It executes no models and writes nothing outside its output directory.

It answers two preregistered questions (docs/research/CLAIM_RECONSTRUCTION.md section G):

  EE-08  Can a published leaderboard row be reconstructed from the published per-task
         breakdown, and is the exclusion predicate uniquely recoverable?
  E1'    In genuine Harbor job records, does the expected attempt count agree with the
         discovered one, and how often are retries used?

Sources (all public, no credentials):
  - tbench.ai leaderboard rows and per-row detail payloads
  - HuggingFace dataset harborframework/terminal-bench-2-leaderboard (submission folders,
    job-level config.json / result.json / lock.json, trial directory listings)

Usage:
  python3 scripts/research/tb20_reconstruction.py --out /tmp/tb20 [--stage all]

Stages are resumable; fetched artifacts are cached under --out and re-used.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HF_API = "https://huggingface.co/api/datasets/harborframework/terminal-bench-2-leaderboard/tree/main/"
HF_RAW = "https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard/raw/main/"
SUBMISSIONS = "submissions/terminal-bench/2.0"
BOARD = "https://www.tbench.ai/leaderboard/terminal-bench/2.0"
UA = {"User-Agent": "eval-evidence research (claim reconstruction study)"}
TASK_RE = re.compile(r'\\"data\\":\[(\{\\"taskName\\".*?)\]', re.S)


def fetch(url: str, tries: int = 3, timeout: int = 90) -> bytes:
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=timeout
            ).read()
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 404) or attempt == tries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def tree(path: str) -> list[dict]:
    """List a HuggingFace dataset path, following Link rel=next pagination."""
    url = HF_API + path
    out: list[dict] = []
    while url:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as resp:
            out.extend(json.load(resp))
            link = resp.headers.get("Link", "")
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = match.group(1) if match else None
    return out


def stage_rows(out: pathlib.Path) -> list[dict]:
    """Leaderboard row objects, from the board's embedded payload."""
    cache = out / "rows.json"
    if cache.exists():
        return json.loads(cache.read_text())
    html = fetch(BOARD).decode("utf-8", "replace")
    blobs = re.findall(r'\{\\"agent\\":.*?\\"key\\":\\"[^"]*?\\"\}', html, re.S)
    rows = []
    for blob in blobs:
        try:
            rows.append(json.loads(blob.replace('\\"', '"').replace("\\\\", "\\")))
        except json.JSONDecodeError:
            continue
    dedup = {(r["agentName"], str(r["agentVersion"]), tuple(r["modelNames"])): r for r in rows}
    rows = list(dedup.values())
    cache.write_text(json.dumps(rows, indent=1))
    return rows


def row_url(row: dict) -> str:
    models = ",".join(f"{n}@{p}" for n, p in zip(row["modelNames"], row["modelProviders"]))
    quote = lambda s: urllib.parse.quote(str(s), safe="")
    return f"{BOARD}/{quote(row['agentName'])}/{quote(row['agentVersion'])}/{quote(models)}"


def ident(row: dict) -> str:
    return f"{row['agentName']}__{row['agentVersion']}__{row['key']}".replace("/", "_")


def stage_details(out: pathlib.Path, rows: list[dict]) -> None:
    """Per-row per-task breakdown (nTrials, successCount, taskChecksum)."""
    dest = out / "details"
    dest.mkdir(exist_ok=True)
    for row in rows:
        target = dest / (ident(row) + ".json")
        if target.exists():
            continue
        html = fetch(row_url(row)).decode("utf-8", "replace")
        match = TASK_RE.search(html)
        if not match:
            print(f"  no payload: {ident(row)}", file=sys.stderr)
            continue
        tasks = json.loads(("[" + match.group(1) + "]").replace('\\"', '"').replace("\\\\", "\\"))
        target.write_text(json.dumps({"ident": ident(row), "row": row, "tasks": tasks}))
        time.sleep(0.35)


def stage_jobs(out: pathlib.Path) -> dict:
    """Job-level config/result/lock plus trial-directory counts per submission folder."""
    cache = out / "jobs_index.json"
    index = json.loads(cache.read_text()) if cache.exists() else {}
    jobs_dir = out / "jobs"
    jobs_dir.mkdir(exist_ok=True)
    folders = [e["path"] for e in tree(SUBMISSIONS) if e["type"] == "directory"]
    for i, folder_path in enumerate(folders, 1):
        name = folder_path.split("/")[-1]
        if name in index:
            continue
        entry = {"path": folder_path, "jobs": []}
        for job_path in [k["path"] for k in tree(folder_path) if k["type"] == "directory"]:
            job = job_path.split("/")[-1]
            local = jobs_dir / name
            local.mkdir(exist_ok=True)
            rec = {"job": job, "path": job_path}
            for fn in ("result.json", "config.json", "lock.json"):
                target = local / f"{job}__{fn}"
                marker = local / f"{job}__{fn}.absent"
                if target.exists():
                    rec[fn] = True
                    continue
                if marker.exists():
                    rec[fn] = False
                    continue
                try:
                    target.write_bytes(fetch(HF_RAW + job_path + "/" + fn))
                    rec[fn] = True
                except Exception:
                    marker.write_text("")
                    rec[fn] = False
            rec["trial_directories"] = sum(
                1 for x in tree(job_path) if x["type"] == "directory"
            )
            entry["jobs"].append(rec)
        index[name] = entry
        if i % 10 == 0:
            cache.write_text(json.dumps(index, indent=1))
            print(f"  folders {i}/{len(folders)}", file=sys.stderr)
    cache.write_text(json.dumps(index, indent=1))
    return index


def analyse(out: pathlib.Path) -> dict:
    details = [json.loads(p.read_text()) for p in sorted((out / "details").glob("*.json"))]
    index = json.loads((out / "jobs_index.json").read_text())

    # --- EE-08: reconstruct each displayed row from its published per-task breakdown
    row_rows = []
    for d in details:
        row, tasks = d["row"], d["tasks"]
        n_tasks = len(tasks)
        counted = sum(t["nTrials"] for t in tasks)
        successes = sum(t["successCount"] for t in tasks)
        rates = [t["successCount"] / t["nTrials"] for t in tasks if t["nTrials"]]
        per_task_mean = sum(rates) / n_tasks if n_tasks and len(rates) == n_tasks else None
        singletons = [t for t in tasks if t["nTrials"] < 2]
        stderr = None
        if not singletons and n_tasks:
            var = sum(
                (t["successCount"] / t["nTrials"]) * (1 - t["successCount"] / t["nTrials"]) / (t["nTrials"] - 1)
                for t in tasks
            )
            stderr = math.sqrt(var) / n_tasks
        row_rows.append(
            dict(
                ident=d["ident"], agent=row["agentName"], version=row["agentVersion"], key=row["key"],
                displayed_accuracy=row["accuracy"], displayed_stderr=row["stderr"],
                tasks=n_tasks, counted_trials=counted, successes=successes,
                recomputed_accuracy=per_task_mean, recomputed_stderr=stderr,
                pooled_accuracy=successes / counted if counted else None,
                tasks_with_lt2_trials=len(singletons),
            )
        )

    def near(a, b, tol):
        return a is not None and b is not None and abs(a - b) <= tol

    acc_ok = sum(near(r["recomputed_accuracy"], r["displayed_accuracy"], 1e-12) for r in row_rows)
    pooled_ok = sum(near(r["pooled_accuracy"], r["displayed_accuracy"], 1e-9) for r in row_rows)
    with_se = [r for r in row_rows if r["displayed_stderr"] is not None]
    se_ok = sum(near(r["recomputed_stderr"], r["displayed_stderr"], 1e-9) for r in with_se)
    null_se = [r for r in row_rows if r["displayed_stderr"] is None]

    checksums = collections.defaultdict(set)
    for d in details:
        for t in d["tasks"]:
            checksums[t["taskName"]].add(t["taskChecksum"])
    keys = collections.Counter(d["row"]["key"] for d in details)

    # --- E1': expected vs discovered per genuine Harbor job
    job_rows = []
    for folder, info in index.items():
        for job in info["jobs"]:
            path = out / "jobs" / folder / f"{job['job']}__result.json"
            rec = dict(folder=folder, job=job["job"], trial_directories=job.get("trial_directories"))
            if not path.exists():
                rec.update(unreadable=True)
                job_rows.append(rec)
                continue
            try:
                result = json.loads(path.read_text())
            except json.JSONDecodeError:
                rec.update(unreadable=True)
                job_rows.append(rec)
                continue
            stats = result.get("stats") or {}
            named = set()
            for ev in (stats.get("evals") or {}).values():
                for by_value in (ev.get("reward_stats") or {}).values():
                    for names in by_value.values():
                        named.update(names)
                for names in (ev.get("exception_stats") or {}).values():
                    named.update(names)
            rec.update(
                unreadable=False, n_total_trials=result.get("n_total_trials"), named_in_stats=len(named),
                pending=stats.get("n_pending_trials", 0), running=stats.get("n_running_trials", 0),
                n_retries=stats.get("n_retries", 0), n_errored=stats.get("n_errored_trials", 0),
                started_at=result.get("started_at"),
            )
            job_rows.append(rec)

    stated = [r for r in job_rows if not r.get("unreadable") and r.get("n_total_trials") is not None]
    disagree = [r for r in stated if r["n_total_trials"] != r["trial_directories"]]
    retried = [r for r in job_rows if (r.get("n_retries") or 0) > 0]

    return dict(
        ee08=dict(
            rows=len(row_rows),
            accuracy_reproduced_per_task_mean=acc_ok,
            accuracy_reproduced_pooled=pooled_ok,
            rows_with_displayed_stderr=len(with_se),
            stderr_reproduced=se_ok,
            rows_without_stderr=len(null_se),
            rows_without_stderr_having_a_task_under_2_trials=sum(1 for r in null_se if r["tasks_with_lt2_trials"]),
            distinct_task_names=len(checksums),
            tasks_with_more_than_one_checksum=sum(1 for v in checksums.values() if len(v) > 1),
            distinct_row_keys=len(keys),
            colliding_row_keys=[k for k, v in keys.items() if v > 1],
        ),
        e1=dict(
            jobs=len(job_rows),
            jobs_unreadable=sum(1 for r in job_rows if r.get("unreadable")),
            jobs_without_n_total=sum(1 for r in job_rows if not r.get("unreadable") and r.get("n_total_trials") is None),
            jobs_with_stated_expectation=len(stated),
            expected_equals_discovered=len(stated) - len(disagree),
            expected_differs_from_discovered=len(disagree),
            disagreements=[
                dict(folder=r["folder"], job=r["job"], n_total=r["n_total_trials"],
                     dirs=r["trial_directories"], pending=r["pending"], running=r["running"])
                for r in disagree
            ],
            jobs_with_retries=len(retried),
            total_trial_directories=sum(r.get("trial_directories") or 0 for r in job_rows),
        ),
        _tables=dict(rows=row_rows, jobs=job_rows),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--stage", default="all", choices=["all", "fetch", "analyse"])
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.stage in ("all", "fetch"):
        rows = stage_rows(args.out)
        print(f"leaderboard rows: {len(rows)}", file=sys.stderr)
        stage_details(args.out, rows)
        stage_jobs(args.out)

    if args.stage in ("all", "analyse"):
        report = analyse(args.out)
        tables = report.pop("_tables")
        (args.out / "tables.json").write_text(json.dumps(tables, indent=1))
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
