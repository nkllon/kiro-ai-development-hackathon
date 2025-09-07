#!/usr/bin/env python3
"""
Enhanced SHACL validator with security and temporal support.

This tool validates RDF data against SHACL shapes with additional features:
- Security-based filtering by clearance level
- Temporal filtering for point-in-time validation
- Audit trail generation
- Multi-file validation support

Usage:
    python tools/validate.py --data examples/usps-sun.ttl \
        --shapes ontology/shacl/core.shacl.ttl ontology/shacl/governance.shacl.ttl \
        --user-clearance internal \
        --as-of-date 2024-01-15T10:30:00Z
"""

import argparse
import sys
from datetime import datetime, timezone
from rdflib import Graph, Namespace, Literal
from pyshacl import validate

# Namespaces
SEC = Namespace("http://nkllon.dev/security#")
TIME = Namespace("http://nkllon.dev/time#")
EVENT = Namespace("http://nkllon.dev/event#")

def filter_by_security_clearance(graph, clearance_level):
    """Filter graph based on user's security clearance."""
    clearance_hierarchy = {
        "public": 0,
        "internal": 1, 
        "confidential": 2,
        "restricted": 3
    }
    
    user_level = clearance_hierarchy.get(clearance_level, 0)
    filtered_graph = Graph()
    
    for subj, pred, obj in graph:
        # Check if subject has security classification
        classification = graph.value(subj, SEC.hasClassification)
        if classification:
            resource_level = clearance_hierarchy.get(str(classification).split("#")[-1], 0)
            if user_level >= resource_level:
                filtered_graph.add((subj, pred, obj))
        else:
            # No classification = public
            filtered_graph.add((subj, pred, obj))
    
    return filtered_graph

def filter_by_temporal_validity(graph, as_of_date):
    """Filter graph to show only resources valid at specific date."""
    filtered_graph = Graph()
    as_of_dt = datetime.fromisoformat(as_of_date.replace('Z', '+00:00'))
    
    for subj, pred, obj in graph:
        # Check temporal validity
        valid_from = graph.value(subj, TIME.validFrom)
        valid_until = graph.value(subj, TIME.validUntil)
        
        is_valid = True
        if valid_from:
            from_dt = datetime.fromisoformat(str(valid_from).replace('Z', '+00:00'))
            if as_of_dt < from_dt:
                is_valid = False
        
        if valid_until and is_valid:
            until_dt = datetime.fromisoformat(str(valid_until).replace('Z', '+00:00'))
            if as_of_dt > until_dt:
                is_valid = False
        
        if is_valid:
            filtered_graph.add((subj, pred, obj))
    
    return filtered_graph

def generate_security_shapes(clearance_level):
    """Generate security-specific SHACL shapes based on clearance level."""
    shapes_graph = Graph()
    
    # Add security validation shapes based on clearance
    if clearance_level in ["confidential", "restricted"]:
        # Higher clearance users get additional validation
        shapes_ttl = f"""
        @prefix sec: <http://nkllon.dev/security#> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        
        sec:HighClearanceShape a sh:NodeShape ;
            sh:targetSubjectsOf sec:hasClassification ;
            sh:property [
                sh:path sec:hasClassification ;
                sh:in (sec:public sec:internal sec:confidential sec:restricted) ;
                sh:message "Security classification must be valid"
            ] .
        """
        shapes_graph.parse(data=shapes_ttl, format='turtle')
    
    return shapes_graph

def emit_validation_event(conforms, file_count, user_context, validation_stats):
    """Emit validation audit event."""
    event_data = {
        "event_id": str(uuid4()) if 'uuid4' in globals() else "validation_event",
        "event_type": "ValidationPerformed",
        "conforms": conforms,
        "file_count": file_count,
        "user": user_context.user_id if user_context else "anonymous",
        "clearance": user_context.clearance_level if user_context else "public",
        "validation_stats": validation_stats,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"VALIDATION_EVENT: {event_data}", file=sys.stderr)

def validate_with_security_and_temporal(data_files, shape_files, user_context=None, as_of_date=None):
    """Validate with security filtering and temporal constraints."""
    
    # Load and filter data based on security clearance
    data_g = Graph()
    original_triple_count = 0
    
    for f in data_files:
        temp_g = Graph()
        temp_g.parse(f, format='turtle')
        original_triple_count += len(temp_g)
        
        # Filter based on security classification
        if user_context and hasattr(user_context, 'clearance_level'):
            filtered_g = filter_by_security_clearance(temp_g, user_context.clearance_level)
            data_g += filtered_g
        else:
            data_g += temp_g
    
    # Apply temporal filtering if as_of_date provided
    if as_of_date:
        data_g = filter_by_temporal_validity(data_g, as_of_date)
    
    # Load shapes
    shapes_g = Graph()
    for s in shape_files:
        shapes_g.parse(s, format='turtle')
    
    # Add security-specific shapes based on user context
    if user_context and hasattr(user_context, 'clearance_level'):
        security_shapes = generate_security_shapes(user_context.clearance_level)
        shapes_g += security_shapes
    
    # Validate
    conforms, results_graph, results_text = validate(
        data_g, 
        shacl_graph=shapes_g, 
        inference='rdfs', 
        abort_on_error=False, 
        advanced=True
    )
    
    # Collect validation statistics
    validation_stats = {
        "original_triples": original_triple_count,
        "filtered_triples": len(data_g),
        "shape_count": len(list(shapes_g.subjects())),
        "temporal_filtering": as_of_date is not None
    }
    
    # Emit audit event
    emit_validation_event(conforms, len(data_files), user_context, validation_stats)
    
    return conforms, results_text, validation_stats

def main():
    parser = argparse.ArgumentParser(description="Validate RDF data against SHACL shapes with security and temporal support")
    parser.add_argument('--data', nargs='+', required=True, help='RDF data files to validate')
    parser.add_argument('--shapes', nargs='+', required=True, help='SHACL shape files')
    parser.add_argument('--user-clearance', choices=['public', 'internal', 'confidential', 'restricted'], 
                       help='User security clearance level')
    parser.add_argument('--as-of-date', help='ISO datetime for temporal filtering (e.g., 2024-01-15T10:30:00Z)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output including statistics')
    
    args = parser.parse_args()
    
    # Mock user context
    class UserContext:
        def __init__(self, clearance):
            self.clearance_level = clearance
            self.user_id = "validation_user"
    
    user_context = UserContext(args.user_clearance) if args.user_clearance else None
    
    try:
        conforms, results_text, stats = validate_with_security_and_temporal(
            args.data, 
            args.shapes, 
            user_context, 
            args.as_of_date
        )
        
        if args.verbose:
            print(f"Validation Statistics:", file=sys.stderr)
            print(f"  Original triples: {stats['original_triples']}", file=sys.stderr)
            print(f"  Filtered triples: {stats['filtered_triples']}", file=sys.stderr)
            print(f"  Shape count: {stats['shape_count']}", file=sys.stderr)
            print(f"  Temporal filtering: {stats['temporal_filtering']}", file=sys.stderr)
            print(f"  User clearance: {args.user_clearance or 'public'}", file=sys.stderr)
            print("", file=sys.stderr)
        
        print(results_text)
        
        if conforms:
            print("✅ Validation PASSED", file=sys.stderr)
        else:
            print("❌ Validation FAILED", file=sys.stderr)
        
        sys.exit(0 if conforms else 2)
        
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()