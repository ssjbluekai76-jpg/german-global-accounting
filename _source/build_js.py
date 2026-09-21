#!/usr/bin/env python3
"""Builds assets/site.js from _source/src/site.js (drops full-line comments and indentation).
Run:  python3 _source/build_js.py"""
import os, re, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "_source", "src", "site.js"), encoding="utf-8").read()
src = re.sub(r"/\*.*?\*/", "", src, flags=re.S) if False else src
out, in_block = [], False
for line in src.split("\n"):
    t = line.strip()
    if in_block:
        if "*/" in t: in_block = False
        continue
    if t.startswith("/*"):
        if "*/" not in t: in_block = True
        continue
    if not t or t.startswith("//"): continue
    out.append(t)
res = "\n".join(out) + "\n"
open(os.path.join(ROOT, "assets", "site.js"), "w", encoding="utf-8").write(res)
print(f"site.js  {len(src)/1024:.0f} KB -> {len(res)/1024:.0f} KB")
