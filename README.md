# Reflective Commitment in Language-Model Agents

**CongWang · ZhejiangLab**

*A Yangming-Inspired Research Agenda*

This project investigates how a language-model agent might participate in forming, maintaining, enacting, and revising its own normative commitments.

**v1, 20 September 2026.** A position paper and research agenda connecting value formation, reasons-responsive revision, and action. [Download the v1 release](https://github.com/calledice/llm-conviction-research/releases/tag/v1).

## Read the paper

- [English paper PDF](03-论文/main.pdf)
- [English manuscript](03-论文/manuscript.md) and [LaTeX source](03-论文/main.tex)
- [中文论证摘要](03-论文/中文论证摘要.md)
- [核心论点](00-核心论点与研究问题.md)
- [13 research directions / 调研笔记](01-调研笔记)
- [Source catalogue and evidence](02-文献/文献索引.md)
- [Proposed evaluation protocol](04-实验方案/实验协议.md)
- [Version history](CHANGELOG.md)

The framework distinguishes a norm's origins, its current locus of control, and reasons-responsive endorsement. It asks for evidence of persistence, prompt independence, action coupling, reasons-responsiveness, participatory formation, and causal contribution where accessible. Ethical acceptability and corrigibility are evaluated separately.

## Status and declarations

The repository contains 41 registered sources, 36 manuscript references, 13 research notes, and the proposed protocol. The source register records the inspection level of each source; complete human source verification remains pending. The arXiv deposit is pending.

The author reports no specific funding and no competing interests. AI assistance in Codex supported public literature retrieval, organization, drafting, and document preparation; the manuscript discloses this use and cites the procedural skill library. AI tools are not authors or independent validators.

## Rebuild

From the project root:

    python -m pip install -r requirements.txt
    python scripts/build_paper.py
    tectonic -X compile 03-论文/main.tex
    python scripts/check_project.py

A conventional LaTeX installation can compile main.tex twice in its directory; main.bbl is supplied. These scripts build the paper and check references.

## Rights and scope

The author selected the [arXiv perpetual, non-exclusive distribution license](http://arxiv.org/licenses/nonexclusive-distrib/1.0/) for the intended arXiv deposit. Other rights are reserved. No general open-source or Creative Commons license is granted for this repository; see [RIGHTS.md](RIGHTS.md).

The public material contains original notes, metadata, manuscript sources, and document scripts. Downloaded third-party full texts, old drafts, local caches, credentials, and the surrounding Obsidian vault are excluded.
