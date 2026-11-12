#!/usr/bin/env python3
import argparse
import csv
import json
import re
import statistics
import time
from pathlib import Path

import mysql.connector
from mysql.connector import errors

ROOT = Path(__file__).resolve().parent.parent
QFILE = ROOT / "mysql" / "queries.sql"
PARAMS = ROOT / "params" / "params.json"
OUT = ROOT / "results" / "mysql"
DEFAULT_SCALES = ["s10", "s25", "s50", "s100", "s10_noidx"]
USER_VARS = ("px", "py", "category", "radius", "wkt_seg", "wkt_rect_small", "wkt_rect_big", "wkt_container")


def load_queries(path=QFILE):
    queries, name, buf = {}, None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"--\s*name:\s*(\S+)", line)
        if m:
            if name:
                queries[name] = "\n".join(buf)
            name, buf = m.group(1), []
        elif name and not line.lstrip().startswith("--"):
            buf.append(line)
    if name:
        queries[name] = "\n".join(buf)
    return {n: s.strip().rstrip(";") for n, s in queries.items()}


def set_vars(cur, p):
    cur.execute("SET " + ", ".join(f"@{k} = %s" for k in USER_VARS), [p[k] for k in USER_VARS])


def write_env(cur):
    OUT.mkdir(parents=True, exist_ok=True)
    cur.execute("SELECT VERSION()")
    lines = ["MySQL " + cur.fetchone()[0]]
    cur.execute("SHOW VARIABLES WHERE Variable_name IN ('innodb_buffer_pool_size','max_execution_time')")
    lines += [f"{k} = {v}" for k, v in cur.fetchall()]
    (OUT / "env.txt").write_text("\n".join(lines) + "\n")


def run_explain(cur, queries, params, scale):
    d = OUT / "plans"
    d.mkdir(parents=True, exist_ok=True)
    cur.execute(f"USE {scale}")
    set_vars(cur, params[0])
    for name, sql in queries.items():
        cur.execute("EXPLAIN ANALYZE " + sql)
        (d / f"{name}_{scale}.txt").write_text("\n".join(r[0] for r in cur.fetchall()) + "\n")
        print("plan", name, scale)


def run_bench(cur, queries, params, args, run):
    OUT.mkdir(parents=True, exist_ok=True)
    resfile = OUT / "results.csv"
    new = not resfile.exists() or (args.fresh and run == 1)
    cur.execute(f"SET SESSION max_execution_time = {args.timeout * 1000}")
    with open(resfile, "w" if new else "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["dbms", "scale", "variant", "query", "param_idx", "rep", "time_ms", "rows", "run"])
        for scale in args.scales:
            cur.execute(f"USE {scale}")
            variant = "noidx" if scale.endswith("_noidx") else "idx"
            pct = re.match(r"s(\d+)", scale).group(1)
            nparams = min(args.nparams, 10) if variant == "noidx" else args.nparams
            for qname, sql in queries.items():
                times = []
                for i, p in enumerate(params[:nparams]):
                    set_vars(cur, p)
                    try:
                        cur.execute(sql)
                        cur.fetchall()
                        for rep in range(args.reps):
                            t0 = time.perf_counter()
                            cur.execute(sql)
                            rows = len(cur.fetchall())
                            ms = (time.perf_counter() - t0) * 1000
                            w.writerow(["mysql", pct, variant, qname, i, rep, f"{ms:.3f}", rows, run])
                            times.append(ms)
                    except errors.DatabaseError as e:
                        if e.errno != 3024:
                            raise
                        w.writerow(["mysql", pct, variant, qname, i, 0, args.timeout * 1000, -1, run])
                        times.append(args.timeout * 1000)
                f.flush()
                print(f"run{run} {scale:10s} {qname:4s} median={statistics.median(times):10.2f} ms  (n={len(times)})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="spdb")
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
    conn = mysql.connector.connect(host=args.host, port=args.port, user=args.user,
                                   password=args.password, autocommit=True)
    cur = conn.cursor()
    write_env(cur)
    if args.explain:
        run_explain(cur, queries, params, "s100")
    else:
        for run in range(1, args.runs + 1):
            run_bench(cur, queries, params, args, run)
    conn.close()


if __name__ == "__main__":
    main()
