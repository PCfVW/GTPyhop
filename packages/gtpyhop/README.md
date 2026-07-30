# gtpyhop

A Goal-Task-Network (HTN/HGN/GTN) planning package written in Python.

This is the full-bundle meta-package: it installs `gtpyhop-core` (the
planner) and `gtpyhop-examples` (the bundled example domains) together,
exactly as `pip install gtpyhop` always has.

```
pip install gtpyhop
```

If you only need the planner — for a production deployment, CI, or any
environment where install footprint or file provenance matters — install
`gtpyhop-core` on its own instead; it provides the identical `import
gtpyhop` public API without the bundled examples.

Full documentation, tutorials, and the complete list of example domains:
https://github.com/PCfVW/GTPyhop/tree/pip
