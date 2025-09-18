#!/usr/bin/env python3
"""
Adjacency Cluster Analyzer
=========================

Advanced cluster analysis and adjacency detection for session vectors.
"What the hell is this thing?" - Identifying new classes and outliers.
"""

import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import os
from collections import defaultdict
from dynamic_session_classifier import (
    SessionVector,
    SessionClassifier,
    MultiDimensionalSessionAnalyzer,
)


@dataclass
class ClusterAnalysis:
    """Results of cluster analysis"""

    cluster_id: str
    cluster_name: str
    vector_count: int
    centroid: Dict[str, float]  # average dimension values
    variance: Dict[str, float]  # variance in each dimension
    cohesion_score: float  # how tightly clustered
    separation_score: float  # how well separated from other clusters
    representative_vectors: List[str]  # vector hashes that represent this cluster
    outlier_vectors: List[str]  # vectors that don't fit well
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        return data


@dataclass
class AdjacencyResult:
    """Results of adjacency analysis between vectors"""

    vector1_hash: str
    vector2_hash: str
    similarity_score: float
    dimension_similarities: Dict[str, float]
    matching_dimensions: List[str]
    differing_dimensions: List[str]
    adjacency_type: str  # exact_match, high_similarity, moderate_similarity, low_similarity, outlier

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class OutlierAnalysis:
    """Analysis of outlier vectors"""

    vector_hash: str
    outlier_score: float
    closest_cluster: Optional[str]
    distance_to_closest: float
    outlier_reasons: List[str]
    potential_new_class: bool
    suggested_class_name: Optional[str]
    isolation_level: str  # completely_isolated, moderately_isolated, slightly_isolated

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class AdjacencyClusterAnalyzer:
    """Analyzes vector adjacency and clustering patterns"""

    def __init__(self):
        self.vectors: Dict[str, SessionVector] = {}
        self.clusters: Dict[str, ClusterAnalysis] = {}
        self.adjacency_matrix: Dict[str, Dict[str, AdjacencyResult]] = {}
        self.outliers: List[OutlierAnalysis] = []
        self.similarity_thresholds = {
            "exact_match": 0.95,
            "high_similarity": 0.8,
            "moderate_similarity": 0.6,
            "low_similarity": 0.4,
            "outlier": 0.2,
        }

    def add_vector(self, vector: SessionVector):
        """Add a vector to the analysis"""
        self.vectors[vector.vector_hash] = vector
        print(f"📊 Added vector: {vector.vector_hash}")

    def analyze_adjacency(self) -> Dict[str, Any]:
        """Main adjacency analysis - 'What the hell is this thing?'"""
        print("🔍 ADJACENCY ANALYSIS - Finding clusters and outliers...")

        if len(self.vectors) < 2:
            return {"error": "Need at least 2 vectors for adjacency analysis"}

        # Calculate adjacency matrix
        self._calculate_adjacency_matrix()

        # Find clusters
        clusters = self._find_clusters()

        # Identify outliers
        outliers = self._identify_outliers()

        # Analyze cluster patterns
        cluster_patterns = self._analyze_cluster_patterns()

        # Generate insights
        insights = self._generate_insights(clusters, outliers)

        return {
            "total_vectors": len(self.vectors),
            "clusters_found": len(clusters),
            "outliers_found": len(outliers),
            "clusters": {cid: cluster.to_dict() for cid, cluster in clusters.items()},
            "outliers": [outlier.to_dict() for outlier in outliers],
            "cluster_patterns": cluster_patterns,
            "insights": insights,
            "adjacency_matrix": self._serialize_adjacency_matrix(),
        }

    def _calculate_adjacency_matrix(self):
        """Calculate adjacency matrix between all vectors"""
        print("📐 Calculating adjacency matrix...")

        vector_hashes = list(self.vectors.keys())

        for i, hash1 in enumerate(vector_hashes):
            self.adjacency_matrix[hash1] = {}
            for j, hash2 in enumerate(vector_hashes):
                if i != j:
                    similarity = self._calculate_vector_similarity(
                        self.vectors[hash1], self.vectors[hash2]
                    )

                    adjacency_result = AdjacencyResult(
                        vector1_hash=hash1,
                        vector2_hash=hash2,
                        similarity_score=similarity["overall_similarity"],
                        dimension_similarities=similarity["dimension_similarities"],
                        matching_dimensions=similarity["matching_dimensions"],
                        differing_dimensions=similarity["differing_dimensions"],
                        adjacency_type=self._classify_adjacency_type(
                            similarity["overall_similarity"]
                        ),
                    )

                    self.adjacency_matrix[hash1][hash2] = adjacency_result

        print(f"✅ Adjacency matrix calculated for {len(vector_hashes)} vectors")

    def _calculate_vector_similarity(
        self, vector1: SessionVector, vector2: SessionVector
    ) -> Dict[str, Any]:
        """Calculate detailed similarity between two vectors"""
        similarities = {}
        matching_dimensions = []
        differing_dimensions = []

        # Get all dimensions
        all_dimensions = set(vector1.dimensions.keys()) | set(vector2.dimensions.keys())

        for dimension in all_dimensions:
            val1 = vector1.dimensions.get(dimension, 0.0)
            val2 = vector2.dimensions.get(dimension, 0.0)

            # Calculate similarity (1 - absolute difference)
            similarity = 1.0 - abs(val1 - val2)
            similarities[dimension] = similarity

            # Classify as matching or differing
            if similarity > 0.8:
                matching_dimensions.append(dimension)
            else:
                differing_dimensions.append(dimension)

        # Calculate overall similarity (weighted average)
        weights = {
            "technical_complexity": 0.2,
            "risk_level": 0.25,
            "uncertainty_level": 0.15,
            "resource_constraints": 0.1,
            "time_pressure": 0.1,
            "user_expertise": 0.1,
            "system_stability": 0.1,
        }

        weighted_similarity = sum(
            similarities.get(dim, 0.0) * weights.get(dim, 1.0) for dim in all_dimensions
        ) / sum(weights.get(dim, 1.0) for dim in all_dimensions)

        return {
            "overall_similarity": weighted_similarity,
            "dimension_similarities": similarities,
            "matching_dimensions": matching_dimensions,
            "differing_dimensions": differing_dimensions,
        }

    def _classify_adjacency_type(self, similarity: float) -> str:
        """Classify adjacency type based on similarity score"""
        if similarity >= self.similarity_thresholds["exact_match"]:
            return "exact_match"
        elif similarity >= self.similarity_thresholds["high_similarity"]:
            return "high_similarity"
        elif similarity >= self.similarity_thresholds["moderate_similarity"]:
            return "moderate_similarity"
        elif similarity >= self.similarity_thresholds["low_similarity"]:
            return "low_similarity"
        else:
            return "outlier"

    def _find_clusters(self) -> Dict[str, ClusterAnalysis]:
        """Find clusters of similar vectors"""
        print("🔍 Finding clusters...")

        clusters = {}
        processed_vectors = set()

        for vector_hash, vector in self.vectors.items():
            if vector_hash in processed_vectors:
                continue

            # Find all vectors similar to this one
            cluster_vectors = [vector_hash]
            processed_vectors.add(vector_hash)

            for other_hash, adjacency_result in self.adjacency_matrix[
                vector_hash
            ].items():
                if (
                    other_hash not in processed_vectors
                    and adjacency_result.adjacency_type
                    in ["exact_match", "high_similarity"]
                ):
                    cluster_vectors.append(other_hash)
                    processed_vectors.add(other_hash)

            # Create cluster if we have enough vectors
            if len(cluster_vectors) >= 2:
                cluster = self._create_cluster(cluster_vectors)
                clusters[cluster.cluster_id] = cluster
                print(
                    f"✅ Found cluster: {cluster.cluster_name} ({len(cluster_vectors)} vectors)"
                )

                # Mark all vectors in this cluster as processed
                for cluster_vector_hash in cluster_vectors:
                    processed_vectors.add(cluster_vector_hash)

        return clusters

    def _create_cluster(self, vector_hashes: List[str]) -> ClusterAnalysis:
        """Create a cluster from a list of vector hashes"""
        vectors = [self.vectors[hash_val] for hash_val in vector_hashes]

        # Calculate centroid (average dimension values)
        all_dimensions = set()
        for vector in vectors:
            all_dimensions.update(vector.dimensions.keys())

        centroid = {}
        variance = {}

        for dimension in all_dimensions:
            values = [v.dimensions.get(dimension, 0.0) for v in vectors]
            centroid[dimension] = sum(values) / len(values)

            # Calculate variance
            mean_val = centroid[dimension]
            variance[dimension] = sum((val - mean_val) ** 2 for val in values) / len(
                values
            )

        # Calculate cohesion score (how tightly clustered)
        cohesion_scores = []
        for i, hash1 in enumerate(vector_hashes):
            for j, hash2 in enumerate(vector_hashes):
                if i != j:
                    cohesion_scores.append(
                        self.adjacency_matrix[hash1][hash2].similarity_score
                    )

        cohesion_score = (
            sum(cohesion_scores) / len(cohesion_scores) if cohesion_scores else 0.0
        )

        # Calculate separation score (how well separated from other clusters)
        separation_score = self._calculate_separation_score(vector_hashes)

        # Find representative vectors (closest to centroid)
        representative_vectors = self._find_representative_vectors(vectors, centroid)

        # Find outlier vectors within cluster
        outlier_vectors = self._find_cluster_outliers(vectors, centroid)

        cluster = ClusterAnalysis(
            cluster_id=f"cluster_{len(self.clusters) + 1}",
            cluster_name=self._generate_cluster_name(centroid),
            vector_count=len(vectors),
            centroid=centroid,
            variance=variance,
            cohesion_score=cohesion_score,
            separation_score=separation_score,
            representative_vectors=representative_vectors,
            outlier_vectors=outlier_vectors,
            created_at=datetime.now(),
        )

        return cluster

    def _calculate_separation_score(self, vector_hashes: List[str]) -> float:
        """Calculate how well separated this cluster is from others"""
        if not self.clusters:
            return 1.0  # First cluster is perfectly separated

        separation_scores = []

        for cluster_id, cluster in self.clusters.items():
            # Calculate minimum distance to this cluster
            min_distance = float("inf")

            for vector_hash in vector_hashes:
                for other_hash in cluster.representative_vectors:
                    if other_hash in self.vectors:
                        similarity = self.adjacency_matrix[vector_hash][
                            other_hash
                        ].similarity_score
                        distance = 1.0 - similarity
                        min_distance = min(min_distance, distance)

            separation_scores.append(min_distance)

        return (
            sum(separation_scores) / len(separation_scores)
            if separation_scores
            else 1.0
        )

    def _find_representative_vectors(
        self, vectors: List[SessionVector], centroid: Dict[str, float]
    ) -> List[str]:
        """Find vectors that best represent the cluster centroid"""
        distances = []

        for vector in vectors:
            distance = 0.0
            for dimension, centroid_val in centroid.items():
                vector_val = vector.dimensions.get(dimension, 0.0)
                distance += (vector_val - centroid_val) ** 2

            distances.append((vector.vector_hash, distance))

        # Sort by distance and take the closest ones
        distances.sort(key=lambda x: x[1])
        return [hash_val for hash_val, _ in distances[: min(3, len(distances))]]

    def _find_cluster_outliers(
        self, vectors: List[SessionVector], centroid: Dict[str, float]
    ) -> List[str]:
        """Find vectors that are outliers within the cluster"""
        outliers = []

        for vector in vectors:
            distance = 0.0
            for dimension, centroid_val in centroid.items():
                vector_val = vector.dimensions.get(dimension, 0.0)
                distance += (vector_val - centroid_val) ** 2

            # If distance is too high, it's an outlier
            if distance > 0.5:  # Threshold for cluster outliers
                outliers.append(vector.vector_hash)

        return outliers

    def _generate_cluster_name(self, centroid: Dict[str, float]) -> str:
        """Generate a descriptive name for the cluster based on centroid"""
        dominant_dimensions = sorted(
            centroid.items(), key=lambda x: x[1], reverse=True
        )[:3]

        name_parts = []
        for dimension, value in dominant_dimensions:
            if value > 0.7:
                name_parts.append(f"High-{dimension.replace('_', ' ').title()}")
            elif value > 0.4:
                name_parts.append(f"Medium-{dimension.replace('_', ' ').title()}")
            else:
                name_parts.append(f"Low-{dimension.replace('_', ' ').title()}")

        return " ".join(name_parts)

    def _identify_outliers(self) -> List[OutlierAnalysis]:
        """Identify outlier vectors that don't fit well in any cluster"""
        print("🎯 Identifying outliers...")

        outliers = []

        # Track which vectors are already in clusters
        clustered_vectors = set()
        for cluster in self.clusters.values():
            # Get all vectors that belong to this cluster
            for vector_hash in self.vectors.keys():
                # Check if this vector is similar to cluster representatives
                is_in_cluster = False
                for rep_hash in cluster.representative_vectors:
                    if rep_hash in self.vectors:
                        similarity = self.adjacency_matrix[vector_hash][
                            rep_hash
                        ].similarity_score
                        if similarity > 0.7:  # High similarity threshold
                            is_in_cluster = True
                            break

                if is_in_cluster:
                    clustered_vectors.add(vector_hash)

        # Analyze vectors that are not in any cluster
        for vector_hash, vector in self.vectors.items():
            if vector_hash not in clustered_vectors:
                outlier_analysis = self._analyze_outlier(vector_hash, vector)
                outliers.append(outlier_analysis)

        return outliers

    def _analyze_outlier(
        self, vector_hash: str, vector: SessionVector
    ) -> OutlierAnalysis:
        """Analyze a potential outlier vector"""
        # Find closest cluster
        closest_cluster = None
        min_distance = float("inf")

        if self.clusters:
            for cluster_id, cluster in self.clusters.items():
                distance = 0.0
                for dimension, centroid_val in cluster.centroid.items():
                    vector_val = vector.dimensions.get(dimension, 0.0)
                    distance += (vector_val - centroid_val) ** 2

                if distance < min_distance:
                    min_distance = distance
                    closest_cluster = cluster_id
        else:
            # No clusters exist - calculate distance to other vectors
            for other_hash, other_vector in self.vectors.items():
                if other_hash != vector_hash:
                    distance = 0.0
                    all_dimensions = set(vector.dimensions.keys()) | set(
                        other_vector.dimensions.keys()
                    )
                    for dimension in all_dimensions:
                        val1 = vector.dimensions.get(dimension, 0.0)
                        val2 = other_vector.dimensions.get(dimension, 0.0)
                        distance += (val1 - val2) ** 2

                    if distance < min_distance:
                        min_distance = distance
                        closest_cluster = f"vector_{other_hash}"

        # Calculate outlier score
        outlier_score = min_distance if min_distance != float("inf") else 1.0

        # Determine isolation level
        if outlier_score > 0.8:
            isolation_level = "completely_isolated"
        elif outlier_score > 0.5:
            isolation_level = "moderately_isolated"
        else:
            isolation_level = "slightly_isolated"

        # Determine if this could be a new class
        potential_new_class = outlier_score > 0.6

        # Generate reasons for being an outlier
        outlier_reasons = []
        if vector.dimensions.get("technical_complexity", 0) > 0.8:
            outlier_reasons.append("Extremely high technical complexity")
        if vector.dimensions.get("risk_level", 0) > 0.8:
            outlier_reasons.append("Extremely high risk level")
        if vector.dimensions.get("uncertainty_level", 0) > 0.8:
            outlier_reasons.append("Extremely high uncertainty")
        if vector.dimensions.get("time_pressure", 0) > 0.8:
            outlier_reasons.append("Extremely high time pressure")

        # Suggest class name
        suggested_class_name = None
        if potential_new_class:
            suggested_class_name = self._suggest_outlier_class_name(vector)

        return OutlierAnalysis(
            vector_hash=vector_hash,
            outlier_score=outlier_score,
            closest_cluster=closest_cluster,
            distance_to_closest=min_distance if min_distance != float("inf") else 1.0,
            outlier_reasons=outlier_reasons,
            potential_new_class=potential_new_class,
            suggested_class_name=suggested_class_name,
            isolation_level=isolation_level,
        )

    def _suggest_outlier_class_name(self, vector: SessionVector) -> str:
        """Suggest a class name for an outlier vector"""
        dimensions = vector.dimensions

        # Find the most extreme dimensions
        extreme_dimensions = []
        for dimension, value in dimensions.items():
            if value > 0.8:
                extreme_dimensions.append(
                    f"Extreme-{dimension.replace('_', ' ').title()}"
                )
            elif value < 0.2:
                extreme_dimensions.append(
                    f"Minimal-{dimension.replace('_', ' ').title()}"
                )

        if extreme_dimensions:
            return " ".join(extreme_dimensions[:2])
        else:
            return "Unique Session Pattern"

    def _analyze_cluster_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across clusters"""
        patterns = {
            "cluster_sizes": [
                cluster.vector_count for cluster in self.clusters.values()
            ],
            "cohesion_scores": [
                cluster.cohesion_score for cluster in self.clusters.values()
            ],
            "separation_scores": [
                cluster.separation_score for cluster in self.clusters.values()
            ],
            "dominant_dimensions": {},
            "cluster_relationships": {},
        }

        # Analyze dominant dimensions across clusters
        for cluster_id, cluster in self.clusters.items():
            for dimension, value in cluster.centroid.items():
                if dimension not in patterns["dominant_dimensions"]:
                    patterns["dominant_dimensions"][dimension] = []
                patterns["dominant_dimensions"][dimension].append(value)

        # Analyze relationships between clusters
        for cluster1_id, cluster1 in self.clusters.items():
            patterns["cluster_relationships"][cluster1_id] = {}
            for cluster2_id, cluster2 in self.clusters.items():
                if cluster1_id != cluster2_id:
                    # Calculate distance between cluster centroids
                    distance = 0.0
                    all_dimensions = set(cluster1.centroid.keys()) | set(
                        cluster2.centroid.keys()
                    )
                    for dimension in all_dimensions:
                        val1 = cluster1.centroid.get(dimension, 0.0)
                        val2 = cluster2.centroid.get(dimension, 0.0)
                        distance += (val1 - val2) ** 2

                    patterns["cluster_relationships"][cluster1_id][
                        cluster2_id
                    ] = distance

        return patterns

    def _generate_insights(
        self, clusters: Dict[str, ClusterAnalysis], outliers: List[OutlierAnalysis]
    ) -> List[str]:
        """Generate insights about the clustering analysis"""
        insights = []

        # Cluster insights
        if clusters:
            insights.append(f"Found {len(clusters)} distinct session clusters")

            largest_cluster = max(clusters.values(), key=lambda c: c.vector_count)
            insights.append(
                f"Largest cluster: {largest_cluster.cluster_name} ({largest_cluster.vector_count} vectors)"
            )

            most_cohesive = max(clusters.values(), key=lambda c: c.cohesion_score)
            insights.append(
                f"Most cohesive cluster: {most_cohesive.cluster_name} (cohesion: {most_cohesive.cohesion_score:.2f})"
            )

            most_separated = max(clusters.values(), key=lambda c: c.separation_score)
            insights.append(
                f"Most separated cluster: {most_separated.cluster_name} (separation: {most_separated.separation_score:.2f})"
            )

        # Outlier insights
        if outliers:
            insights.append(f"Found {len(outliers)} outlier vectors")

            potential_new_classes = [o for o in outliers if o.potential_new_class]
            if potential_new_classes:
                insights.append(
                    f"{len(potential_new_classes)} outliers suggest new session classes:"
                )
                for outlier in potential_new_classes:
                    insights.append(
                        f"  - {outlier.suggested_class_name} (isolation: {outlier.isolation_level})"
                    )

            completely_isolated = [
                o for o in outliers if o.isolation_level == "completely_isolated"
            ]
            if completely_isolated:
                insights.append(
                    f"{len(completely_isolated)} vectors are completely isolated - strong candidates for new classes"
                )

        # Pattern insights
        if len(clusters) > 1:
            insights.append(
                "Multiple clusters suggest diverse session types in the dataset"
            )

        if len(outliers) > len(clusters):
            insights.append(
                "High number of outliers suggests the dataset may contain many unique session patterns"
            )

        return insights

    def _serialize_adjacency_matrix(self) -> Dict[str, Any]:
        """Serialize adjacency matrix for export"""
        serialized = {}
        for hash1, adjacencies in self.adjacency_matrix.items():
            serialized[hash1] = {}
            for hash2, adjacency_result in adjacencies.items():
                serialized[hash1][hash2] = adjacency_result.to_dict()
        return serialized

    def export_analysis(self, output_file: str):
        """Export adjacency analysis results"""
        analysis = self.analyze_adjacency()

        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"✅ Adjacency analysis exported to {output_file}")


def main():
    """Main function to demonstrate adjacency cluster analysis"""
    print("🔍 ADJACENCY CLUSTER ANALYZER")
    print("=" * 60)

    # Initialize analyzer
    analyzer = AdjacencyClusterAnalyzer()

    # Create test vectors with different patterns
    test_vectors = [
        # Cluster 1: High complexity, high risk
        SessionVector(
            session_id="complex_1",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.9,
                "risk_level": 0.8,
                "uncertainty_level": 0.6,
                "resource_constraints": 0.1,
                "time_pressure": 0.7,
                "user_expertise": 0.8,
                "system_stability": 0.7,
            },
            context_signals={},
            vector_hash="complex_1_hash",
        ),
        SessionVector(
            session_id="complex_2",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.8,
                "risk_level": 0.9,
                "uncertainty_level": 0.5,
                "resource_constraints": 0.2,
                "time_pressure": 0.8,
                "user_expertise": 0.7,
                "system_stability": 0.6,
            },
            context_signals={},
            vector_hash="complex_2_hash",
        ),
        SessionVector(
            session_id="complex_3",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.85,
                "risk_level": 0.7,
                "uncertainty_level": 0.7,
                "resource_constraints": 0.0,
                "time_pressure": 0.6,
                "user_expertise": 0.9,
                "system_stability": 0.8,
            },
            context_signals={},
            vector_hash="complex_3_hash",
        ),
        # Cluster 2: Low complexity, low risk
        SessionVector(
            session_id="simple_1",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.1,
                "risk_level": 0.2,
                "uncertainty_level": 0.1,
                "resource_constraints": 0.0,
                "time_pressure": 0.1,
                "user_expertise": 0.8,
                "system_stability": 0.9,
            },
            context_signals={},
            vector_hash="simple_1_hash",
        ),
        SessionVector(
            session_id="simple_2",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.2,
                "risk_level": 0.1,
                "uncertainty_level": 0.0,
                "resource_constraints": 0.1,
                "time_pressure": 0.0,
                "user_expertise": 0.9,
                "system_stability": 1.0,
            },
            context_signals={},
            vector_hash="simple_2_hash",
        ),
        # Outlier: Extreme uncertainty
        SessionVector(
            session_id="outlier_1",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.3,
                "risk_level": 0.1,
                "uncertainty_level": 0.95,
                "resource_constraints": 0.0,
                "time_pressure": 0.0,
                "user_expertise": 0.2,
                "system_stability": 0.8,
            },
            context_signals={},
            vector_hash="outlier_1_hash",
        ),
        # Outlier: Extreme time pressure
        SessionVector(
            session_id="outlier_2",
            timestamp=datetime.now(),
            dimensions={
                "technical_complexity": 0.4,
                "risk_level": 0.3,
                "uncertainty_level": 0.2,
                "resource_constraints": 0.8,
                "time_pressure": 0.95,
                "user_expertise": 0.6,
                "system_stability": 0.5,
            },
            context_signals={},
            vector_hash="outlier_2_hash",
        ),
    ]

    # Add vectors to analyzer
    for vector in test_vectors:
        analyzer.add_vector(vector)

    # Perform adjacency analysis
    print(f"\n🔍 ANALYZING {len(test_vectors)} VECTORS...")
    analysis = analyzer.analyze_adjacency()

    # Display results
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"   Total Vectors: {analysis['total_vectors']}")
    print(f"   Clusters Found: {analysis['clusters_found']}")
    print(f"   Outliers Found: {analysis['outliers_found']}")

    # Display clusters
    print(f"\n🏗️ CLUSTERS:")
    for cluster_id, cluster_data in analysis["clusters"].items():
        print(f"   {cluster_data['cluster_name']}:")
        print(f"     Vectors: {cluster_data['vector_count']}")
        print(f"     Cohesion: {cluster_data['cohesion_score']:.2f}")
        print(f"     Separation: {cluster_data['separation_score']:.2f}")
        print(f"     Representative: {cluster_data['representative_vectors']}")
        if cluster_data["outlier_vectors"]:
            print(f"     Internal Outliers: {cluster_data['outlier_vectors']}")

    # Display outliers
    print(f"\n🎯 OUTLIERS:")
    for outlier in analysis["outliers"]:
        print(f"   {outlier['vector_hash']}:")
        print(f"     Outlier Score: {outlier['outlier_score']:.2f}")
        print(f"     Isolation Level: {outlier['isolation_level']}")
        print(f"     Potential New Class: {outlier['potential_new_class']}")
        if outlier["suggested_class_name"]:
            print(f"     Suggested Class: {outlier['suggested_class_name']}")
        print(f"     Reasons: {', '.join(outlier['outlier_reasons'])}")

    # Display insights
    print(f"\n💡 INSIGHTS:")
    for insight in analysis["insights"]:
        print(f"   • {insight}")

    # Export analysis
    analyzer.export_analysis("adjacency_cluster_analysis.json")

    print(f"\n🎉 Adjacency cluster analysis complete!")
    print(f"   Analysis exported to: adjacency_cluster_analysis.json")


if __name__ == "__main__":
    main()
