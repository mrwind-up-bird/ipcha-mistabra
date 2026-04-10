import os
import json
import logging
from dataclasses import dataclass

import psycopg2

logger = logging.getLogger("ipcha.calibration.export")


@dataclass
class WorkflowRun:
    workflow_id: str
    proponent_text: str
    synthesis_text: str
    gate_decision: str
    finding_count: int
    critical_count: int


def export_runs(
    db_url: str | None = None,
    output_path: str = "calibration_data.json",
) -> list[WorkflowRun]:
    url = db_url or os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL required")

    conn = psycopg2.connect(url)
    cur = conn.cursor()

    # Find Ipcha workflows
    cur.execute("""
        SELECT w.id, w.name, w.status
        FROM workflows w
        WHERE w.name ILIKE '%ipcha%' OR w.name ILIKE '%mistabra%'
        ORDER BY w."createdAt" DESC
    """)
    workflows = cur.fetchall()
    logger.info("Found %d Ipcha workflows", len(workflows))

    runs = []
    for wf_id, wf_name, wf_status in workflows:
        cur.execute("""
            SELECT ws.label, ws.output, ws."subOutputs", ws."order"
            FROM workflow_steps ws
            WHERE ws."workflowId" = %s
            ORDER BY ws."order" ASC
        """, (wf_id,))
        steps = cur.fetchall()

        if len(steps) < 2:
            continue

        proponent_text = steps[0][1] or ""
        synthesis_text = steps[-1][1] or ""

        if not proponent_text or not synthesis_text:
            continue

        finding_count = 0
        for _, _, sub_outputs, _ in steps:
            if sub_outputs and isinstance(sub_outputs, list):
                finding_count += len(sub_outputs)

        runs.append(WorkflowRun(
            workflow_id=wf_id,
            proponent_text=proponent_text[:10000],
            synthesis_text=synthesis_text[:10000],
            gate_decision=wf_status or "UNKNOWN",
            finding_count=finding_count,
            critical_count=0,
        ))

    conn.close()

    data = [vars(r) for r in runs]
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Exported %d runs to %s", len(runs), output_path)
    return runs
