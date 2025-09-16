#!/bin/bash
# RC1 Document Hash Verification Script (Simplified)
# Ensures document integrity and enables LLM coordination

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print header
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  RC1 Document Hash Verification${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

# Function to verify single document
verify_document() {
    local file_path="$1"
    local expected_hash="$2"
    local document_name="$3"
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}❌ MISSING: $document_name${NC} (${file_path})"
        return 1
    fi
    
    local actual_hash
    actual_hash=$(md5sum "$file_path" | cut -d' ' -f1)
    
    if [[ "$actual_hash" == "$expected_hash" ]]; then
        echo -e "${GREEN}✅ VERIFIED: $document_name${NC} (${file_path})"
        echo -e "   Hash: ${GREEN}$actual_hash${NC}"
        return 0
    else
        echo -e "${RED}❌ MISMATCH: $document_name${NC} (${file_path})"
        echo -e "   Expected: ${YELLOW}$expected_hash${NC}"
        echo -e "   Actual:   ${RED}$actual_hash${NC}"
        return 1
    fi
}

# Function to find document by hash
find_by_hash() {
    local target_hash="$1"
    echo -e "${BLUE}🔍 Searching for document with hash: $target_hash${NC}"
    echo "----------------------------------------"
    
    local found=false
    
    # Search RC1 documents in migrated locations
    find . -name "RC1_*.md" | while read -r file; do
        if [[ -f "$file" ]]; then
            local hash
            hash=$(md5sum "$file" | cut -d' ' -f1)
            if [[ "$hash" == "$target_hash" ]]; then
                echo -e "${GREEN}✅ Found: $file${NC}"
                echo -e "   Path: $file"
                echo -e "   Hash: $hash"
                found=true
            fi
        fi
    done
    
    # Search model documents
    if [[ -d "models" ]]; then
        for file in models/*.json; do
            if [[ -f "$file" ]]; then
                local hash
                hash=$(md5sum "$file" | cut -d' ' -f1)
                if [[ "$hash" == "$target_hash" ]]; then
                    echo -e "${GREEN}✅ Found: $file${NC}"
                    echo -e "   Path: $file"
                    echo -e "   Hash: $hash"
                    found=true
                fi
            fi
        done
    fi
    
    # Search ontology documents
    if [[ -d "ontology" ]]; then
        for file in ontology/*.ttl ontology/*.md; do
            if [[ -f "$file" ]]; then
                local hash
                hash=$(md5sum "$file" | cut -d' ' -f1)
                if [[ "$hash" == "$target_hash" ]]; then
                    echo -e "${GREEN}✅ Found: $file${NC}"
                    echo -e "   Path: $file"
                    echo -e "   Hash: $hash"
                    found=true
                fi
            fi
        done
    fi
    
    if [[ "$found" == false ]]; then
        echo -e "${RED}❌ No document found with hash: $target_hash${NC}"
    fi
    
    echo
}

# Function to list all documents with hashes
list_all_documents() {
    echo -e "${BLUE}📚 All RC1 Documents with Hashes${NC}"
    echo "========================================"
    echo
    
    echo -e "${YELLOW}RC1 Documents:${NC}"
    find . -name "RC1_*.md" | while read -r file; do
        if [[ -f "$file" ]]; then
            local hash
            hash=$(md5sum "$file" | cut -d' ' -f1)
            echo -e "  ${GREEN}$hash${NC}  $file"
        fi
    done
    echo
    
    if [[ -d "models" ]]; then
        echo -e "${YELLOW}Model Documents:${NC}"
        for file in models/*.json; do
            if [[ -f "$file" ]]; then
                local hash
                hash=$(md5sum "$file" | cut -d' ' -f1)
                echo -e "  ${GREEN}$hash${NC}  $file"
            fi
        done
        echo
    fi
    
    if [[ -d "ontology" ]]; then
        echo -e "${YELLOW}Ontology Documents:${NC}"
        for file in ontology/*.ttl ontology/*.md; do
            if [[ -f "$file" ]]; then
                local hash
                hash=$(md5sum "$file" | cut -d' ' -f1)
                echo -e "  ${GREEN}$hash${NC}  $file"
            fi
        done
        echo
    fi
}

# Function to verify all RC1 documents
verify_rc1_documents() {
    echo -e "${BLUE}📋 Verifying RC1 Documents${NC}"
    echo "----------------------------------------"
    
    local error_count=0
    
    # Verify each RC1 document in migrated locations
    verify_document "docs/rc1/planning/RC1_MASTER_PLAN_SUMMARY.md" "f9c223f8efd4a3f1465621b61791be2f" "RC1 Master Plan Summary" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_VISION_AND_STRATEGY.md" "deac677ebe408d293bce95d784596673" "RC1 Vision and Strategy" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_DEVELOPMENT_PLAN.md" "3b8f4aa28feec78fee72e1bc4359e3ce" "RC1 Development Plan" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_DAG_FOUNDATION_STRATEGY.md" "ec49d0385a335ed3e8907117cc141cd8" "RC1 DAG Foundation Strategy" || ((error_count++))
    verify_document "docs/rc1/analysis/RC1_COMPLETE_DAG_ANALYSIS.md" "830f57a10fe8fe9083e8e06cacb390be" "RC1 Complete DAG Analysis" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_DOCUMENT_MANAGEMENT_DAG_STRATEGY.md" "24723a2b9ca2e39693d47a6e9d3ba1a1" "RC1 Document Management DAG Strategy" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_MULTI_DIMENSIONAL_INDEXING_STRATEGY.md" "37da96784cdfff1468d85cdb82a71d14" "RC1 Multi-Dimensional Indexing Strategy" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_BEAST_MODE_GHOSTBUSTERS_PLANNING.md" "3bca6bf9d3023ba90293b8ec251787d3" "RC1 Beast Mode Ghostbusters Planning" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_CONCURRENT_EXECUTION_STRATEGY.md" "142df6bc63553738c73fe25d20dd236c" "RC1 Concurrent Execution Strategy" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_JSON_MODELS_COMPREHENSIVE.md" "fdae3a8a78bb66b895c682fef866c2f5" "RC1 JSON Models Comprehensive" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_LLM_ENTRY_POINT.md" "6aa2c8706759ada6c47b73de54a415c8" "RC1 LLM Entry Point" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_LLM_ENTRY_POINT_HASHED.md" "0e245c8c8d0708ea6f87a41547992e1a" "RC1 LLM Entry Point Hashed" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_DOCUMENTATION_INDEX.md" "3072035c516037b5e69bc879b687e083" "RC1 Documentation Index" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_NAVIGATION_MAP.md" "f52ee38ebdd78a368e64d2e774aebca1" "RC1 Navigation Map" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_README_INTEGRATION.md" "18ec0d55fd5dbf2665391bdc1f3a3068" "RC1 README Integration" || ((error_count++))
    verify_document "docs/rc1/planning/RC1_DOCUMENT_REGISTRY.md" "a3c1985833dcc5ed589025072a4362de" "RC1 Document Registry" || ((error_count++))
    
    echo
    if [[ $error_count -eq 0 ]]; then
        echo -e "${GREEN}✅ All RC1 documents verified successfully${NC}"
    else
        echo -e "${RED}❌ $error_count RC1 documents failed verification${NC}"
    fi
    
    echo
    return $error_count
}

# Function to verify model documents
verify_model_documents() {
    echo -e "${BLUE}📊 Verifying Model Documents${NC}"
    echo "----------------------------------------"
    
    local error_count=0
    
    if [[ -d "models" ]]; then
        verify_document "models/as_is_static_structure.json" "92232707b28553236dcf890a3d862d11" "As-Is Static Structure" || ((error_count++))
        verify_document "models/to_be_static_structure.json" "c442fa476f8f7bdd2a2f73e7c425dd1e" "To-Be Static Structure" || ((error_count++))
        verify_document "models/multi_dimensional_index.json" "b4a944c6d61741b9d80b40c09571fe10" "Multi-Dimensional Index" || ((error_count++))
        verify_document "models/migration_activity_models.json" "ffeadd7783dfa414ef64d6271456fc0b" "Migration Activity Models" || ((error_count++))
        verify_document "models/initial_execution_activity_models.json" "2dde14b54c4a008fd38c9a2d7610bee9" "Initial Execution Activity Models" || ((error_count++))
    else
        echo -e "${RED}❌ Models directory not found${NC}"
        error_count=5
    fi
    
    echo
    if [[ $error_count -eq 0 ]]; then
        echo -e "${GREEN}✅ All model documents verified successfully${NC}"
    else
        echo -e "${RED}❌ $error_count model documents failed verification${NC}"
    fi
    
    echo
    return $error_count
}

# Function to verify ontology documents
verify_ontology_documents() {
    echo -e "${BLUE}🔗 Verifying Ontology Documents${NC}"
    echo "----------------------------------------"
    
    local error_count=0
    
    if [[ -d "ontology" ]]; then
        verify_document "ontology/documentation_system_ontology.ttl" "73343c6f1fb87cc8591a8c800e623c29" "Documentation System Ontology" || ((error_count++))
        verify_document "ontology/ontology_summary.md" "e675fb1d63b5176a8f13edf02d60fadc" "Ontology Summary" || ((error_count++))
    else
        echo -e "${RED}❌ Ontology directory not found${NC}"
        error_count=2
    fi
    
    echo
    if [[ $error_count -eq 0 ]]; then
        echo -e "${GREEN}✅ All ontology documents verified successfully${NC}"
    else
        echo -e "${RED}❌ $error_count ontology documents failed verification${NC}"
    fi
    
    echo
    return $error_count
}

# Function to show help
show_help() {
    echo "RC1 Document Hash Verification Script"
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  verify-all     Verify all documents against expected hashes"
    echo "  verify-rc1     Verify only RC1 documents"
    echo "  verify-models  Verify only model documents"
    echo "  verify-ontology Verify only ontology documents"
    echo "  find HASH      Find document by hash"
    echo "  list           List all documents with their hashes"
    echo "  help           Show this help message"
    echo
    echo "Examples:"
    echo "  $0 verify-all"
    echo "  $0 find f9c223f8efd4a3f1465621b61791be2f"
    echo "  $0 list"
}

# Main function
main() {
    local command="${1:-verify-all}"
    
    print_header
    
    case "$command" in
        "verify-all")
            local total_errors=0
            
            verify_rc1_documents
            ((total_errors += $?))
            
            verify_model_documents
            ((total_errors += $?))
            
            verify_ontology_documents
            ((total_errors += $?))
            
            echo "========================================"
            if [[ $total_errors -eq 0 ]]; then
                echo -e "${GREEN}🎉 ALL DOCUMENTS VERIFIED SUCCESSFULLY!${NC}"
                echo -e "${GREEN}   Total documents: 23${NC}"
            else
                echo -e "${RED}❌ VERIFICATION FAILED${NC}"
                echo -e "${RED}   Total errors: $total_errors${NC}"
                exit 1
            fi
            ;;
        "verify-rc1")
            verify_rc1_documents
            ;;
        "verify-models")
            verify_model_documents
            ;;
        "verify-ontology")
            verify_ontology_documents
            ;;
        "find")
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ Error: Hash required for find command${NC}"
                echo "Usage: $0 find HASH"
                exit 1
            fi
            find_by_hash "$2"
            ;;
        "list")
            list_all_documents
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Error: Unknown command '$command'${NC}"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
