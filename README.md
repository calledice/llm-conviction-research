# Reflective Commitment in Language-Model Agents

**CongWang · ZhejiangLab**

*A Yangming-Inspired Research Agenda*

This project investigates how a language-model agent might participate in forming, maintaining, enacting, and revising its own normative commitments.

**v0.2 public working draft, 20 September 2026.** This is a position paper and proposed research agenda. It reports no new model experiments and does not establish consciousness or spontaneous convergence to beneficial values. The author has confirmed the core position; a complete human source audit remains pending.

## Read the paper

- [English paper PDF](03-论文/main.pdf)
- [English manuscript](03-论文/manuscript.md) and [LaTeX source](03-论文/main.tex)
- [中文论证摘要](03-论文/中文论证摘要.md)
- [核心论点](00-核心论点与研究问题.md)
- [13 research directions / 调研笔记](01-调研笔记)
- [Source catalogue and evidence](02-文献/文献索引.md)
- [Proposed evaluation protocol](04-实验方案/实验协议.md)

The framework distinguishes a norm's origins, its current locus of control, and reasons-responsive endorsement. It asks for evidence of persistence, prompt independence, action coupling, reasons-responsiveness, participatory formation, and causal contribution where accessible. Ethical acceptability and corrigibility are evaluated separately.

## Status and declarations

The repository contains 41 registered sources, 36 manuscript references, research notes, and the proposed protocol. No experiments have been run. No arXiv identifier has been assigned.

The author reports no specific funding and no competing interests. AI assistance in Codex supported public literature retrieval, organization, drafting, and document preparation; the manuscript discloses this use and cites the procedural skill library. AI tools are not authors or independent validators.

## Rebuild

From the project root:

    python -m pip install -r requirements.txt
    python scripts/build_paper.py
    tectonic -X compile 03-论文/main.tex
    python scripts/check_project.py

A conventional LaTeX installation can compile main.tex twice in its directory; main.bbl is supplied. These scripts build documents and check references; they do not train or evaluate models.

## Rights and scope

The author selected the [arXiv perpetual, non-exclusive distribution license](http://arxiv.org/licenses/nonexclusive-distrib/1.0/) for the intended arXiv deposit. Other rights are reserved. No general open-source or Creative Commons license is granted for this repository; see [RIGHTS.md](RIGHTS.md).

The public material contains original notes, metadata, manuscript sources, and document scripts. Downloaded third-party full texts, old drafts, local caches, credentials, and the surrounding Obsidian vault are excluded.
