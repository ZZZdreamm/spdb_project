#!/usr/bin/env python3
import argparse
import csv
import json
import re
import statistics
import time
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent.parent
QFILE = ROOT / "postgres" / "queries.sql"
PARAMS = ROOT / "params" / "params.json"
OUT = ROOT / "results" / "postgres"
DEFAULT_SCALES = ["s10", "s25", "s50", "s100", "s10_noidx", "s10_comp", "s25_comp", "s50_comp", "s100_comp"]


def load_queries(path=QFILE):
    queries, name, buf = {}, None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"--\s*name:\s*(\S+)", line)
        if m:
            if name:
                queries[name] = "\n".join(buf)
            name, buf = m.group(1), []
        elif name and not line.lstrip().startswith(("--", "\\")):
            buf.append(line)
    if name:
        queries[name] = "\n".join(buf)
    return {n: to_driver(s.strip().rstrip(";")) for n, s in queries.items()}


def to_driver(sql):
    sql = re.sub(r":'(\w+)'", r"%(\1)s", sql)
    return re.sub(r"(?<![:\w]):([A-Za-z_]\w*)", r"%(\1)s", sql)


def connect(args):
    return psycopg.connect(host=args.host, port=args.port, user=args.user,
                           password=args.password, dbname=args.db, autocommit=True)


def write_env(conn):
    OUT.mkdir(parents=True, exist_ok=True)
    with conn.cursor() as cur:
        cur.execute("SELECT version(), postgis_full_version()")
        ver, gis = cur.fetchone()
        cur.execute("SELECT name, setting, unit FROM pg_settings WHERE name IN "
                    "('shared_buffers','effective_cache_size','work_mem','random_page_cost',"
                    "'max_parallel_workers_per_gather')")
        sett = cur.fetchall()
    lines = [ver, gis] + [f"{n} = {s} {u or ''}" for n, s, u in sett]
    (OUT / "env.txt").write_text("\n".join(lines) + "\n")


def run_explain(conn, queries, params, scale):
    d = OUT / "plans"
    d.mkdir(parents=True, exist_ok=True)
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {scale}, public")
        for name, sql in queries.items():
            cur.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql, params[0])
            plan = "\n".join(r[0] for r in cur.fetchall())
            (d / f"{name}_{scale}.txt").write_text(plan + "\n")
            print("plan", name, scale)


def run_bench(conn, queries, params, args, run):
    OUT.mkdir(parents=True, exist_ok=True)
    resfile = OUT / "results.csv"
    new = not resfile.exists() or (args.fresh and run == 1)
    with open(resfile, "w" if new else "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["dbms", "scale", "variant", "query", "param_idx", "rep", "time_ms", "rows", "run"])
        with conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {args.timeout * 1000}")
            for scale in args.scales:
                cur.execute(f"SET search_path TO {scale}, public")
                variant = "noidx" if scale.endswith("_noidx") else "comp" if scale.endswith("_comp") else "idx"
                pct = re.match(r"s(\d+)", scale).group(1)
                nparams = min(args.nparams, 10) if variant == "noidx" else args.nparams
                for qname, sql in queries.items():
                    times = []
                    for i, p in enumerate(params[:nparams]):
                        try:
                            cur.execute(sql, p)
                            cur.fetchall()
                            for rep in range(args.reps):
                                t0 = time.perf_counter()
                                cur.execute(sql, p)
                                rows = len(cur.fetchall())
                                ms = (time.perf_counter() - t0) * 1000
                                w.writerow(["postgres", pct, variant, qname, i, rep, f"{ms:.3f}", rows, run])
                                times.append(ms)
                        except psycopg.errors.QueryCanceled:
                            w.writerow(["postgres", pct, variant, qname, i, 0, args.timeout * 1000, -1, run])
                            times.append(args.timeout * 1000)
                    f.flush()
                    print(f"run{run} {scale:10s} {qname:4s} median={statistics.median(times):10.2f} ms  (n={len(times)})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--password", default="spdb")
    ap.add_argument("--db", default="spdb")
    ap.add_argument("--scales", nargs="+", default=DEFAULT_SCALES)
    ap.add_argument("--nparams", type=int, default=20)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--runs", type=int, default=1, help="liczba niezależnych przebiegów całego testu")
    ap.add_argument("--timeout", type=int, default=120, help="limit czasu zapytania [s]")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--fresh", action="store_true", help="nadpisz results.csv")
    args = ap.parse_args()

    queries = load_queries()
    params = json.loads(PARAMS.read_text())
    with connect(args) as conn:
        write_env(conn)
        if args.explain:
            for sc in ("s100", "s100_comp"):
                run_explain(conn, queries, params, sc)
        else:
            for run in range(1, args.runs + 1):
                run_bench(conn, queries, params, args, run)


if __name__ == "__main__":
    main()
