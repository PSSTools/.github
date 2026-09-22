<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/lockup-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/lockup-light.png">
  <img alt="psstools" src="assets/lockup-light.png" width="420">
</picture>

### Open-source tooling for the Portable Test and Stimulus Standard

[![Website](https://img.shields.io/badge/docs-psstools.github.io-4FB0EE)](https://psstools.github.io)
[![PSS](https://img.shields.io/badge/Accellera-PSS-A855F7)](https://www.accellera.org/downloads/standards/portable-stimulus)

</div>

---

**psstools** builds a practical, open toolchain around the Accellera
[Portable Test and Stimulus Standard](https://www.accellera.org/downloads/standards/portable-stimulus)
(PSS) — from parsing and static analysis to compilation and SystemVerilog
integration. The goal: take a graph of *possible* behaviors and generate one
concrete, traversable scenario, the same way the mark above lights a single
**chosen path** through a greyed-out space of scenarios.

## Projects

| Repository | What it does |
|------------|--------------|
| [**pssc**](https://github.com/psstools/pssc) | The PSS compiler. Parses PSS, maps it to the Zuspec IR, and lowers to targets such as Python and SystemVerilog. |
| [**pssparser**](https://github.com/psstools/pssparser) | ANTLR4-based parser and AST/data model for the PSS language, with a plug-in system for custom checkers. |
| [**pss-sv-if**](https://github.com/psstools/pss-sv-if) | PSS-to-SystemVerilog core interface library for connecting generated stimulus to SV testbenches. |
| [**psstools.github.io**](https://github.com/psstools/psstools.github.io) | Documentation site for the toolchain. |

## Getting started

```sh
# Compile a PSS model to live Python classes
pip install pssc
pssc compile model.pss --target python -o out/

# Lint/check a PSS model
pssparser --list-checkers
pssparser model.pss
```

Full documentation lives at **[psstools.github.io](https://psstools.github.io)**.

## Contributing

We welcome issues and pull requests across all repositories. Head to the
project you're interested in to file an issue or open a PR.

Before opening a pull request, please read
**[CONTRIBUTING.md](https://github.com/psstools/.github/blob/main/CONTRIBUTING.md)** — it
covers the inbound terms and the two things asked of every contribution:

- **Sign off your commits.** `git commit -s` adds a `Signed-off-by` trailer certifying the
  [DCO](https://github.com/psstools/.github/blob/main/DCO). A CI check enforces it. This is
  not a copyright assignment — projects here carry shared copyright
  (`Copyright <year> Matthew Ballance and Contributors`) and you keep yours.
- **Follow the
  [Code of Conduct](https://github.com/psstools/.github/blob/main/CODE_OF_CONDUCT.md).**

Substantial contributions additionally need a signed ICLA; the threshold is published and
generous, and most contributions never reach it. Contributions are licensed under
Apache-2.0 and may be relicensed or contributed to a standards body such as Accellera as
part of long-term stewardship — see the
[relicensing notice](https://github.com/psstools/.github/blob/main/CONTRIBUTING.md#relicensing-notice).
