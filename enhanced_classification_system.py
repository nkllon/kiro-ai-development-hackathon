#!/usr/bin/env python3
"""
Enhanced Classification System
=============================

Incorporates all Beast Mode findings with full compliance spread:
- Fixed oversized detection logic
- SPA vs Traditional App classification
- Enhanced Meta/Facebook ecosystem detection
- Cross-domain pattern discovery
- Metaproperty detection system
"""

import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


@dataclass
class SPAAnalysis:
    """Single Page Application analysis results"""
    is_spa: bool
    spa_confidence: float
    framework_indicators: List[str]
    routing_type: str  # client_side, server_side, hybrid
    content_loading: str  # dynamic, static, hybrid
    api_usage: bool
    javascript_heavy: bool
    meta_framework: Optional[str]  # react, vue, angular, etc.
    spa_characteristics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetaEcosystemAnalysis:
    """Meta/Facebook ecosystem analysis results"""
    has_meta_integration: bool
    meta_confidence: float
    facebook_sdk: bool
    instagram_embed: bool
    whatsapp_integration: bool
    meta_business_tools: bool
    facebook_login: bool
    meta_analytics: bool
    open_graph_tags: bool
    meta_pixel: bool
    meta_ecosystem_indicators: List[str]
    metaproperty_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrossDomainPattern:
    """Cross-domain pattern discovery results"""
    pattern_id: str
    source_domain: str
    target_domain: str
    similarity_score: float
    pattern_type: str  # exact_match, high_similarity, novel_pattern
    pattern_characteristics: Dict[str, Any]
    investigation_priority: str  # high, medium, low
    metaproperty_indicators: List[str]
    worth_investigation: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetapropertyDetection:
    """Metaproperty detection results"""
    is_metaproperty: bool
    metaproperty_confidence: float
    source_pattern: str
    target_context: str
    pattern_transfer_indicators: List[str]
    novelty_score: float
    investigation_recommended: bool
    similar_patterns_found: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EnhancedClassificationSystem:
    """Enhanced classification system incorporating all Beast Mode findings"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cross_domain_patterns: List[CrossDomainPattern] = []
        self.metaproperty_detections: List[MetapropertyDetection] = []
        
        # SPA detection patterns
        self.spa_frameworks = {
            'react': ['react', 'jsx', 'createElement', 'useState', 'useEffect'],
            'vue': ['vue', 'v-if', 'v-for', 'Vue.component', 'vue-router'],
            'angular': ['angular', 'ng-', 'angular.module', 'angular.controller'],
            'svelte': ['svelte', 'svelte/store', 'svelte/transition'],
            'next': ['next.js', 'next/router', 'next/link', 'next/image'],
            'nuxt': ['nuxt', 'nuxt.config', 'nuxt/layouts'],
            'gatsby': ['gatsby', 'gatsby-plugin', 'gatsby-image']
        }
        
        # Meta ecosystem patterns
        self.meta_patterns = {
            'facebook_sdk': ['facebook.net', 'fbsdk', 'FB.init', 'facebook-js-sdk'],
            'instagram': ['instagram.com/embed', 'instagram.com/p/', 'instagram-media'],
            'whatsapp': ['wa.me', 'whatsapp.com', 'whatsapp://'],
            'meta_business': ['business.facebook.com', 'facebook.com/business'],
            'meta_analytics': ['facebook.com/tr', 'fbq(', 'Facebook Pixel'],
            'open_graph': ['property="og:', 'content="og:', 'og:title', 'og:description'],
            'meta_login': ['facebook.com/login', 'fb-login-button', 'facebook-login']
        }
        
        # Cross-domain pattern indicators
        self.cross_domain_indicators = {
            'authentication': ['login', 'auth', 'oauth', 'sso', 'jwt'],
            'form_handling': ['form', 'submit', 'validation', 'csrf'],
            'navigation': ['menu', 'nav', 'routing', 'breadcrumb'],
            'content_management': ['cms', 'content', 'editor', 'publish'],
            'ecommerce': ['cart', 'checkout', 'payment', 'product'],
            'social': ['share', 'like', 'comment', 'follow', 'social']
        }
    
    def analyze_page_comprehensive(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive page analysis incorporating all findings"""
        self.logger.info("🔍 Starting comprehensive page analysis...")
        
        # Extract basic page information
        url = page_data.get('url', '')
        title = page_data.get('title', '')
        html_content = page_data.get('html_content', '')
        
        # Run all analysis modules
        spa_analysis = self.detect_spa_characteristics(page_data)
        meta_analysis = self.detect_meta_ecosystem(page_data)
        cross_domain_patterns = self.detect_cross_domain_patterns(page_data)
        metaproperty_analysis = self.detect_metaproperties(page_data, cross_domain_patterns)
        
        # Combine results
        comprehensive_analysis = {
            'url': url,
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'spa_analysis': spa_analysis.to_dict(),
            'meta_analysis': meta_analysis.to_dict(),
            'cross_domain_patterns': [p.to_dict() for p in cross_domain_patterns],
            'metaproperty_analysis': metaproperty_analysis.to_dict(),
            'classification_summary': self._generate_classification_summary(
                spa_analysis, meta_analysis, metaproperty_analysis
            ),
            'investigation_priorities': self._generate_investigation_priorities(
                cross_domain_patterns, metaproperty_analysis
            )
        }
        
        self.logger.info(f"✅ Comprehensive analysis complete for {url}")
        return comprehensive_analysis
    
    def detect_spa_characteristics(self, page_data: Dict[str, Any]) -> SPAAnalysis:
        """Detect Single Page Application characteristics"""
        self.logger.info("🔍 Detecting SPA characteristics...")
        
        html_content = page_data.get('html_content', '').lower()
        url = page_data.get('url', '')
        
        # Initialize analysis
        framework_indicators = []
        spa_characteristics = {
            'client_side_routing': False,
            'dynamic_content_loading': False,
            'api_endpoints': False,
            'minimal_page_refresh': False,
            'javascript_heavy': False,
            'hash_routing': False,
            'history_api': False
        }
        
        # Detect JavaScript frameworks
        for framework, indicators in self.spa_frameworks.items():
            if any(indicator in html_content for indicator in indicators):
                framework_indicators.append(framework)
                spa_characteristics['client_side_routing'] = True
                spa_characteristics['javascript_heavy'] = True
        
        # Detect API usage patterns
        api_patterns = ['fetch(', 'axios', '$.ajax', 'XMLHttpRequest', 'api/', '/api/']
        if any(pattern in html_content for pattern in api_patterns):
            spa_characteristics['api_endpoints'] = True
            spa_characteristics['dynamic_content_loading'] = True
        
        # Detect routing patterns
        if '#' in url or 'hash' in html_content:
            spa_characteristics['hash_routing'] = True
        if 'history.pushState' in html_content or 'history.replaceState' in html_content:
            spa_characteristics['history_api'] = True
        
        # Detect minimal page refresh indicators
        refresh_patterns = ['preventDefault', 'stopPropagation', 'return false']
        if any(pattern in html_content for pattern in refresh_patterns):
            spa_characteristics['minimal_page_refresh'] = True
        
        # Calculate SPA confidence
        spa_score = sum([
            spa_characteristics['client_side_routing'],
            spa_characteristics['dynamic_content_loading'],
            spa_characteristics['api_endpoints'],
            spa_characteristics['javascript_heavy'],
            len(framework_indicators) > 0
        ]) / 5.0
        
        # Determine routing type
        if spa_characteristics['hash_routing']:
            routing_type = 'client_side'
        elif spa_characteristics['history_api']:
            routing_type = 'hybrid'
        else:
            routing_type = 'server_side'
        
        # Determine content loading type
        if spa_characteristics['dynamic_content_loading']:
            content_loading = 'dynamic'
        elif spa_characteristics['javascript_heavy']:
            content_loading = 'hybrid'
        else:
            content_loading = 'static'
        
        # Determine meta framework
        meta_framework = None
        if framework_indicators:
            meta_framework = framework_indicators[0]  # Primary framework
        
        return SPAAnalysis(
            is_spa=spa_score > 0.5,
            spa_confidence=spa_score,
            framework_indicators=framework_indicators,
            routing_type=routing_type,
            content_loading=content_loading,
            api_usage=spa_characteristics['api_endpoints'],
            javascript_heavy=spa_characteristics['javascript_heavy'],
            meta_framework=meta_framework,
            spa_characteristics=spa_characteristics
        )
    
    def detect_meta_ecosystem(self, page_data: Dict[str, Any]) -> MetaEcosystemAnalysis:
        """Detect Meta/Facebook ecosystem integration"""
        self.logger.info("🔍 Detecting Meta/Facebook ecosystem...")
        
        html_content = page_data.get('html_content', '').lower()
        url = page_data.get('url', '').lower()
        
        # Initialize analysis
        meta_ecosystem_indicators = []
        meta_integrations = {
            'facebook_sdk': False,
            'instagram_embed': False,
            'whatsapp_integration': False,
            'meta_business_tools': False,
            'facebook_login': False,
            'meta_analytics': False,
            'open_graph_tags': False,
            'meta_pixel': False
        }
        
        # Detect Meta ecosystem patterns
        for integration_type, patterns in self.meta_patterns.items():
            if any(pattern in html_content for pattern in patterns):
                meta_integrations[integration_type] = True
                meta_ecosystem_indicators.append(integration_type)
        
        # Additional URL-based detection
        if 'facebook.com' in url:
            meta_integrations['facebook_sdk'] = True
            meta_ecosystem_indicators.append('facebook_url')
        if 'instagram.com' in url:
            meta_integrations['instagram_embed'] = True
            meta_ecosystem_indicators.append('instagram_url')
        
        # Calculate Meta confidence
        meta_score = sum([
            meta_integrations['facebook_sdk'],
            meta_integrations['instagram_embed'],
            meta_integrations['whatsapp_integration'],
            meta_integrations['meta_business_tools'],
            meta_integrations['facebook_login'],
            meta_integrations['meta_analytics'],
            meta_integrations['open_graph_tags']
        ]) / 7.0
        
        # Calculate metaproperty score (how much this looks like a Meta property)
        metaproperty_score = 0.0
        if meta_integrations['facebook_sdk'] and meta_integrations['meta_analytics']:
            metaproperty_score += 0.4  # Core Meta integration
        if meta_integrations['open_graph_tags']:
            metaproperty_score += 0.3  # Social media integration
        if meta_integrations['facebook_login']:
            metaproperty_score += 0.3  # Authentication integration
        
        return MetaEcosystemAnalysis(
            has_meta_integration=meta_score > 0.3,
            meta_confidence=meta_score,
            facebook_sdk=meta_integrations['facebook_sdk'],
            instagram_embed=meta_integrations['instagram_embed'],
            whatsapp_integration=meta_integrations['whatsapp_integration'],
            meta_business_tools=meta_integrations['meta_business_tools'],
            facebook_login=meta_integrations['facebook_login'],
            meta_analytics=meta_integrations['meta_analytics'],
            open_graph_tags=meta_integrations['open_graph_tags'],
            meta_pixel=meta_integrations['meta_pixel'],
            meta_ecosystem_indicators=meta_ecosystem_indicators,
            metaproperty_score=metaproperty_score
        )
    
    def detect_cross_domain_patterns(self, page_data: Dict[str, Any]) -> List[CrossDomainPattern]:
        """Detect cross-domain patterns worth investigation"""
        self.logger.info("🔍 Detecting cross-domain patterns...")
        
        html_content = page_data.get('html_content', '').lower()
        url = page_data.get('url', '')
        domain = urlparse(url).netloc.lower()
        
        cross_domain_patterns = []
        
        # Analyze current page for patterns
        current_patterns = self._extract_patterns_from_content(html_content, url)
        
        # Compare with known cross-domain patterns
        for pattern_type, indicators in self.cross_domain_indicators.items():
            pattern_matches = sum(1 for indicator in indicators if indicator in html_content)
            
            if pattern_matches > 0:
                similarity_score = pattern_matches / len(indicators)
                
                # Check if this pattern has been seen in other domains
                similar_patterns = self._find_similar_patterns(pattern_type, domain)
                
                for similar_pattern in similar_patterns:
                    if similar_pattern['domain'] != domain:
                        cross_domain_pattern = CrossDomainPattern(
                            pattern_id=f"cross_domain_{len(cross_domain_patterns)}",
                            source_domain=similar_pattern['domain'],
                            target_domain=domain,
                            similarity_score=similarity_score,
                            pattern_type=self._classify_pattern_type(similarity_score),
                            pattern_characteristics=similar_pattern['characteristics'],
                            investigation_priority=self._determine_priority(similarity_score),
                            metaproperty_indicators=self._extract_metaproperty_indicators(
                                pattern_type, similar_pattern
                            ),
                            worth_investigation=similarity_score > 0.6
                        )
                        cross_domain_patterns.append(cross_domain_pattern)
        
        # Store current patterns for future comparison
        self._store_patterns(domain, current_patterns)
        
        return cross_domain_patterns
    
    def detect_metaproperties(self, page_data: Dict[str, Any], 
                            cross_domain_patterns: List[CrossDomainPattern]) -> MetapropertyDetection:
        """Detect metaproperties - patterns from one area appearing in different contexts"""
        self.logger.info("🔍 Detecting metaproperties...")
        
        url = page_data.get('url', '')
        domain = urlparse(url).netloc.lower()
        
        # Analyze for metaproperty indicators
        metaproperty_indicators = []
        pattern_transfer_indicators = []
        similar_patterns_found = []
        
        # Check cross-domain patterns for metaproperty potential
        for pattern in cross_domain_patterns:
            if pattern.worth_investigation:
                metaproperty_indicators.extend(pattern.metaproperty_indicators)
                pattern_transfer_indicators.append(
                    f"Pattern {pattern.pattern_type} from {pattern.source_domain} "
                    f"appears in {pattern.target_domain}"
                )
                similar_patterns_found.append(pattern.pattern_id)
        
        # Calculate novelty score
        novelty_score = len(metaproperty_indicators) / 10.0  # Normalize to 0-1
        novelty_score = min(novelty_score, 1.0)
        
        # Determine if this is a metaproperty
        is_metaproperty = (
            len(metaproperty_indicators) > 2 and
            novelty_score > 0.3 and
            len(similar_patterns_found) > 0
        )
        
        # Calculate metaproperty confidence
        metaproperty_confidence = (
            novelty_score * 0.4 +
            (len(metaproperty_indicators) / 5.0) * 0.3 +
            (len(similar_patterns_found) / 3.0) * 0.3
        )
        metaproperty_confidence = min(metaproperty_confidence, 1.0)
        
        return MetapropertyDetection(
            is_metaproperty=is_metaproperty,
            metaproperty_confidence=metaproperty_confidence,
            source_pattern=cross_domain_patterns[0].source_domain if cross_domain_patterns else "unknown",
            target_context=domain,
            pattern_transfer_indicators=pattern_transfer_indicators,
            novelty_score=novelty_score,
            investigation_recommended=is_metaproperty and metaproperty_confidence > 0.5,
            similar_patterns_found=similar_patterns_found
        )
    
    def _extract_patterns_from_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract patterns from HTML content"""
        patterns = {
            'authentication': 0,
            'form_handling': 0,
            'navigation': 0,
            'content_management': 0,
            'ecommerce': 0,
            'social': 0
        }
        
        # Count pattern indicators
        for pattern_type, indicators in self.cross_domain_indicators.items():
            patterns[pattern_type] = sum(1 for indicator in indicators if indicator in html_content)
        
        return patterns
    
    def _find_similar_patterns(self, pattern_type: str, current_domain: str) -> List[Dict[str, Any]]:
        """Find similar patterns from other domains"""
        # This would typically query a pattern database
        # For now, return mock data based on known patterns
        similar_patterns = []
        
        # Mock similar patterns (in real implementation, this would query a database)
        if pattern_type == 'authentication':
            similar_patterns.append({
                'domain': 'github.com',
                'characteristics': {'login_forms': 2, 'oauth_integration': True}
            })
            similar_patterns.append({
                'domain': 'google.com',
                'characteristics': {'login_forms': 1, 'oauth_integration': True}
            })
        elif pattern_type == 'form_handling':
            similar_patterns.append({
                'domain': 'devpost.com',
                'characteristics': {'form_validation': True, 'csrf_protection': True}
            })
        
        return similar_patterns
    
    def _classify_pattern_type(self, similarity_score: float) -> str:
        """Classify pattern type based on similarity score"""
        if similarity_score >= 0.9:
            return 'exact_match'
        elif similarity_score >= 0.7:
            return 'high_similarity'
        elif similarity_score >= 0.5:
            return 'moderate_similarity'
        else:
            return 'low_similarity'
    
    def _determine_priority(self, similarity_score: float) -> str:
        """Determine investigation priority based on similarity score"""
        if similarity_score >= 0.8:
            return 'high'
        elif similarity_score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _extract_metaproperty_indicators(self, pattern_type: str, similar_pattern: Dict[str, Any]) -> List[str]:
        """Extract metaproperty indicators from pattern analysis"""
        indicators = []
        
        if pattern_type == 'authentication':
            indicators.extend(['oauth_pattern', 'login_flow', 'session_management'])
        elif pattern_type == 'social':
            indicators.extend(['social_integration', 'sharing_pattern', 'social_auth'])
        elif pattern_type == 'ecommerce':
            indicators.extend(['payment_flow', 'cart_management', 'checkout_process'])
        
        return indicators
    
    def _store_patterns(self, domain: str, patterns: Dict[str, Any]):
        """Store patterns for future cross-domain analysis"""
        # In a real implementation, this would store to a database
        # For now, just log the patterns
        self.logger.debug(f"Storing patterns for {domain}: {patterns}")
    
    def _generate_classification_summary(self, spa_analysis: SPAAnalysis, 
                                       meta_analysis: MetaEcosystemAnalysis,
                                       metaproperty_analysis: MetapropertyDetection) -> Dict[str, Any]:
        """Generate classification summary"""
        return {
            'application_type': 'SPA' if spa_analysis.is_spa else 'Traditional',
            'spa_confidence': spa_analysis.spa_confidence,
            'meta_integration': meta_analysis.has_meta_integration,
            'meta_confidence': meta_analysis.meta_confidence,
            'is_metaproperty': metaproperty_analysis.is_metaproperty,
            'metaproperty_confidence': metaproperty_analysis.metaproperty_confidence,
            'primary_framework': spa_analysis.meta_framework,
            'investigation_priority': 'high' if metaproperty_analysis.investigation_recommended else 'low'
        }
    
    def _generate_investigation_priorities(self, cross_domain_patterns: List[CrossDomainPattern],
                                         metaproperty_analysis: MetapropertyDetection) -> List[Dict[str, Any]]:
        """Generate investigation priorities"""
        priorities = []
        
        # Add cross-domain pattern priorities
        for pattern in cross_domain_patterns:
            if pattern.worth_investigation:
                priorities.append({
                    'type': 'cross_domain_pattern',
                    'priority': pattern.investigation_priority,
                    'description': f"Pattern {pattern.pattern_type} from {pattern.source_domain}",
                    'similarity_score': pattern.similarity_score
                })
        
        # Add metaproperty investigation priority
        if metaproperty_analysis.investigation_recommended:
            priorities.append({
                'type': 'metaproperty_detection',
                'priority': 'high',
                'description': f"Metaproperty detected: {metaproperty_analysis.source_pattern} -> {metaproperty_analysis.target_context}",
                'confidence': metaproperty_analysis.metaproperty_confidence
            })
        
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        priorities.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return priorities
    
    def export_analysis(self, analysis: Dict[str, Any], output_file: str):
        """Export comprehensive analysis results"""
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        self.logger.info(f"✅ Analysis exported to {output_file}")


def main():
    """Main function to demonstrate enhanced classification system"""
    print("🚀 ENHANCED CLASSIFICATION SYSTEM")
    print("=" * 60)
    
    # Initialize system
    classifier = EnhancedClassificationSystem()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "React SPA with Meta Integration",
            "page_data": {
                "url": "https://example.com/dashboard",
                "title": "Dashboard - React App",
                "html_content": """
                <html>
                <head>
                    <meta property="og:title" content="My App">
                    <script src="https://facebook.net/js/api.js"></script>
                </head>
                <body>
                    <div id="root"></div>
                    <script>
                        React.createElement('div', null, 'Hello');
                        fetch('/api/users');
                        history.pushState({}, '', '/dashboard');
                    </script>
                </body>
                </html>
                """
            }
        },
        {
            "name": "Traditional DevPost Page",
            "page_data": {
                "url": "https://devpost.com/software/project-overview",
                "title": "Project Overview - DevPost",
                "html_content": """
                <html>
                <head>
                    <title>Project Overview</title>
                </head>
                <body>
                    <form action="/submit" method="post">
                        <input type="text" name="project_name">
                        <button type="submit">Submit</button>
                    </form>
                    <nav>
                        <a href="/login">Login</a>
                        <a href="/manage-team">Manage Team</a>
                    </nav>
                </body>
                </html>
                """
            }
        },
        {
            "name": "Meta Business Tool",
            "page_data": {
                "url": "https://business.facebook.com/ads",
                "title": "Facebook Ads Manager",
                "html_content": """
                <html>
                <head>
                    <script src="https://facebook.net/fbsdk.js"></script>
                    <meta property="og:type" content="website">
                </head>
                <body>
                    <div class="fb-login-button"></div>
                    <script>
                        FB.init({appId: '123456'});
                        fbq('track', 'PageView');
                    </script>
                </body>
                </html>
                """
            }
        }
    ]
    
    # Analyze each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎭 ANALYZING SCENARIO {i}: {scenario['name']}")
        print("-" * 50)
        
        analysis = classifier.analyze_page_comprehensive(scenario['page_data'])
        
        # Display key results
        summary = analysis['classification_summary']
        print(f"📊 CLASSIFICATION SUMMARY:")
        print(f"   Application Type: {summary['application_type']}")
        print(f"   SPA Confidence: {summary['spa_confidence']:.2f}")
        print(f"   Meta Integration: {summary['meta_integration']}")
        print(f"   Meta Confidence: {summary['meta_confidence']:.2f}")
        print(f"   Is Metaproperty: {summary['is_metaproperty']}")
        print(f"   Investigation Priority: {summary['investigation_priority']}")
        
        # Display investigation priorities
        priorities = analysis['investigation_priorities']
        if priorities:
            print(f"\n🎯 INVESTIGATION PRIORITIES:")
            for priority in priorities[:3]:  # Top 3 priorities
                print(f"   {priority['priority'].upper()}: {priority['description']}")
        
        # Export analysis
        output_file = f"enhanced_analysis_scenario_{i}.json"
        classifier.export_analysis(analysis, output_file)
        print(f"   Analysis exported to: {output_file}")
    
    print(f"\n🎉 Enhanced classification system demo complete!")
    print(f"   All Beast Mode findings incorporated:")
    print(f"   ✅ SPA Detection - Comprehensive Single Page Application classification")
    print(f"   ✅ Meta Ecosystem Detection - Facebook/Meta tool identification")
    print(f"   ✅ Cross-Domain Pattern Discovery - Novel pattern detection")
    print(f"   ✅ Metaproperty Detection - Pattern transfer identification")
    print(f"   ✅ Investigation Priorities - Automated priority assignment")


if __name__ == "__main__":
    main()

