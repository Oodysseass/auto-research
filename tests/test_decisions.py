import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import decisions  # noqa: E402
import check_packet  # noqa: E402

CARD = """# {id}

- class: {cls}
- status: {status}
- event: Definitions and property statements
- header: Corrupt win
- question: What does a successful corrupted mining attempt produce?
- recommendation: A
- reason: The notes give honest parties exactly this rule; the symmetric reading adds nothing new.
- depends: {depends}
- evidence: resources/notes.md:24; .work/model.md#OP4
- answer: none
- answered: none

## Options

- A | Extends chosen chain | Adversarial chains grow by one block per success; no new assumption.
- B | Any valid chain | The adversary may produce any valid chain; Lemma 2 likely fails.
- C | Leave open | Proofs may not use corrupted successes; counterexamples cannot either.
"""

CLAIMS = """# Claims registry

## C1
- label: def.a
- type: definition
- statement: a
- status: checked
- assumptions: A4
- depends_on: none
- verified_by: none
- refuted_by: none
- provisional_on: none
- base_status: none
- notes: none

## C2
- label: lem.b
- type: lemma
- statement: b
- status: verified
- assumptions: A1
- depends_on: C1
- verified_by: G1:conformance-reviewer:claude-opus-5-5@abc
- refuted_by: none
- notes: none

## C3
- label: lem.c
- type: lemma
- statement: c
- status: draft
- assumptions: none
- depends_on: none
- verified_by: none
- refuted_by: none
- notes: none

## C4
- label: lem.d
- type: lemma
- statement: d
- status: refuted
- assumptions: A4
- depends_on: none
- verified_by: none
- refuted_by: G2/counterexample-hunter/1
- notes: none
"""

BRIEF = """# Brief {id}

- stage: S5
- status: done
- claims: {claims}

## Goal

x
"""

STATE = """# State

- stage: S5

## Next actions

1. x

## Requeued

Briefs requeued by a reversed decision. Run them first.

- none
"""


def project(tmp_path, cls="checkpoint", status="open", depends="A4"):
    w = tmp_path / ".work"
    (w / "decisions").mkdir(parents=True)
    (w / "briefs").mkdir()
    (w / "decisions" / "D1.md").write_text(CARD.format(id="D1", cls=cls, status=status, depends=depends))
    (w / "claims.md").write_text(CLAIMS)
    (w / "briefs" / "S5-defs.md").write_text(BRIEF.format(id="S5-defs", claims="C1"))
    (w / "briefs" / "S7-lemma.md").write_text(BRIEF.format(id="S7-lemma", claims="C2"))
    (w / "briefs" / "S7-other.md").write_text(BRIEF.format(id="S7-other", claims="C3"))
    (w / "state.md").write_text(STATE)
    (w / "decisions.md").write_text("# Decisions\n")
    return tmp_path


def claims(root):
    _, blocks = decisions.parse_claim_blocks(root / ".work" / "claims.md")
    return {c: f for c, (_, _, f) in blocks.items()}


def run(root, *args):
    return decisions.main(["--root", str(root), *args])


def test_template_card_fields_match_script():
    t = (ROOT / "templates/project/.work/decisions/_template.md").read_text()
    for k in decisions.CARD_KEYS:
        assert f"- {k}:" in t


def test_lint_clean(tmp_path):
    root = project(tmp_path)
    assert decisions.lint_card(decisions.load(root, "D1")) == []


@pytest.mark.parametrize("old,new,msg", [
    ("- C | Leave open | Proofs may not use corrupted successes; counterexamples cannot either.\n", "", None),
    ("- header: Corrupt win", "- header: Corrupted success", "12 characters"),
    ("- recommendation: A", "- recommendation: D", "not an option"),
    ("produce?", "produce.", "'?'"),
    ("adds nothing new.", "adds nothing new and saves 200k tokens.", "token"),
    ("Lemma 2 likely fails.", "needs two more review rounds.", "review round count"),
    ("Lemma 2 likely fails.", "needs the Mythos tier.", "model"),
    ("- class: checkpoint", "- class: logged", "logged decisions get no card"),
    ("| Leave open |", "| Leave the corrupted success fully open |", "words"),
])
def test_lint_errors(tmp_path, old, new, msg):
    root = project(tmp_path)
    p = root / ".work/decisions/D1.md"
    p.write_text(p.read_text().replace(old, new))
    errs = decisions.lint_card(decisions.load(root, "D1"))
    if msg is None:  # two options is still fine
        assert errs == []
    else:
        assert any(msg in e for e in errs), errs


def test_lint_one_option_fails(tmp_path):
    root = project(tmp_path)
    p = root / ".work/decisions/D1.md"
    t = p.read_text()
    t = t.replace("- B | Any valid chain | The adversary may produce any valid chain; Lemma 2 likely fails.\n", "")
    t = t.replace("- C | Leave open | Proofs may not use corrupted successes; counterexamples cannot either.\n", "")
    p.write_text(t)
    assert any("need 2 to 4" in e for e in decisions.lint_card(decisions.load(root, "D1")))


def test_compress_recommended_first(tmp_path, capsys):
    root = project(tmp_path)
    p = root / ".work/decisions/D1.md"
    p.write_text(p.read_text().replace("- recommendation: A", "- recommendation: B"))
    assert run(root, "compress", "D1") == 0
    q = json.loads(capsys.readouterr().out)[0]
    assert q["options"][0]["label"] == "Any valid chain (Recommended)"
    assert "Why:" in q["options"][0]["description"]
    assert [o["label"] for o in q["options"][1:]] == ["Extends chosen chain", "Leave open"]
    assert len(q["header"]) <= 12 and 2 <= len(q["options"]) <= 4


def test_compress_batches_of_four(tmp_path, capsys):
    root = project(tmp_path)
    for i in range(2, 7):
        (root / f".work/decisions/D{i}.md").write_text(CARD.format(id=f"D{i}", cls="checkpoint", status="open", depends="none"))
    run(root, "compress", *[f"D{i}" for i in range(1, 7)])
    batches = json.loads(capsys.readouterr().out)
    assert [len(b) for b in batches] == [4, 2]


def test_next_id(tmp_path, capsys):
    root = project(tmp_path)
    run(root, "next-id")
    assert capsys.readouterr().out.strip() == "D2"


def test_affected_follows_assumptions_and_dependencies(tmp_path):
    root = project(tmp_path)
    affected, _ = decisions.affected_claims(root, decisions.load(root, "D1"))
    assert affected == ["C1", "C2"]  # C1 uses A4, C2 depends on C1; C4 is refuted; C3 unrelated


def test_provisional_then_accept_restores_status(tmp_path):
    root = project(tmp_path)
    assert run(root, "provisional", "D1") == 0
    c = claims(root)
    assert (c["C1"]["status"], c["C1"]["base_status"], c["C1"]["provisional_on"]) == ("provisional", "checked", "D1")
    assert (c["C2"]["status"], c["C2"]["base_status"]) == ("provisional", "verified")
    assert c["C4"]["status"] == "refuted"
    card = decisions.load(root, "D1")
    assert (card["status"], card["answer"]) == ("provisional", "A")
    assert run(root, "accept", "D1") == 0
    c = claims(root)
    assert (c["C1"]["status"], c["C2"]["status"]) == ("checked", "verified")
    assert c["C2"]["provisional_on"] == "none" and c["C2"]["base_status"] == "none"
    assert decisions.load(root, "D1")["status"] == "accepted"
    log = (root / ".work/decisions.md").read_text()
    assert "D1 provisional" in log and "D1 accepted" in log


def test_two_provisional_decisions_release_in_turn(tmp_path):
    root = project(tmp_path)
    (root / ".work/decisions/D2.md").write_text(CARD.format(id="D2", cls="checkpoint", status="open", depends="C2"))
    run(root, "provisional", "D1")
    run(root, "provisional", "D2")
    assert claims(root)["C2"]["provisional_on"] == "D1, D2"
    run(root, "accept", "D1")
    c = claims(root)
    assert (c["C1"]["status"], c["C2"]["status"], c["C2"]["provisional_on"]) == ("checked", "provisional", "D2")
    run(root, "accept", "D2")
    assert claims(root)["C2"]["status"] == "verified"


def test_reverse_requeues_dependent_work(tmp_path):
    root = project(tmp_path)
    run(root, "provisional", "D1")
    assert run(root, "reverse", "D1", "--to", "B") == 0
    c = claims(root)
    assert (c["C1"]["status"], c["C2"]["status"], c["C3"]["status"]) == ("draft", "draft", "draft")
    assert c["C2"]["verified_by"] == "none" and "requeued by D1" in c["C2"]["notes"]
    b = (root / ".work/briefs/S5-defs.md").read_text()
    assert "- status: requeued" in b
    assert "- status: requeued" in (root / ".work/briefs/S7-lemma.md").read_text()
    assert "- status: done" in (root / ".work/briefs/S7-other.md").read_text()
    st = (root / ".work/state.md").read_text()
    assert "briefs/S5-defs.md" in st and "briefs/S7-lemma.md" in st and "- none" not in st.split("## Requeued")[1]
    card = decisions.load(root, "D1")
    assert (card["status"], card["answer"]) == ("reversed", "B")


def test_accept_with_other_option_reverses(tmp_path):
    root = project(tmp_path)
    run(root, "provisional", "D1")
    run(root, "accept", "D1", "--option", "C")
    assert decisions.load(root, "D1")["status"] == "reversed"


def test_blocking_cannot_be_provisional(tmp_path):
    root = project(tmp_path, cls="blocking")
    assert run(root, "provisional", "D1") == 2
    assert run(root, "accept", "D1", "--option", "B") == 0
    card = decisions.load(root, "D1")
    assert (card["status"], card["answer"]) == ("accepted", "B")
    assert claims(root)["C1"]["status"] == "checked"


def test_checkpoint_screen_and_digest(tmp_path, capsys):
    root = project(tmp_path)
    (root / ".work/decisions.md").write_text(
        "# Decisions\n\n## 2026-11-01 | old routing\n- made by: orchestrator\n- class: logged\n- card: none\n- reason: x\n- routing: n/a\n"
        "\n## 2026-11-02 | checkpoint closed\n- made by: human\n- class: checkpoint\n- card: none\n- reason: x\n- routing: n/a\n"
        "\n## 2026-11-03 | route C2 to prover-mythos (T3)\n- made by: orchestrator\n- class: logged\n- card: none\n- reason: x\n- routing: claude-mythos-5-2, xhigh\n"
        "\n## 2026-11-03 | extend budget of S7-lemma by 50%\n- made by: orchestrator\n- class: logged\n- card: none\n- reason: new issues\n- routing: n/a\n")
    (root / ".work/usage.tsv").write_text("time\tsession\tstage_type\tbrief\trole\ttokens\nt\ts\tmodel\tS5-defs\tmodeler\t120000\n")
    run(root, "provisional", "D1")
    capsys.readouterr()
    run(root, "checkpoint")
    out = capsys.readouterr().out
    assert "**D1**" in out and "taken: Extends chosen chain" in out and "C1, C2" in out
    assert "route C2 to prover-mythos" in out and "extend budget of S7-lemma" in out
    assert "old routing" not in out
    assert "S5-defs: 120k" in out
    run(root, "checkpoint", "--questions")
    q = json.loads(capsys.readouterr().out)
    assert len(q) == 1 and q[0]["options"][0]["label"] == "Accept all (Recommended)"
    run(root, "accept", "D1")
    run(root, "checkpoint", "--close")
    capsys.readouterr()
    run(root, "checkpoint")
    out = capsys.readouterr().out
    assert "route C2" not in out and "## Provisional decisions (0)" in out


PACKET = """# Approval packet: S4

## What was produced

The model, with assumptions A1 to A13.

## What changed since the last approval

Everything: first approval.

## Review findings and resolution

One major issue on the corrupted mining rule, settled provisionally by D1.

## What remains uncertain

D1: corrupted successes extend the chosen chain (provisional).

## What approval unlocks

Stage S7: the lemma statements.
"""


def test_packet_ok(tmp_path):
    root = project(tmp_path)
    run(root, "provisional", "D1")
    p = tmp_path / "S4.md"
    p.write_text(PACKET)
    assert check_packet.check(p, root) == []


def test_packet_errors(tmp_path):
    root = project(tmp_path)
    run(root, "provisional", "D1")
    p = tmp_path / "S4.md"
    p.write_text(PACKET.replace("D1", "the decision").replace("## What approval unlocks\n\nStage S7: the lemma statements.\n",
                                                              "## What approval unlocks\n\n")
                 .replace("first approval.", "first approval. The stage used 300k tokens of its budget."))
    errs = check_packet.check(p, root)
    assert any("D1 is not named" in e for e in errs)
    assert any("empty" in e for e in errs)
    assert any("token" in e for e in errs) and any("budget" in e for e in errs)
