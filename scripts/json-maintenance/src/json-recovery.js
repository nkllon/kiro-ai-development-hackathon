#!/usr/bin/env node

/**
 * 🚨 Cursor IDE Systemic Issue - JSON Recovery Script
 * 
 * This script safely recovers the simple changes that were lost when
 * the complex JSON structure corrupted the project_model_registry.json
 * 
 * RECOVERY STRATEGY: Only update existing arrays/objects, no new sections
 */

const fs = require('fs-extra');
const path = require('path');

// Configuration
const PROJECT_ROOT = path.resolve(__dirname, '../../..');
const MODEL_FILE = path.join(PROJECT_ROOT, 'project_model_registry.json');


const BACKUP_FILE = path.join(PROJECT_ROOT, 'project_model_registry.json.backup');

// Recovery data from the stash analysis
const RECOVERY_DATA = {
  // Domain additions to existing arrays
  domains: {
    demo_tools: {
      domains: ['cursor_ide_systemic_issue_mitigation']
    },
    demo_infrastructure: {
      domains: ['cursor_ide_systemic_issue_mitigation']
    },
    cursor_rules: {
      domains: ['cursor_ide_systemic_issue_mitigation'],
      emoji_prefixes: {
        'cursor_ide_systemic_issue_mitigation': '🚨'
      }
    }
  },
  
  // Known issues update
  known_issues: [
    '🚨 CRITICAL: Cursor IDE systemic issue - AI assistants may not scan .cursor/rules and docs/ before work, leading to incomplete context and potential errors'
  ],
  
  // Backlog item
  backlogged: [
    {
      requirement: 'Fix 131 MyPy type errors',
      status: 'backlogged',
      domain: 'python_quality',
      priority: 'high',
      estimated_effort: '1-2 weeks',
      dependencies: [
        'src/**/*.py',
        'tests/**/*.py'
      ],
      description: 'Resolve 131 MyPy type errors currently affecting code quality and maintainability',
      acceptance_criteria: [
        'All MyPy type errors resolved',
        'Type annotations properly implemented',
        'Code quality score improved',
        'No new type errors introduced'
      ],
      risk_assessment: {
        risk_level: 'HIGH',
        impact: 'Affects code quality, maintainability, and development velocity',
        mitigation: 'Systematic resolution with pre-commit hooks and CI/CD integration'
      },
      date_added: '2025-08-19'
    }
  ],
  
  // Requirements traceability
  requirements_traceability: [
    {
      requirement: 'Cursor IDE systemic issue mitigation',
      domain: 'cursor_ide_systemic_issue_mitigation',
      implementation: 'Makefile status reminders, risk management framework, multi-agent validation',
      test: 'test_requirement_cursor_ide_mitigation'
    }
  ]
};

/**
 * Create backup of current model file
 */
function createBackup() {
  try {
    fs.copyFileSync(MODEL_FILE, BACKUP_FILE);
    console.log('✅ Backup created:', BACKUP_FILE);
    return true;
  } catch (error) {
    console.error('❌ Failed to create backup:', error.message);
    return false;
  }
}

/**
 * Load and parse the model file
 */
function loadModel() {
  try {
    const content = fs.readFileSync(MODEL_FILE, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.error('❌ Failed to load model:', error.message);
    return null;
  }
}

/**
 * Save the model file with validation
 */
function saveModel(model) {
  try {
    // Validate JSON before saving
    JSON.stringify(model);
    
    // Save with pretty formatting
    fs.writeFileSync(MODEL_FILE, JSON.stringify(model, null, 2));
    console.log('✅ Model saved successfully');
    return true;
  } catch (error) {
    console.error('❌ Failed to save model:', error.message);
    return false;
  }
}

/**
 * Validate JSON syntax
 */
function validateJSON() {
  try {
    const content = fs.readFileSync(MODEL_FILE, 'utf8');
    JSON.parse(content);
    console.log('✅ JSON syntax is valid');
    return true;
  } catch (error) {
    console.error('❌ JSON syntax error:', error.message);
    return false;
  }
}

/**
 * Apply domain additions
 */
function applyDomainAdditions(model) {
  console.log('🔧 Applying domain additions...');
  
  // Add to demo_tools domains
  if (model.domains.demo_tools && model.domains.demo_tools.domains) {
    if (!model.domains.demo_tools.domains.includes('cursor_ide_systemic_issue_mitigation')) {
      model.domains.demo_tools.domains.push('cursor_ide_systemic_issue_mitigation');
      console.log('  ✅ Added to demo_tools domains');
    }
  }
  
  // Add to demo_infrastructure domains
  if (model.domains.demo_infrastructure && model.domains.demo_infrastructure.domains) {
    if (!model.domains.demo_infrastructure.domains.includes('cursor_ide_systemic_issue_mitigation')) {
      model.domains.demo_infrastructure.domains.push('cursor_ide_systemic_issue_mitigation');
      console.log('  ✅ Added to demo_infrastructure domains');
    }
  }
  
  // Add to cursor_rules domains and emoji_prefixes
  if (model.domains.cursor_rules) {
    if (model.domains.cursor_rules.domains && !model.domains.cursor_rules.domains.includes('cursor_ide_systemic_issue_mitigation')) {
      model.domains.cursor_rules.domains.push('cursor_ide_systemic_issue_mitigation');
      console.log('  ✅ Added to cursor_rules domains');
    }
    
    if (model.domains.cursor_rules.emoji_prefixes) {
      model.domains.cursor_rules.emoji_prefixes['cursor_ide_systemic_issue_mitigation'] = '🚨';
      console.log('  ✅ Added emoji prefix 🚨');
    }
  }
}

/**
 * Apply known issues update
 */
function applyKnownIssuesUpdate(model) {
  console.log('🔧 Applying known issues update...');
  
  console.log('  🔍 Checking known_issues section...');
  const knownIssues = model.system_status?.known_issues;
  console.log('    - model.system_status.known_issues exists:', !!knownIssues);
  console.log('    - model.system_status.known_issues is array:', Array.isArray(knownIssues));
  if (knownIssues) {
    console.log('    - Current known_issues count:', knownIssues.length);
    console.log('    - Current known_issues:', knownIssues);
  }
  
  if (knownIssues && Array.isArray(knownIssues)) {
    const cursorIssue = '🚨 CRITICAL: Cursor IDE systemic issue - AI assistants may not scan .cursor/rules and docs/ before work, leading to incomplete context and potential errors';
    
    if (!knownIssues.includes(cursorIssue)) {
      knownIssues.push(cursorIssue);
      console.log('  ✅ Added Cursor IDE systemic issue to known_issues');
    } else {
      console.log('  ℹ️  Cursor IDE issue already exists in known_issues');
    }
  } else {
    console.log('  ❌ known_issues section not found or not an array');
  }
}

/**
 * Apply backlog item
 */
function applyBacklogItem(model) {
  console.log('🔧 Applying backlog item...');
  
  console.log('  🔍 Checking backlogged section...');
  const backlogged = model.implementation_plan?.backlogged;
  console.log('    - model.implementation_plan.backlogged exists:', !!backlogged);
  console.log('    - model.implementation_plan.backlogged is array:', Array.isArray(backlogged));
  if (backlogged) {
    console.log('    - Current backlogged count:', backlogged.length);
  }
  
  if (backlogged && Array.isArray(backlogged)) {
    const mypyItem = {
      requirement: 'Fix 131 MyPy type errors',
      status: 'backlogged',
      domain: 'python_quality',
      priority: 'high',
      estimated_effort: '1-2 weeks',
      dependencies: [
        'src/**/*.py',
        'tests/**/*.py'
      ],
      description: 'Resolve 131 MyPy type errors currently affecting code quality and maintainability',
      acceptance_criteria: [
        'All MyPy type errors resolved',
        'Type annotations properly implemented',
        'Code quality score improved',
        'No new type errors introduced'
      ],
      risk_assessment: {
        risk_level: 'HIGH',
        impact: 'Affects code quality, maintainability, and development velocity',
        mitigation: 'Systematic resolution with pre-commit hooks and CI/CD integration'
      },
      date_added: '2025-08-19'
    };
    
    // Check if already exists
    const exists = backlogged.some(item => 
      item.requirement === 'Fix 131 MyPy type errors'
    );
    
    if (!exists) {
      backlogged.push(mypyItem);
      console.log('  ✅ Added MyPy type errors to backlog');
    } else {
      console.log('  ℹ️  MyPy type errors already exists in backlog');
    }
  }
}

/**
 * Apply requirements traceability
 */
function applyRequirementsTraceability(model) {
  console.log('🔧 Applying requirements traceability...');
  
  if (model.requirements_traceability && Array.isArray(model.requirements_traceability)) {
    const cursorRequirement = {
      requirement: 'Cursor IDE systemic issue mitigation',
      domain: 'cursor_ide_systemic_issue_mitigation',
      implementation: 'Makefile status reminders, risk management framework, multi-agent validation',
      test: 'test_requirement_cursor_ide_mitigation'
    };
    
    // Check if already exists
    const exists = model.requirements_traceability.some(item => 
      item.requirement === 'Cursor IDE systemic issue mitigation'
    );
    
    if (!exists) {
      model.requirements_traceability.push(cursorRequirement);
      console.log('  ✅ Added Cursor IDE requirement to traceability');
    }
  }
}

/**
 * Main recovery function
 */
function performRecovery() {
  console.log('🚨 Starting Cursor IDE Systemic Issue Recovery...\n');
  
  // Check if model file exists
  if (!fs.existsSync(MODEL_FILE)) {
    console.error('❌ Model file not found:', MODEL_FILE);
    process.exit(1);
  }
  
  // Create backup
  if (!createBackup()) {
    process.exit(1);
  }
  
  // Load model
  const model = loadModel();
  if (!model) {
    process.exit(1);
  }
  
  console.log('✅ Model loaded successfully\n');
  
  // Apply all recovery changes
  applyDomainAdditions(model);
  applyKnownIssuesUpdate(model);
  applyBacklogItem(model);
  applyRequirementsTraceability(model);
  
  console.log('\n🔧 All recovery changes applied');
  
  // Save model
  if (!saveModel(model)) {
    console.error('❌ Failed to save model, attempting to restore backup...');
    try {
      fs.copyFileSync(BACKUP_FILE, MODEL_FILE);
      console.log('✅ Backup restored');
    } catch (restoreError) {
      console.error('❌ Failed to restore backup:', restoreError.message);
    }
    process.exit(1);
  }
  
  // Validate final JSON
  console.log('\n🔍 Validating final JSON...');
  if (!validateJSON()) {
    console.error('❌ Final JSON validation failed, attempting to restore backup...');
    try {
      fs.copyFileSync(BACKUP_FILE, MODEL_FILE);
      console.log('✅ Backup restored');
    } catch (restoreError) {
      console.error('❌ Failed to restore backup:', restoreError.message);
    }
    process.exit(1);
  }
  
  console.log('\n🎉 Recovery completed successfully!');
  console.log('📁 Backup saved as:', BACKUP_FILE);
  console.log('🔍 Please review the changes with: git diff project_model_registry.json');
}

// Run recovery if this script is executed directly
if (require.main === module) {
  performRecovery();
}

module.exports = {
  performRecovery,
  createBackup,
  loadModel,
  saveModel,
  validateJSON
};
