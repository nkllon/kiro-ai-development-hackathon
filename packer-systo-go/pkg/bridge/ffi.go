// Package bridge provides FFI (Foreign Function Interface) capabilities
// for Go-Python interoperability in the Packer Systo ecosystem
package bridge

/*
#include <stdlib.h>
#include <string.h>

// C bridge functions for Python FFI
typedef struct {
    char* data;
    int length;
    int error_code;
    char* error_message;
} BridgeResult;

// Free memory allocated by bridge functions
void free_bridge_result(BridgeResult* result) {
    if (result->data) {
        free(result->data);
        result->data = NULL;
    }
    if (result->error_message) {
        free(result->error_message);
        result->error_message = NULL;
    }
}
*/
import "C"

import (
	"context"
	"encoding/json"
	"fmt"
	"unsafe"

	"github.com/your-org/packer-systo-go/pkg/interfaces"
)

// BridgeAPI provides the main API for Python-Go bridge communication
type BridgeAPI struct {
	delusionDetector interfaces.DelusionDetector
	recoveryEngine   interfaces.RecoveryEngine
	validationAgent  interfaces.ValidationAgent
}

// NewBridgeAPI creates a new bridge API instance
func NewBridgeAPI(
	detector interfaces.DelusionDetector,
	recovery interfaces.RecoveryEngine,
	validator interfaces.ValidationAgent,
) *BridgeAPI {
	return &BridgeAPI{
		delusionDetector: detector,
		recoveryEngine:   recovery,
		validationAgent:  validator,
	}
}

// createBridgeResult creates a C bridge result from Go data
func createBridgeResult(data interface{}, err error) *C.BridgeResult {
	result := (*C.BridgeResult)(C.malloc(C.sizeof_BridgeResult))
	
	if err != nil {
		result.error_code = C.int(1)
		errMsg := C.CString(err.Error())
		result.error_message = errMsg
		result.data = nil
		result.length = 0
		return result
	}
	
	jsonData, jsonErr := json.Marshal(data)
	if jsonErr != nil {
		result.error_code = C.int(2)
		errMsg := C.CString(fmt.Sprintf("JSON marshal error: %v", jsonErr))
		result.error_message = errMsg
		result.data = nil
		result.length = 0
		return result
	}
	
	result.error_code = 0
	result.error_message = nil
	result.data = C.CString(string(jsonData))
	result.length = C.int(len(jsonData))
	
	return result
}

// parsePackerConfig parses JSON string to PackerConfig
func parsePackerConfig(jsonStr string) (*interfaces.PackerConfig, error) {
	var config interfaces.PackerConfig
	err := json.Unmarshal([]byte(jsonStr), &config)
	return &config, err
}

//export analyze_configuration
func analyze_configuration(configJSON *C.char) *C.BridgeResult {
	goConfigJSON := C.GoString(configJSON)
	
	config, err := parsePackerConfig(goConfigJSON)
	if err != nil {
		return createBridgeResult(nil, fmt.Errorf("failed to parse config: %v", err))
	}
	
	// This would be injected by the actual implementation
	// For now, we create a mock bridge API
	bridgeAPI := &BridgeAPI{}
	if bridgeAPI.delusionDetector == nil {
		return createBridgeResult(nil, fmt.Errorf("delusion detector not initialized"))
	}
	
	ctx := context.Background()
	report, err := bridgeAPI.delusionDetector.AnalyzeConfiguration(ctx, config)
	
	return createBridgeResult(report, err)
}

//export detect_patterns
func detect_patterns(hclContent *C.char) *C.BridgeResult {
	goHCL := C.GoString(hclContent)
	
	bridgeAPI := &BridgeAPI{}
	if bridgeAPI.delusionDetector == nil {
		return createBridgeResult(nil, fmt.Errorf("delusion detector not initialized"))
	}
	
	ctx := context.Background()
	patterns, err := bridgeAPI.delusionDetector.DetectPatterns(ctx, goHCL)
	
	return createBridgeResult(patterns, err)
}

//export diagnose_failure
func diagnose_failure(buildLog *C.char, configJSON *C.char) *C.BridgeResult {
	goBuildLog := C.GoString(buildLog)
	goConfigJSON := C.GoString(configJSON)
	
	config, err := parsePackerConfig(goConfigJSON)
	if err != nil {
		return createBridgeResult(nil, fmt.Errorf("failed to parse config: %v", err))
	}
	
	bridgeAPI := &BridgeAPI{}
	if bridgeAPI.recoveryEngine == nil {
		return createBridgeResult(nil, fmt.Errorf("recovery engine not initialized"))
	}
	
	ctx := context.Background()
	diagnosis, err := bridgeAPI.recoveryEngine.DiagnoseFailure(ctx, goBuildLog, config)
	
	return createBridgeResult(diagnosis, err)
}

//export validate_configuration
func validate_configuration(configJSON *C.char) *C.BridgeResult {
	goConfigJSON := C.GoString(configJSON)
	
	config, err := parsePackerConfig(goConfigJSON)
	if err != nil {
		return createBridgeResult(nil, fmt.Errorf("failed to parse config: %v", err))
	}
	
	bridgeAPI := &BridgeAPI{}
	if bridgeAPI.validationAgent == nil {
		return createBridgeResult(nil, fmt.Errorf("validation agent not initialized"))
	}
	
	ctx := context.Background()
	report, err := bridgeAPI.validationAgent.ValidateConfiguration(ctx, config)
	
	return createBridgeResult(report, err)
}

//export free_result
func free_result(result *C.BridgeResult) {
	if result != nil {
		C.free_bridge_result(result)
		C.free(unsafe.Pointer(result))
	}
}

// SetGlobalBridgeAPI sets the global bridge API instance for FFI calls
// This should be called during initialization
var globalBridgeAPI *BridgeAPI

func SetGlobalBridgeAPI(api *BridgeAPI) {
	globalBridgeAPI = api
}

// GetGlobalBridgeAPI returns the global bridge API instance
func GetGlobalBridgeAPI() *BridgeAPI {
	return globalBridgeAPI
}

// BridgeConfig represents configuration for the bridge
type BridgeConfig struct {
	LogLevel    string `json:"log_level"`
	Timeout     int    `json:"timeout_seconds"`
	MaxRetries  int    `json:"max_retries"`
	EnableCache bool   `json:"enable_cache"`
}

// InitializeBridge initializes the Go-Python bridge with the given configuration
//export initialize_bridge
func initialize_bridge(configJSON *C.char) *C.BridgeResult {
	goConfigJSON := C.GoString(configJSON)
	
	var config BridgeConfig
	err := json.Unmarshal([]byte(goConfigJSON), &config)
	if err != nil {
		return createBridgeResult(nil, fmt.Errorf("failed to parse bridge config: %v", err))
	}
	
	// Initialize bridge with configuration
	// This would set up logging, timeouts, etc.
	
	result := map[string]interface{}{
		"status":  "initialized",
		"config":  config,
		"version": "1.0.0",
	}
	
	return createBridgeResult(result, nil)
}

// GetBridgeInfo returns information about the bridge
//export get_bridge_info
func get_bridge_info() *C.BridgeResult {
	info := map[string]interface{}{
		"version":     "1.0.0",
		"go_version":  "1.21",
		"features":    []string{"delusion_detection", "recovery_engine", "validation"},
		"status":      "ready",
		"initialized": globalBridgeAPI != nil,
	}
	
	return createBridgeResult(info, nil)
}

func main() {
	// Required for CGO builds
}