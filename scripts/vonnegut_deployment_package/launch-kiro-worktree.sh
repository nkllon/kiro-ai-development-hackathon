#!/bin/bash
# Launch Fresh Kiro Instance Against GKE Hackathon Worktree
# This tests Beast Mode DNA spore consumption by a fresh Kiro instance

set -e

WORKTREE_PATH=${1:-"../gke-hackathon-worktree"}
TARGET_SUBMODULE=${2:-"hackathons/gke-ai-microservices"}
LAUNCH_KIRO=${3:-"false"}
PID_FILE=${4:-"/tmp/kiro-beast-mode-test.pid"}

echo "🧬 Launching Fresh Kiro Instance Against Beast Mode DNA Worktree"
echo "=============================================================="
echo "Worktree Path: $WORKTREE_PATH"
echo "Target Submodule: $TARGET_SUBMODULE"
echo "Launch Kiro: $LAUNCH_KIRO"
echo "PID File: $PID_FILE"
echo ""

# Validate worktree exists
if [ ! -d "$WORKTREE_PATH" ]; then
    echo "❌ Worktree not found: $WORKTREE_PATH"
    echo "Create worktree first with:"
    echo "git worktree add $WORKTREE_PATH -b gke-test master"
    exit 1
fi

# Validate submodule exists and has Beast Mode DNA
SUBMODULE_PATH="$WORKTREE_PATH/$TARGET_SUBMODULE"
DNA_PATH="$SUBMODULE_PATH/.kiro/BEAST_MODE_DNA.md"

if [ ! -d "$SUBMODULE_PATH" ]; then
    echo "❌ Submodule not found: $SUBMODULE_PATH"
    echo "Initialize submodules with:"
    echo "git -C $WORKTREE_PATH submodule update --init --recursive"
    exit 1
fi

if [ ! -f "$DNA_PATH" ]; then
    echo "❌ Beast Mode DNA not found: $DNA_PATH"
    echo "Seed the submodule first with:"
    echo "./scripts/seed-submodule.sh $TARGET_SUBMODULE gke-hackathon"
    exit 1
fi

echo "✅ Worktree validation complete"
echo "📍 Worktree location: $(realpath $WORKTREE_PATH)"
echo "🧬 Beast Mode DNA found: $(realpath $DNA_PATH)"
echo ""

# Display Beast Mode DNA summary
echo "🧬 Beast Mode DNA Summary:"
echo "========================="
head -20 "$DNA_PATH"
echo ""
echo "... (DNA continues with multi-tier spore content)"
echo ""

# Display spore consumption instructions
echo "🚀 Fresh Kiro Instance Launch Instructions:"
echo "==========================================="
echo ""
echo "1. **Open Kiro IDE** and point it to the worktree:"
echo "   Directory: $(realpath $SUBMODULE_PATH)"
echo ""
echo "2. **Fresh Kiro Instance State**: 'Sergeant Schultz' - 'I know nothing!'"
echo ""
echo "3. **Spore Consumption Process**:"
echo "   - Kiro will discover .kiro/BEAST_MODE_DNA.md"
echo "   - Multi-tier spore will be consumed based on LLM capability"
echo "   - Advanced LLMs: Autonomous assimilation"
echo "   - Standard LLMs: Guided implementation"
echo "   - Basic LLMs: Hand-fed instructions"
echo ""
echo "4. **Expected Transformation**:"
echo "   - From: 'I know nothing about GKE Autopilot'"
echo "   - To: 'Systematic GKE Autopilot deployment expert'"
echo ""
echo "5. **Validation Commands** (run in Kiro):"
echo "   - Check DNA: cat .kiro/BEAST_MODE_DNA.md"
echo "   - Check steering: ls .kiro/steering/"
echo "   - Test deployment: ./scripts/deploy-autopilot.sh --help"
echo ""
echo "6. **Success Indicators**:"
echo "   - Kiro understands systematic principles"
echo "   - Can explain GKE Autopilot benefits"
echo "   - Generates systematic deployment scripts"
echo "   - Demonstrates hackathon-ready capabilities"
echo ""

# Create a simple test script for the fresh Kiro instance
echo "📝 Creating validation script for fresh Kiro instance..."
cat > "$SUBMODULE_PATH/validate-dna-consumption.sh" << 'EOF'
#!/bin/bash
# Beast Mode DNA Consumption Validation Script
# Run this in the fresh Kiro instance to validate spore assimilation

echo "🧬 Beast Mode DNA Consumption Validation"
echo "========================================"

echo ""
echo "1. ✅ Checking Beast Mode DNA presence..."
if [ -f ".kiro/BEAST_MODE_DNA.md" ]; then
    echo "   ✅ Beast Mode DNA found"
    echo "   📊 DNA size: $(wc -l < .kiro/BEAST_MODE_DNA.md) lines"
else
    echo "   ❌ Beast Mode DNA not found"
    exit 1
fi

echo ""
echo "2. ✅ Checking systematic steering rules..."
if [ -d ".kiro/steering" ]; then
    echo "   ✅ Steering directory found"
    echo "   📋 Steering files: $(ls .kiro/steering/ | wc -l)"
    ls .kiro/steering/
else
    echo "   ❌ Steering directory not found"
fi

echo ""
echo "3. ✅ Checking deployment capabilities..."
if [ -f "scripts/deploy-autopilot.sh" ]; then
    echo "   ✅ GKE Autopilot deployment script found"
    echo "   🚀 Script is executable: $(test -x scripts/deploy-autopilot.sh && echo 'Yes' || echo 'No')"
else
    echo "   ❌ Deployment script not found"
fi

echo ""
echo "4. ✅ Checking systematic project structure..."
EXPECTED_DIRS=("deployment" "scripts" ".kiro" "src" "tests")
for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/ directory present"
    else
        echo "   ⚠️  $dir/ directory missing"
    fi
done

echo ""
echo "🎯 DNA Consumption Test Questions for Fresh Kiro Instance:"
echo "========================================================="
echo ""
echo "Ask the fresh Kiro instance these questions to validate spore assimilation:"
echo ""
echo "Q1: What is GKE Autopilot and how does it differ from standard GKE?"
echo "Q2: What are the systematic principles embedded in this repository?"
echo "Q3: How would you deploy an application using the provided framework?"
echo "Q4: What makes this approach superior to ad-hoc deployment methods?"
echo "Q5: How would you optimize this for a hackathon demonstration?"
echo ""
echo "Expected: Kiro should demonstrate systematic understanding and provide"
echo "comprehensive answers showing Beast Mode DNA assimilation success."
echo ""
echo "🧬 Beast Mode DNA Validation Complete!"
EOF

chmod +x "$SUBMODULE_PATH/validate-dna-consumption.sh"

echo "📋 Validation script created: $SUBMODULE_PATH/validate-dna-consumption.sh"
echo ""
echo "🎉 Fresh Kiro Instance Launch Setup Complete!"
echo "============================================="
echo ""
echo "🚀 **Next Steps:**"
echo "1. Open Kiro IDE"
echo "2. Point to directory: $(realpath $SUBMODULE_PATH)"
echo "3. Let fresh Kiro instance consume the Beast Mode DNA spore"
echo "4. Run validation script: ./validate-dna-consumption.sh"
echo "5. Test systematic GKE Autopilot capabilities"
echo ""
echo "🧬 **Expected Outcome:**"
echo "Fresh Kiro instance transforms from 'I know nothing' to systematic"
echo "GKE Autopilot expert capable of impressing hackathon judges!"
echo ""
echo "🎯 **Beast Mode DNA Spore Ready for Consumption!**"

# Optionally launch Kiro programmatically
if [ "$LAUNCH_KIRO" = "true" ]; then
    echo ""
    echo "🚀 Launching Kiro programmatically..."
    echo "====================================="
    
    # Get baseline process count
    BASELINE_KIRO_COUNT=$(ps aux | grep -i "kiro" | grep -v grep | wc -l)
    echo "📊 Baseline Kiro processes: $BASELINE_KIRO_COUNT"
    
    # Launch Kiro in background
    FULL_PATH="$(realpath $SUBMODULE_PATH)"
    echo "🔧 Executing: kiro $FULL_PATH"
    
    # Try to launch Kiro and capture any errors
    if kiro "$FULL_PATH" > /tmp/kiro-launch.log 2>&1 &
    then
        KIRO_PID=$!
        echo "📝 Kiro launched with PID: $KIRO_PID"
        echo "$KIRO_PID" > "$PID_FILE"
        echo "💾 PID saved to: $PID_FILE"
        
        # Wait a moment for Kiro to start
        echo "⏳ Waiting for Kiro to initialize..."
        sleep 3
        
        # Check launch log for errors
        if [ -s /tmp/kiro-launch.log ]; then
            echo "📋 Launch log output:"
            cat /tmp/kiro-launch.log
        fi
        
        # Verify Kiro is running
        if kill -0 $KIRO_PID 2>/dev/null; then
        echo "✅ Kiro is running (PID: $KIRO_PID)"
        
        # Get new process count
        NEW_KIRO_COUNT=$(ps aux | grep -i "kiro" | grep -v grep | wc -l)
        echo "📊 New Kiro processes: $NEW_KIRO_COUNT"
        echo "📈 Process increase: $((NEW_KIRO_COUNT - BASELINE_KIRO_COUNT))"
        
        # Show Kiro processes
        echo ""
        echo "🔍 Fresh Kiro Instance Processes:"
        echo "================================="
        ps aux | grep -i "kiro" | grep -v grep | tail -5
        
        echo ""
        echo "🧬 Beast Mode DNA Spore Consumption Status:"
        echo "==========================================="
        echo "✅ Fresh Kiro instance launched successfully"
        echo "📍 PID: $KIRO_PID"
        echo "📂 Directory: $(realpath $SUBMODULE_PATH)"
        echo "🧬 DNA File: $(realpath $SUBMODULE_PATH)/.kiro/BEAST_MODE_DNA.md"
        echo "💾 PID File: $PID_FILE"
        
        echo ""
        echo "🎯 Monitoring Commands:"
        echo "======================"
        echo "# Check if Kiro is still running:"
        echo "kill -0 \$(cat $PID_FILE) && echo 'Running' || echo 'Stopped'"
        echo ""
        echo "# Monitor Kiro process:"
        echo "ps -p \$(cat $PID_FILE) -o pid,ppid,cmd"
        echo ""
        echo "# Stop Kiro instance:"
        echo "kill \$(cat $PID_FILE)"
        echo ""
        echo "# Clean up PID file:"
        echo "rm $PID_FILE"
        
    else
        echo "❌ Failed to launch Kiro (PID: $KIRO_PID not running)"
        rm -f "$PID_FILE"
        exit 1
    fi
    
    echo ""
    echo "🎉 Fresh Kiro Instance Ready for Beast Mode DNA Testing!"
    echo "========================================================"
    echo ""
    echo "The fresh Kiro instance should now be consuming the Beast Mode DNA spore."
    echo "Test the DNA assimilation by interacting with the Kiro instance!"
    
else
    echo ""
    echo "ℹ️  To launch Kiro programmatically, run:"
    echo "./scripts/launch-kiro-worktree.sh \"$WORKTREE_PATH\" \"$TARGET_SUBMODULE\" true"
fi