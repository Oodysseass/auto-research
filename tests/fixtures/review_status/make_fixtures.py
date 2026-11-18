#!/usr/bin/env python3
"""Regenerate the review_status fixture directories. Run from anywhere; output is committed.

Each case is a mini project: <case>/paper/lemma.tex, <case>/.work/briefs/S1-lemma.md,
<case>/.work/issues/*.json. Artifact slug: `lemma`. File contents are versions "A", "B", ...
so the Review log hashes are real `git hash-object` values.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from review_status import content_hashes, format_hashes  # noqa: E402

SLUG = "lemma"
FILE = "paper/lemma.tex"


def content(v):
    return f"\\begin{{lemma}}\\label{{lem.x}} Version {v}. \\end{{lemma}}\n".encode()


def model(v):
    return f"# Model\n\n- A1: Delta-bounded synchrony, version {v}.\n"


def claims(v, status="draft"):
    """C1 (the artifact's claim) depends on C2, whose statement has version v. C3 is unrelated."""
    return ("# Claims registry\n\n"
            f"## C1\n- label: lem.x\n- type: lemma\n- statement: paper/lemma.tex#lem.x\n- status: {status}\n"
            "- assumptions: A1\n- depends_on: C2\n- verified_by: none\n- refuted_by: none\n- notes: none\n\n"
            f"## C2\n- label: def.y\n- type: definition\n- statement: Chain growth, version {v}.\n- status: draft\n"
            "- assumptions: A1\n- depends_on: none\n- verified_by: none\n- refuted_by: none\n- notes: none\n\n"
            "## C3\n- label: lem.z\n- type: lemma\n- statement: Unrelated.\n- status: draft\n"
            "- assumptions: none\n- depends_on: none\n- verified_by: none\n- refuted_by: none\n- notes: none\n")


GLOSSARY = "# Glossary\n\n## Macros\n\n| Macro | Kind | Meaning | Raw forms |\n|---|---|---|---|\n"
FIELDS = {"artifact files": FILE, "claims": "C1"}


def materialize(root, version, model_v, claims_v, status="draft"):
    (root / "paper").mkdir(parents=True, exist_ok=True)
    (root / ".work").mkdir(parents=True, exist_ok=True)
    (root / FILE).write_bytes(content(version))
    (root / ".work" / "model.md").write_text(model(model_v))
    (root / ".work" / "glossary.md").write_text(GLOSSARY)
    (root / ".work" / "claims.md").write_text(claims(claims_v, status))


def hashes(version, model_v="A", claims_v="A", status="draft"):
    with tempfile.TemporaryDirectory() as d:
        materialize(Path(d), version, model_v, claims_v, status)
        return format_hashes(content_hashes(d, FIELDS))


def issue(gate, rv, n, sev="major", dup=None):
    i = {"id": f"{gate}/{rv}/{n}", "severity": sev, "location": f"{FILE}:1", "claim": "C1",
         "evidence": "Quoted text and why it fails.", "suggested_fix": "One fix."}
    if dup:
        i["duplicate_of"] = dup
    return i


class Case:
    def __init__(self, name, current="A", critical=False, main=False, rounds=5, gates=None,
                 model="A", claims="A", status="draft"):
        self.dir = HERE / name
        self.current, self.critical, self.main, self.rounds, self.gates = current, critical, main, rounds, gates
        self.model, self.claims, self.status = model, claims, status
        self.log = []
        self.files = {}

    def review(self, gate, rv, rnd, version, issues=(), model="A", claims="A", status="draft"):
        issues = list(issues)
        bad = any(i["severity"] in ("blocking", "major") for i in issues)
        self.files[f"{SLUG}.{gate}.{rv}.r{rnd}.json"] = {
            "gate": gate, "reviewer": rv, "model": "claude-opus-5-5", "artifact": f"{FILE}#lem.x",
            "commit": f"c{version.lower()}{rnd}", "issues": issues, "verdict": "revise" if bad else "accept"}
        counts = [sum(i["severity"] == s for i in issues) for s in ("blocking", "major", "minor")]
        self.log.append(f"| {rnd} | {gate} | {rv} | claude-opus-5-5 | c{rnd} | {'revise' if bad else 'accept'} | "
                        f"{counts[0]} | {counts[1]} | {counts[2]} | {hashes(version, model, claims, status)} |")
        return self

    def respond(self, gate, rv, rnd, *answers):
        self.files[f"{SLUG}.{gate}.{rv}.r{rnd}.response.json"] = {
            "producer": "prover", "commit": f"x{rnd}",
            "responses": [{"issue_id": i, "status": s, "justification": "Because."} for i, s in answers]}
        return self

    def ruling(self, issue_id, k, verdict):
        g, rv, n = issue_id.split("/")
        self.files[f"{SLUG}.{g}.{rv}.i{n}.ruling{k}.json"] = {
            "arbiter": "arbiter", "model": "claude-opus-5-5", "commit": "r1", "artifact": FILE,
            "issue_id": issue_id, "ruling": verdict, "reviewer_case": "R.", "producer_case": "P.",
            "reasoning": "Checked.", "required_change": None,
            "human_question": "Which?" if verdict == "needs_human" else None}
        return self

    def clean_g2(self, rnd, version):
        for rv in ("assumption-auditor", "proof-checker", "counterexample-hunter"):
            self.review("G2", rv, rnd, version)
        return self

    def write(self):
        if self.dir.exists():
            shutil.rmtree(self.dir)
        materialize(self.dir, self.current, self.model, self.claims, self.status)
        issues = self.dir / ".work" / "issues"
        issues.mkdir(parents=True)
        for name, data in self.files.items():
            (issues / name).write_text(json.dumps(data, indent=2) + "\n")
        gates = f"- gates: {self.gates}\n" if self.gates else ""
        (self.dir / ".work" / "briefs").mkdir()
        (self.dir / ".work" / "briefs" / "S1-lemma.md").write_text(
            "# Brief S1-lemma\n\n- stage: S1\n- status: open\n- assigned agent: prover\n"
            f"- artifact slug: {SLUG}\n- artifact files: {FILE}\n- claims: C1\n- critical: {'yes' if self.critical else 'no'}\n"
            f"- main theorem: {'yes' if self.main else 'no'}\n{gates}\n"
            f"## Budget\n\n- rounds: {self.rounds}\n- tokens: 100k\n\n## Review log\n\n"
            "| round | gate | reviewer | model | commit | verdict | blocking | major | minor | hashes |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(self.log) + "\n")


def cases():
    G1, G2 = "conformance-reviewer", "proof-checker"
    X = f"G2/{G2}/1"
    yield (Case("converged").review("G1", G1, 1, "A").clean_g2(1, "A"))
    yield (Case("open").review("G1", G1, 1, "A", [issue("G1", G1, 1)]))
    yield (Case("deadlocked").review("G1", G1, 1, "A").review("G2", "assumption-auditor", 1, "A")
           .review("G2", G2, 1, "A", [issue("G2", G2, 1)]).respond("G2", G2, 1, (X, "rejected"))
           .review("G2", G2, 2, "A", [issue("G2", G2, 1)]).respond("G2", G2, 2, (X, "rejected"))
           .review("G2", G2, 3, "A", [issue("G2", G2, 1)]))
    yield (Case("stalled", current="B").review("G1", G1, 1, "B", [issue("G1", G1, 1)])
           .respond("G1", G1, 1, ("G1/conformance-reviewer/1", "fixed"))
           .review("G1", G1, 2, "B", [issue("G1", G1, 1)]))
    yield (Case("stalled-repeat", current="A").review("G1", G1, 1, "A", [issue("G1", G1, 1)])
           .respond("G1", G1, 1, ("G1/conformance-reviewer/1", "fixed"))
           .review("G1", G1, 2, "B", [issue("G1", G1, 2)])
           .respond("G1", G1, 2, ("G1/conformance-reviewer/2", "fixed"))
           .review("G1", G1, 3, "A", [issue("G1", G1, 1)]))
    yield (Case("max_rounds", current="C", rounds=3)
           .review("G1", G1, 1, "A", [issue("G1", G1, 1)]).respond("G1", G1, 1, ("G1/conformance-reviewer/1", "fixed"))
           .review("G1", G1, 2, "B", [issue("G1", G1, 2)]).respond("G1", G1, 2, ("G1/conformance-reviewer/2", "fixed"))
           .review("G1", G1, 3, "C", [issue("G1", G1, 3)]))
    yield (Case("critical-g3-second-round", critical=True)
           .review("G1", G1, 1, "A").clean_g2(1, "A").review("G3", "codex", 1, "A"))
    yield (Case("critical-awaiting-g3", critical=True).review("G1", G1, 1, "A").clean_g2(1, "A"))
    yield (Case("critical-g3-other-content", critical=True, current="B")
           .review("G1", G1, 1, "A").clean_g2(1, "A").review("G3", "codex", 1, "B"))
    yield (Case("critical-edit-between-clean-rounds", critical=True, current="B", gates="G1")
           .review("G1", G1, 1, "A").review("G1", G1, 2, "B"))
    yield (Case("critical-two-clean-rounds", critical=True, gates="G1")
           .review("G1", G1, 1, "A").review("G1", G1, 2, "A"))
    yield (Case("critical-model-changed-between-clean-rounds", critical=True, gates="G1", model="B")
           .review("G1", G1, 1, "A").review("G1", G1, 2, "A", model="B"))
    yield (Case("critical-dependency-changed-between-clean-rounds", critical=True, gates="G1", claims="B")
           .review("G1", G1, 1, "A").review("G1", G1, 2, "A", claims="B"))
    yield (Case("critical-status-changed-between-clean-rounds", critical=True, gates="G1", status="checked")
           .review("G1", G1, 1, "A").review("G1", G1, 2, "A", status="checked"))
    yield (Case("model-changed-after-clean", model="B").review("G1", G1, 1, "A").clean_g2(1, "A"))
    yield (Case("edit-after-clean", current="B").review("G1", G1, 1, "A").clean_g2(1, "A"))
    yield (Case("duplicate-only", critical=True)
           .review("G1", G1, 1, "A").review("G2", "assumption-auditor", 1, "A")
           .review("G2", G2, 1, "A", [issue("G2", G2, 1, "blocking")])
           .review("G2", "counterexample-hunter", 1, "A")
           .review("G3", "codex", 1, "A", [issue("G3", "codex", 1, "blocking", dup=X)]))
    dl = lambda name, **kw: (Case(name, **kw).review("G1", G1, 1, "A").review("G2", "assumption-auditor", 1, "A")
                             .review("G2", G2, 1, "A", [issue("G2", G2, 1)]).respond("G2", G2, 1, (X, "rejected"))
                             .review("G2", G2, 2, "A", [issue("G2", G2, 1)]).respond("G2", G2, 2, (X, "rejected"))
                             .review("G2", G2, 3, "A", [issue("G2", G2, 1)]))
    yield dl("ruling-producer-right").ruling(X, 1, "producer_right")
    yield dl("ruling-reviewer-right").ruling(X, 1, "reviewer_right")
    yield dl("ruling-reviewer-right-rejected-again").ruling(X, 1, "reviewer_right").respond("G2", G2, 3, (X, "rejected"))
    yield dl("ruling-needs-human-first").ruling(X, 1, "needs_human")
    yield dl("ruling-main-theorem", main=True).ruling(X, 1, "producer_right")
    yield (dl("duplicate-closed-by-ruling", critical=True).review("G2", "counterexample-hunter", 1, "A")
           .review("G3", "codex", 1, "A", [issue("G3", "codex", 1, "major", dup=X)]).ruling(X, 1, "producer_right"))
    yield dl("ruling-main-theorem-second", main=True).ruling(X, 1, "producer_right").ruling(X, 2, "reviewer_right")


if __name__ == "__main__":
    for c in cases():
        c.write()
        print("wrote", c.dir.name)
