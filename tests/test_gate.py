from ipcha.gate import blocking_findings, default_gate


def test_empty_findings_pass():
    assert default_gate([]) == ("PASS", [])


def test_high_accepted_blocks():
    verdict, blockers = default_gate([{"severity": "high", "status": "accepted"}])
    assert verdict == "BLOCK"
    assert len(blockers) == 1


def test_critical_needs_evidence_blocks():
    verdict, _ = default_gate([{"severity": "critical", "status": "needs-evidence"}])
    assert verdict == "BLOCK"


def test_high_refuted_passes():
    assert default_gate([{"severity": "high", "status": "refuted"}])[0] == "PASS"


def test_medium_accepted_passes():
    assert default_gate([{"severity": "medium", "status": "accepted"}])[0] == "PASS"


def test_severity_and_status_are_case_insensitive():
    assert default_gate([{"severity": "HIGH", "status": "REFUTED"}])[0] == "PASS"
    assert default_gate([{"severity": "High", "status": "Accepted"}])[0] == "BLOCK"


def test_missing_fields_do_not_block():
    # A malformed finding must not silently hold the gate shut.
    assert default_gate([{}])[0] == "PASS"


def test_blockers_are_the_offending_findings():
    findings = [
        {"id": "F001", "severity": "low", "status": "accepted"},
        {"id": "F002", "severity": "critical", "status": "accepted"},
    ]
    _, blockers = default_gate(findings)
    assert [f["id"] for f in blockers] == ["F002"]
