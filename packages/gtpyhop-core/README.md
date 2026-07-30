# gtpyhop-core

The GTPyhop planner (Goal-Task-Network planning), with no bundled example
domains. This is the package to install if you only need the planner —
for instance in production, CI, or any environment where install footprint
or file provenance matters.

```
pip install gtpyhop-core
```

`import gtpyhop` gives you the exact same public API as the full `gtpyhop`
package — the only difference is that `gtpyhop.examples` is not installed.

If you want the bundled example domains too, either install
`gtpyhop-examples` alongside this package, or install the `gtpyhop`
meta-package instead, which pulls in both.

Full documentation: https://github.com/PCfVW/GTPyhop/tree/pip
