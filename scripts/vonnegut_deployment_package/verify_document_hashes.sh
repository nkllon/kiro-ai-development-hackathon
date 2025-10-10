#!/bin/bash
# RC1 Document Hash Verification Script
# Ensures document integrity and enables LLM coordination

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Expected hashes for RC1 documents
declare -A EXPECTED_HASHES=(
    ["RC1_MASTER_PLAN_SUMMARY.md"]="f9c223f8efd4a3f1465621b61791be2f"
    ["RC1_VISION_AND_STRATEGY.md"]="deac677ebe408d293bce95d784596673"
    ["RC1_DEVELOPMENT_PLAN.md"]="3b8f4aa28feec78fee72e1bc4359e3ce"
    ["RC1_DAG_FOUNDATION_STRATEGY.md"]="ec49d0385a335ed3e8907117cc141cd8"
    ["RC1_COMPLETE_DAG_ANALYSIS.md"]="830f57a10fe8fe9083e8e06cacb390be"
    ["RC1_DOCUMENT_MANAGEMENT_DAG_STRATEGY.md"]="24723a2b9ca2e39693d47a6e9d3ba1a1"
    ["RC1_MULTI_DIMENSIONAL_INDEXING_STRATEGY.md"]="37da96784cdfff1468d85cdb82a71d14"
    ["RC1_BEAST_MODE_GHOSTBUSTERS_PLANNING.md"]="3bca6bf9d3023ba90293b8ec251787d3"
    ["RC1_CONCURRENT_EXECUTION_STRATEGY.md"]="142df6bc63553738c73fe25d20dd236c"
    ["RC1_JSON_MODELS_COMPREHENSIVE.md"]="fdae3a8a78bb66b895c682fef866c2f5"
    ["RC1_LLM_ENTRY_POINT.md"]="6aa2c8706759ada6c47b73de54a415c8"
    ["RC1_LLM_ENTRY_POINT_HASHED.md"]="0e245c8c8d0708ea6f87a41547992e1a"
    ["RC1_DOCUMENTATION_INDEX.md"]="3072035c516037b5e69bc879b687e083"
    ["RC1_NAVIGATION_MAP.md"]="f52ee38ebdd78a368e64d2e774aebca1"
    ["RC1_README_INTEGRATION.md"]="18ec0d55fd5dbf2665391bdc1f3a3068"
    ["RC1_DOCUMENT_REGISTRY.md"]="a3c1985833dcc5ed589025072a4362de"
)

# Expected hashes for model documents
declare -A MODEL_HASHES=(
    ["models/as_is_static_structure.json"]="92232707b28553236dcf890a3d862d11"
    ["models/to_be_static_structure.json"]="c442fa476f8f7bdd2a2f73e7c425dd1e"
    ["models/multi_dimensional_index.json"]="b4a944c6d61741b9d80b40c09571fe10"
    ["models/migration_activity_models.json"]="ffeadd7783dfa414ef64d6271456fc0b"
    ["models/initial_execution_activity_models.json"]="2dde14b54c4a008fd38c9a2d7610bee9"
)

# Expected hashes for ontology documents
declare -A ONTOLOGY_HASHES=(
    ["ontology/documentation_system_ontology.ttl"]="73343c6f1fb87cc8591a8c800e623c29"
    ["ontology/ontology_summary.md"]="e675fb1d63b5176a8f13edf02d60fadc"
)

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

# Function to verify document group
verify_group() {
    local group_name="$1"
    local -n hash_array="$2"
    local error_count=0
    
    echo -e "${BLUE}📋 Verifying $group_name${NC}"
    echo "----------------------------------------"
    
    for file_path in "${!hash_array[@]}"; do
        local document_name
        document_name=$(basename "$file_path")
        
        if ! verify_document "$file_path" "${hash_array[$file_path]}" "$document_name"; then
            ((error_count++))
        fi
        echo
    done
    
    if [[ $error_count -eq 0 ]]; then
        echo -e "${GREEN}✅ All $group_name documents verified successfully${NC}"
    else
        echo -e "${RED}❌ $error_count $group_name documents failed verification${NC}"
    fi
    
    echo
    return $error_count
}

# Function to find document by hash
find_by_hash() {
    local target_hash="$1"
    echo -e "${BLUE}🔍 Searching for document with hash: $target_hash${NC}"
    echo "----------------------------------------"
    
    local found=false
    
    # Search RC1 documents
    for file in RC1_*.md; do
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
    for file in RC1_*.md; do
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
            
            verify_group "RC1" EXPECTED_HASHES
            ((total_errors += $?))
            
            verify_group "Model" MODEL_HASHES
            ((total_errors += $?))
            
            verify_group "Ontology" ONTOLOGY_HASHES
            ((total_errors += $?))
            
            echo "========================================"
            if [[ $total_errors -eq 0 ]]; then
                echo -e "${GREEN}🎉 ALL DOCUMENTS VERIFIED SUCCESSFULLY!${NC}"
                echo -e "${GREEN}   Total documents: $((${#EXPECTED_HASHES[@]} + ${#MODEL_HASHES[@]} + ${#ONTOLOGY_HASHES[@]}))${NC}"
            else
                echo -e "${RED}❌ VERIFICATION FAILED${NC}"
                echo -e "${RED}   Total errors: $total_errors${NC}"
                exit 1
            fi
            ;;
        "verify-rc1")
            verify_group "RC1" EXPECTED_HASHES
            ;;
        "verify-models")
            verify_group "Model" MODEL_HASHES
            ;;
        "verify-ontology")
            verify_group "Ontology" ONTOLOGY_HASHES
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
