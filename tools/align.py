#!/usr/bin/env python3
"""
Mathematical alignment calculator with audit trails and event sourcing.

This tool implements the Beastmaster Ontology alignment mathematics:
- Vector-based requirement representation
- Cosine similarity for alignment scoring
- Conflict detection between requirements
- Feasibility constraint validation
- Complete audit trail with event sourcing

Usage:
    python tools/align.py --outcome "[0.8,-0.6,-0.2]" \
        --reqs '[{"vector":[1,-1,0],"weight":0.7}]' \
        --bounds '{"0":[0.6,1.0]}'
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from uuid import uuid4


def normalize(v):
    """Normalize vector to unit length."""
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n else v


def dot(a, b):
    """Compute dot product of two vectors."""
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    """Compute cosine similarity between two vectors."""
    na, nb = normalize(a), normalize(b)
    return dot(na, nb)


def conflict(a, b):
    """Compute conflict score between two requirement vectors."""
    c = cosine(a, b)
    return 1 - (1 + c) / 2  # map [-1,1] -> [0,1]


def weighted_alignment(outcome, reqs):
    """Compute weighted global alignment score."""
    o = normalize(outcome)
    num = 0.0
    den = 0.0
    for r in reqs:
        w = r.get("weight", 1.0)
        num += w * cosine(r["vector"], o)
        den += w
    return num / den if den else 0.0


def feasible(outcome, bounds):
    """Check if outcome satisfies feasibility constraints."""
    for i, (lo, hi) in bounds.items():
        if outcome[i] < lo or outcome[i] > hi:
            return False
    return True


def emit_event(event_type, event_data):
    """Emit domain event for audit trail."""
    event = {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "event_data": event_data,
    }

    # In production, this would go to event store
    print(f"EVENT: {json.dumps(event, indent=2)}", file=sys.stderr)
    return event


def calculate_with_audit(outcome, reqs, bounds=None, user_context=None, trace_id=None):
    """Calculate alignment with full audit trail."""
    calculation_id = str(uuid4())
    start_time = datetime.now(timezone.utc)
    bounds = bounds or {}

    # Emit start event
    emit_event(
        "AlignmentCalculationStarted",
        {
            "calculation_id": calculation_id,
            "trace_id": trace_id,
            "user": user_context.get("user_id") if user_context else None,
            "outcome": outcome,
            "requirements_count": len(reqs),
            "timestamp": start_time.isoformat(),
        },
    )

    try:
        # Calculate alignment
        alignment = weighted_alignment(outcome, reqs)

        # Check feasibility
        is_feasible = feasible(outcome, bounds)

        # Calculate conflicts
        conflicts = []
        for i in range(len(reqs)):
            for j in range(i + 1, len(reqs)):
                conflict_score = conflict(reqs[i]["vector"], reqs[j]["vector"])
                conflicts.append({"i": i, "j": j, "conflict": conflict_score})

                # Emit conflict event if high conflict
                if conflict_score > 0.7:
                    emit_event(
                        "ConflictDetected",
                        {
                            "calculation_id": calculation_id,
                            "requirement_i": i,
                            "requirement_j": j,
                            "conflict_score": conflict_score,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )

        # Check threshold violations
        threshold = 0.5  # Default threshold
        if alignment < threshold:
            emit_event(
                "ThresholdViolated",
                {
                    "calculation_id": calculation_id,
                    "alignment_score": alignment,
                    "threshold": threshold,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        # Check feasibility violations
        if not is_feasible:
            emit_event(
                "FeasibilityViolated",
                {
                    "calculation_id": calculation_id,
                    "outcome": outcome,
                    "bounds": bounds,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        # Success event
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        emit_event(
            "AlignmentCalculated",
            {
                "calculation_id": calculation_id,
                "alignment_score": alignment,
                "feasible": is_feasible,
                "conflicts": conflicts,
                "duration_ms": duration_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        return {
            "calculation_id": calculation_id,
            "alignment": alignment,
            "feasible": is_feasible,
            "conflicts": conflicts,
            "audit_trail": f"event:calculation_{calculation_id}",
        }

    except Exception as e:
        emit_event(
            "AlignmentCalculationFailed",
            {
                "calculation_id": calculation_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Compute alignment metrics with audit trail."
    )
    parser.add_argument(
        "--outcome", required=True, help='JSON list, e.g., "[0.8,0.6,-0.2]"'
    )
    parser.add_argument(
        "--reqs", required=True, help='JSON list of {"vector":[...],"weight":w}'
    )
    parser.add_argument("--bounds", default="{}", help="JSON dict {index:[lo,hi],...}")
    parser.add_argument("--user", help="User context JSON")
    parser.add_argument("--trace-id", help="Trace ID for correlation")
    parser.add_argument("--audit", action="store_true", help="Enable full audit trail")

    args = parser.parse_args()

    try:
        outcome = json.loads(args.outcome)
        reqs = json.loads(args.reqs)
        bounds = {int(k): tuple(v) for k, v in json.loads(args.bounds).items()}
        user_context = json.loads(args.user) if args.user else None

        if args.audit:
            result = calculate_with_audit(
                outcome, reqs, bounds, user_context, args.trace_id
            )
        else:
            # Simple calculation without audit
            A = weighted_alignment(outcome, reqs)
            F = feasible(outcome, bounds)
            conf = []
            for i in range(len(reqs)):
                for j in range(i + 1, len(reqs)):
                    conf.append(
                        {
                            "i": i,
                            "j": j,
                            "conflict": conflict(reqs[i]["vector"], reqs[j]["vector"]),
                        }
                    )

            result = {"alignment": A, "feasible": F, "conflicts": conf}

        print(json.dumps(result, indent=2))

        # Exit with error code if alignment is too low or infeasible
        if result["alignment"] < 0.5 or not result["feasible"]:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
