# GCP Billing Integration Design

## Architecture Overview

### Asset Bridge Pattern
We're implementing a systematic asset bridge to reuse OpenFlow-Playground's GCP billing analysis without reinventing the wheel. This follows Beast Mode's principle of systematic superiority over ad-hoc solutions.

```
OpenFlow-Playground GCP Code → Asset Bridge → Beast Mode Integration
```

## Component Design

### 1. Asset Extraction Strategy

#### Target Assets from OpenFlow-Playground
```
OpenFlow-Playground/
├── src/ghostbusters_gcp/
│   ├── billing/
│   │   ├── api_client.py          # GCP Billing API wrapper
│   │   ├── cost_analyzer.py       # Cost analysis logic
│   │   └── data_models.py         # Billing data structures
│   └── auth/
│       └── gcp_auth.py            # GCP authentication
```

#### Asset Bridge Module Structure
```
src/beast_mode/billing/
├── __init__.py
├── gcp_integration.py             # Main integration class
├── asset_bridge/
│   ├── __init__.py
│   ├── gcp_billing_client.py      # Adapted from OpenFlow
│   ├── cost_analyzer.py           # Adapted from OpenFlow
│   └── auth_manager.py            # Adapted from OpenFlow
└── interfaces.py                  # Beast Mode billing interfaces
```

### 2. Integration Architecture

#### Class Hierarchy
```python
# Beast Mode Integration
class GCPBillingMonitor(ReflectiveModule):
    """Beast Mode GCP billing integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.billing_client = GCPBillingClientBridge(config)
        self.cost_analyzer = CostAnalyzerBridge(config)
        
    async def collect_billing_metrics(self) -> GCPBillingMetrics:
        """Collect GCP billing data using bridged OpenFlow code"""
        
    def get_health_status(self) -> HealthStatus:
        """RM pattern compliance"""

# Asset Bridge Classes (adapted from OpenFlow)
class GCPBillingClientBridge:
    """Bridge wrapper around OpenFlow GCP billing client"""
    
class CostAnalyzerBridge:
    """Bridge wrapper around OpenFlow cost analyzer"""
```

#### Integration with Existing Resource Monitor
```python
# Extended BeastModeResourceMonitor
class BeastModeResourceMonitor:
    def __init__(self):
        # Existing initialization...
        self.gcp_monitor = GCPBillingMonitor(self.config.get('gcp', {}))
    
    async def _collect_financial_metrics(self):
        # Existing LLM cost collection...
        
        # Add GCP billing data
        gcp_metrics = await self.gcp_monitor.collect_billing_metrics()
        self._merge_gcp_costs(gcp_metrics)
```

### 3. Data Flow Design

#### GCP Billing Data Pipeline
```
GCP Billing API → Asset Bridge → Beast Mode Metrics → Dashboard
                      ↓
                 Local Cache → JSONL Logs → Historical Analysis
```

#### Data Structures
```python
@dataclass
class GCPBillingMetrics:
    """GCP billing metrics for Beast Mode integration"""
    project_id: str
    billing_account_id: str
    total_cost_usd: float
    daily_cost_usd: float
    cost_by_service: Dict[str, float]
    cost_by_sku: Dict[str, float]
    usage_metrics: Dict[str, Any]
    timestamp: datetime
    
@dataclass
class UnifiedFinancialMetrics:
    """Combined LLM + GCP + other costs"""
    llm_costs: Dict[str, float]
    gcp_costs: GCPBillingMetrics
    total_cost_usd: float
    cost_breakdown: Dict[str, float]
    burn_rate_hourly: float
    budget_status: BudgetStatus
    timestamp: datetime
```

### 4. Configuration Design

#### GCP Configuration Extension
```json
{
  "gcp": {
    "enabled": true,
    "billing_account_id": "XXXXXX-XXXXXX-XXXXXX",
    "project_ids": ["project-1", "project-2"],
    "credentials_path": "~/.config/gcp/credentials.json",
    "update_interval_minutes": 15,
    "cost_attribution": {
      "development": ["compute", "storage"],
      "ai_ml": ["aiplatform", "ml"],
      "networking": ["networking", "cdn"]
    },
    "budget_alerts": {
      "daily_limit_usd": 100.0,
      "hourly_spike_threshold": 10.0
    }
  }
}
```

### 5. Dashboard Integration Design

#### Enhanced Financial Display
```
💰 ═══════════════════════════════════════════════════════════
   BEAST MODE UNIFIED COST MONITOR
   "LLMs + GCP + Everything = Total Visibility"
═══════════════════════════════════════════════════════════

💸 FINANCIAL STATUS:
   💰 Total Cost: $45.67 (LLM: $12.34, GCP: $33.33)
   🔥 Burn Rate: $8.50/hour (LLM: $2.50, GCP: $6.00)
   🎯 Budget Remaining: $54.33

📊 GCP BREAKDOWN:
   🖥️  Compute Engine: $18.50
   🗄️  Cloud Storage: $8.25
   🤖 AI Platform: $6.58
   🌐 Networking: $2.15

🎯 RECENT ACTIVITY:
   📈 Cost spike detected: AI Platform (+$3.50 in last hour)
   ⚠️  Approaching daily budget (90% used)
   💡 Optimization: 3 idle compute instances detected
```

## Implementation Strategy

### Phase 1: Asset Extraction (4-6 hours)
1. **Locate OpenFlow GCP Code**
   - Search OpenFlow-Playground for billing-related modules
   - Identify core GCP API integration components
   - Document dependencies and requirements

2. **Create Asset Bridge Structure**
   - Set up `src/beast_mode/billing/` module
   - Create bridge wrapper classes
   - Implement basic interface adaptation

3. **Test Extracted Components**
   - Verify GCP API connectivity
   - Test authentication and basic queries
   - Validate data parsing and transformation

### Phase 2: Beast Mode Integration (6-8 hours)
1. **Extend Resource Monitor**
   - Add GCP billing collection to main monitor loop
   - Integrate with existing financial metrics
   - Update configuration handling

2. **Dashboard Enhancement**
   - Add GCP metrics to display logic
   - Implement unified cost visualization
   - Add GCP-specific alerts and thresholds

3. **Testing and Validation**
   - Test end-to-end integration
   - Verify cost accuracy against GCP console
   - Performance testing with real billing data

### Phase 3: Advanced Features (4-6 hours)
1. **Cost Attribution**
   - Tag costs with development context
   - Implement cost-per-feature tracking
   - Add project/team cost allocation

2. **Optimization Recommendations**
   - Detect idle resources
   - Suggest cost optimization opportunities
   - Implement automated cost alerts

## Technical Considerations

### GCP API Constraints
- **Rate Limits**: Billing API has generous limits but we'll implement caching
- **Data Latency**: Billing data can be 1-3 hours behind real-time
- **Authentication**: Reuse OpenFlow's service account approach
- **Permissions**: Requires `billing.accounts.get` and `billing.budgets.list`

### Performance Optimization
- **Caching Strategy**: Cache billing data for 15-30 minutes
- **Incremental Updates**: Only fetch new data since last update
- **Background Processing**: Run GCP queries in separate async tasks
- **Memory Management**: Limit historical data retention

### Error Handling
- **API Failures**: Graceful degradation when GCP API unavailable
- **Authentication Issues**: Clear error messages and recovery guidance
- **Data Inconsistencies**: Validation and reconciliation logic
- **Network Issues**: Retry logic with exponential backoff

## Asset Bridge Implementation Details

### Code Adaptation Strategy
1. **Minimal Changes**: Keep OpenFlow code as close to original as possible
2. **Interface Wrapping**: Add Beast Mode interfaces without changing core logic
3. **Configuration Mapping**: Map Beast Mode config to OpenFlow expectations
4. **Error Translation**: Convert OpenFlow exceptions to Beast Mode patterns

### Dependency Management
- **Shared Dependencies**: Use compatible versions of GCP SDK
- **Isolated Dependencies**: Vendor specific OpenFlow dependencies if needed
- **Version Pinning**: Lock versions to ensure compatibility
- **Testing Matrix**: Test with multiple GCP SDK versions

### Maintenance Strategy
- **Upstream Tracking**: Monitor OpenFlow changes for updates
- **Selective Updates**: Cherry-pick relevant improvements
- **Documentation**: Maintain clear provenance and change log
- **Testing**: Comprehensive test suite for bridge functionality

## Success Metrics

### Integration Success
- [ ] GCP billing data appears in Beast Mode dashboard
- [ ] Cost accuracy within 5% of GCP console
- [ ] Dashboard updates every 15 minutes
- [ ] Zero impact on existing functionality

### Performance Success
- [ ] Dashboard response time < 2 seconds
- [ ] Memory usage increase < 100MB
- [ ] GCP API calls within rate limits
- [ ] Background processing doesn't block UI

### User Experience Success
- [ ] Unified cost view across LLM and GCP
- [ ] Clear cost attribution and breakdown
- [ ] Actionable optimization recommendations
- [ ] Reliable alerting on budget thresholds

## Risk Mitigation

### Technical Risks
- **OpenFlow Code Not Found**: Implement minimal GCP integration as fallback
- **API Changes**: Test with current GCP Billing API version
- **Performance Impact**: Implement comprehensive monitoring and optimization
- **Integration Complexity**: Start with MVP, iterate based on feedback

### Timeline Risks
- **Asset Extraction Delays**: Allocate buffer time for code archaeology
- **Integration Challenges**: Have simplified integration path ready
- **Testing Complexity**: Focus on core functionality first, edge cases later

This design provides a systematic approach to leveraging existing OpenFlow assets while maintaining Beast Mode's architectural principles and performance requirements.