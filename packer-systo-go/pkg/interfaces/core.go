// Package interfaces defines the core interfaces for the Packer Systo Go toolkit
// This implements the systematic improvement interfaces from the design specification
package interfaces

import (
	"context"
	"time"
)

// DelusionType represents the category of delusion detected
type DelusionType string

const (
	DelusionTypeSyntax       DelusionType = "syntax"
	DelusionTypeSecurity     DelusionType = "security"
	DelusionTypeArchitecture DelusionType = "architecture"
	DelusionTypeBuild        DelusionType = "build"
)

// Severity represents the severity level of a detected issue
type Severity string

const (
	SeverityCritical Severity = "critical"
	SeverityHigh     Severity = "high"
	SeverityMedium   Severity = "medium"
	SeverityLow      Severity = "low"
)

// PackerConfig represents a Packer configuration with systematic enhancements
type PackerConfig struct {
	Source          string                 `json:"source"`
	Variables       map[string]interface{} `json:"variables"`
	Builders        []BuilderConfig        `json:"builders"`
	Provisioners    []ProvisionerConfig    `json:"provisioners"`
	PostProcessors  []PostProcessorConfig  `json:"post_processors"`
	ValidationRules []ValidationRule       `json:"validation_rules,omitempty"`
}

// BuilderConfig represents a Packer builder configuration
type BuilderConfig struct {
	Type   string                 `json:"type"`
	Name   string                 `json:"name,omitempty"`
	Config map[string]interface{} `json:"config"`
}

// ProvisionerConfig represents a Packer provisioner configuration
type ProvisionerConfig struct {
	Type   string                 `json:"type"`
	Config map[string]interface{} `json:"config"`
}

// PostProcessorConfig represents a Packer post-processor configuration
type PostProcessorConfig struct {
	Type   string                 `json:"type"`
	Config map[string]interface{} `json:"config"`
}

// ValidationRule represents a systematic validation rule
type ValidationRule struct {
	Name        string            `json:"name"`
	Type        string            `json:"type"`
	Parameters  map[string]string `json:"parameters"`
	Severity    Severity          `json:"severity"`
	Description string            `json:"description"`
}

// DelusionPattern represents a detected delusion pattern
type DelusionPattern struct {
	Type        DelusionType `json:"type"`
	Severity    Severity     `json:"severity"`
	Pattern     string       `json:"pattern"`
	Description string       `json:"description"`
	Remediation string       `json:"remediation"`
	Examples    []string     `json:"examples"`
	Confidence  float64      `json:"confidence"`
	Location    *Location    `json:"location,omitempty"`
}

// Location represents the location of an issue in a configuration file
type Location struct {
	File   string `json:"file"`
	Line   int    `json:"line"`
	Column int    `json:"column"`
	Length int    `json:"length,omitempty"`
}

// DelusionAnalysis represents the results of delusion detection analysis
type DelusionAnalysis struct {
	Patterns              []DelusionPattern     `json:"patterns"`
	SeverityDistribution  map[Severity]int      `json:"severity_distribution"`
	ConfidenceScore       float64               `json:"confidence_score"`
	RemediationPlan       *RemediationPlan      `json:"remediation_plan"`
	LearningOpportunities []LearningPattern     `json:"learning_opportunities"`
	AnalysisTimestamp     time.Time             `json:"analysis_timestamp"`
}

// DelusionReport represents a comprehensive delusion detection report
type DelusionReport struct {
	ConfigHash string           `json:"config_hash"`
	Analysis   DelusionAnalysis `json:"analysis"`
	Metadata   ReportMetadata   `json:"metadata"`
}

// RemediationPlan represents a systematic plan for fixing detected issues
type RemediationPlan struct {
	Steps       []RemediationStep `json:"steps"`
	Confidence  float64           `json:"confidence"`
	Complexity  string            `json:"complexity"`
	EstimatedTime time.Duration   `json:"estimated_time"`
}

// RemediationStep represents a single step in a remediation plan
type RemediationStep struct {
	ID          string            `json:"id"`
	Description string            `json:"description"`
	Action      string            `json:"action"`
	Parameters  map[string]string `json:"parameters"`
	Validation  []string          `json:"validation"`
}

// LearningPattern represents a pattern that can be learned from
type LearningPattern struct {
	Pattern     string  `json:"pattern"`
	Context     string  `json:"context"`
	Frequency   int     `json:"frequency"`
	Accuracy    float64 `json:"accuracy"`
	LastSeen    time.Time `json:"last_seen"`
}

// ReportMetadata contains metadata about analysis reports
type ReportMetadata struct {
	Version     string    `json:"version"`
	Timestamp   time.Time `json:"timestamp"`
	AnalyzerID  string    `json:"analyzer_id"`
	ConfigPath  string    `json:"config_path"`
	Environment string    `json:"environment"`
}

// DelusionDetector defines the interface for delusion detection
type DelusionDetector interface {
	// AnalyzeConfiguration performs comprehensive delusion analysis on a Packer configuration
	AnalyzeConfiguration(ctx context.Context, config *PackerConfig) (*DelusionReport, error)
	
	// DetectPatterns detects delusion patterns in raw HCL content
	DetectPatterns(ctx context.Context, hcl string) ([]DelusionPattern, error)
	
	// LearnFromCorrection learns from user corrections to improve accuracy
	LearnFromCorrection(ctx context.Context, pattern DelusionPattern, correction string) error
	
	// GetConfidenceScore calculates confidence score for an analysis
	GetConfidenceScore(analysis *DelusionAnalysis) float64
	
	// UpdatePatternDatabase updates the pattern database with new patterns
	UpdatePatternDatabase(ctx context.Context, patterns []DelusionPattern) error
}

// Diagnosis represents the diagnosis of a build failure
type Diagnosis struct {
	FailureType    string            `json:"failure_type"`
	RootCause      string            `json:"root_cause"`
	AffectedComponents []string      `json:"affected_components"`
	Confidence     float64           `json:"confidence"`
	Evidence       []Evidence        `json:"evidence"`
	Recommendations []string         `json:"recommendations"`
}

// Evidence represents evidence supporting a diagnosis
type Evidence struct {
	Type        string `json:"type"`
	Description string `json:"description"`
	Source      string `json:"source"`
	Confidence  float64 `json:"confidence"`
}

// RecoveryPlan represents a systematic recovery plan
type RecoveryPlan struct {
	ID          string           `json:"id"`
	Steps       []RecoveryStep   `json:"steps"`
	Confidence  float64          `json:"confidence"`
	Rollback    []RollbackStep   `json:"rollback"`
	Validation  []ValidationCheck `json:"validation"`
	EstimatedTime time.Duration  `json:"estimated_time"`
}

// RecoveryStep represents a single recovery step
type RecoveryStep struct {
	ID          string            `json:"id"`
	Description string            `json:"description"`
	Action      string            `json:"action"`
	Parameters  map[string]string `json:"parameters"`
	Timeout     time.Duration     `json:"timeout"`
	Retries     int               `json:"retries"`
}

// RollbackStep represents a rollback step
type RollbackStep struct {
	ID          string            `json:"id"`
	Description string            `json:"description"`
	Action      string            `json:"action"`
	Parameters  map[string]string `json:"parameters"`
}

// ValidationCheck represents a validation check
type ValidationCheck struct {
	ID          string            `json:"id"`
	Description string            `json:"description"`
	Type        string            `json:"type"`
	Parameters  map[string]string `json:"parameters"`
	Expected    interface{}       `json:"expected"`
}

// RecoveryResult represents the result of recovery execution
type RecoveryResult struct {
	Success             bool              `json:"success"`
	AppliedFixes        []AppliedFix      `json:"applied_fixes"`
	ConfidenceImprovement float64         `json:"confidence_improvement"`
	ValidationResults   *ValidationReport `json:"validation_results"`
	RollbackPlan        *RollbackPlan     `json:"rollback_plan,omitempty"`
	LearningData        *LearningData     `json:"learning_data"`
	ExecutionTime       time.Duration     `json:"execution_time"`
}

// AppliedFix represents a fix that was applied
type AppliedFix struct {
	ID          string    `json:"id"`
	Description string    `json:"description"`
	Type        string    `json:"type"`
	Success     bool      `json:"success"`
	Timestamp   time.Time `json:"timestamp"`
	Details     string    `json:"details"`
}

// RollbackPlan represents a plan for rolling back changes
type RollbackPlan struct {
	Steps     []RollbackStep `json:"steps"`
	Automatic bool           `json:"automatic"`
	Timeout   time.Duration  `json:"timeout"`
}

// LearningData represents data learned from recovery operations
type LearningData struct {
	Patterns    []string  `json:"patterns"`
	Success     bool      `json:"success"`
	Context     string    `json:"context"`
	Timestamp   time.Time `json:"timestamp"`
	Feedback    string    `json:"feedback,omitempty"`
}

// RecoveryEngine defines the interface for systematic recovery
type RecoveryEngine interface {
	// DiagnoseFailure diagnoses a build failure from logs and configuration
	DiagnoseFailure(ctx context.Context, buildLog string, config *PackerConfig) (*Diagnosis, error)
	
	// GenerateRecoveryPlan generates a systematic recovery plan from diagnosis
	GenerateRecoveryPlan(ctx context.Context, diagnosis *Diagnosis) (*RecoveryPlan, error)
	
	// ExecuteRecovery executes a recovery plan
	ExecuteRecovery(ctx context.Context, plan *RecoveryPlan) (*RecoveryResult, error)
	
	// ValidateRecovery validates the results of recovery
	ValidateRecovery(ctx context.Context, result *RecoveryResult) (*ValidationReport, error)
	
	// LearnFromRecovery learns from recovery operations to improve future performance
	LearnFromRecovery(ctx context.Context, result *RecoveryResult, feedback string) error
}

// ValidationReport represents a comprehensive validation report
type ValidationReport struct {
	ConfigHash    string              `json:"config_hash"`
	Timestamp     time.Time           `json:"timestamp"`
	Dimensions    *MultiDimReport     `json:"dimensions"`
	Issues        []ValidationIssue   `json:"issues"`
	Recommendations []string          `json:"recommendations"`
	OverallScore  float64             `json:"overall_score"`
}

// MultiDimReport represents multi-dimensional validation results
type MultiDimReport struct {
	Functionality float64 `json:"functionality"` // Does it work as expected?
	Performance   float64 `json:"performance"`   // Is it optimized?
	Security      float64 `json:"security"`      // Is it secure?
	Compliance    float64 `json:"compliance"`    // Does it meet standards?
	Overall       float64 `json:"overall"`       // Weighted average
}

// ValidationIssue represents a validation issue
type ValidationIssue struct {
	ID          string   `json:"id"`
	Type        string   `json:"type"`
	Severity    Severity `json:"severity"`
	Description string   `json:"description"`
	Location    *Location `json:"location,omitempty"`
	Remediation string   `json:"remediation"`
}

// BuildResult represents the result of a Packer build
type BuildResult struct {
	Success       bool              `json:"success"`
	Artifacts     []BuildArtifact   `json:"artifacts"`
	Metrics       *BuildMetrics     `json:"metrics"`
	Logs          []LogEntry        `json:"logs"`
	Timestamp     time.Time         `json:"timestamp"`
	Duration      time.Duration     `json:"duration"`
	Configuration *PackerConfig     `json:"configuration"`
}

// BuildArtifact represents a build artifact
type BuildArtifact struct {
	ID       string            `json:"id"`
	Type     string            `json:"type"`
	Location string            `json:"location"`
	Metadata map[string]string `json:"metadata"`
	Size     int64             `json:"size"`
	Checksum string            `json:"checksum"`
}

// BuildMetrics represents build performance metrics
type BuildMetrics struct {
	TotalTime     time.Duration     `json:"total_time"`
	StepTimes     map[string]time.Duration `json:"step_times"`
	ResourceUsage *ResourceUsage    `json:"resource_usage"`
	CacheHits     int               `json:"cache_hits"`
	CacheMisses   int               `json:"cache_misses"`
}

// ResourceUsage represents resource usage during build
type ResourceUsage struct {
	CPUPercent    float64 `json:"cpu_percent"`
	MemoryMB      int64   `json:"memory_mb"`
	DiskReadMB    int64   `json:"disk_read_mb"`
	DiskWriteMB   int64   `json:"disk_write_mb"`
	NetworkInMB   int64   `json:"network_in_mb"`
	NetworkOutMB  int64   `json:"network_out_mb"`
}

// LogEntry represents a log entry
type LogEntry struct {
	Timestamp time.Time `json:"timestamp"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
	Component string    `json:"component"`
	Context   map[string]interface{} `json:"context,omitempty"`
}

// Certificate represents a validation certificate
type Certificate struct {
	ID            string        `json:"id"`
	ConfigHash    string        `json:"config_hash"`
	Timestamp     time.Time     `json:"timestamp"`
	Expiry        time.Time     `json:"expiry"`
	Dimensions    *MultiDimReport `json:"dimensions"`
	ConfidenceScore float64     `json:"confidence_score"`
	AuditTrail    []ValidationStep `json:"audit_trail"`
	Issuer        string        `json:"issuer"`
	Signature     string        `json:"signature"`
}

// ValidationStep represents a step in the validation audit trail
type ValidationStep struct {
	ID          string    `json:"id"`
	Description string    `json:"description"`
	Result      string    `json:"result"`
	Timestamp   time.Time `json:"timestamp"`
	Duration    time.Duration `json:"duration"`
	Details     map[string]interface{} `json:"details,omitempty"`
}

// ValidationAgent defines the interface for systematic validation
type ValidationAgent interface {
	// ValidateConfiguration validates a Packer configuration
	ValidateConfiguration(ctx context.Context, config *PackerConfig) (*ValidationReport, error)
	
	// PerformMultiDimensionalCheck performs multi-dimensional validation on build results
	PerformMultiDimensionalCheck(ctx context.Context, build *BuildResult) (*MultiDimReport, error)
	
	// GenerateConfidenceScore generates a confidence score from build metrics
	GenerateConfidenceScore(metrics *BuildMetrics) float64
	
	// CreateValidationCertificate creates a validation certificate
	CreateValidationCertificate(ctx context.Context, report *ValidationReport) (*Certificate, error)
	
	// ValidateCertificate validates an existing certificate
	ValidateCertificate(ctx context.Context, cert *Certificate) (bool, error)
}