#!/usr/bin/env node
/**
 * Backlog CLI - Project Backlog Management Tool
 * Manages backlog items, requirements, and project tracking
 * Uses our existing JavaScript editing tools and schema manager
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class BacklogManager {
    constructor(projectPath = '.') {
        this.projectPath = projectPath;
        this.modelFile = path.join(projectPath, 'project_model_registry.json');
        this.backupDir = path.join(projectPath, 'backup');
    }

    loadModel() {
        try {
            // Load the model directly from file since we need to work with it
            const content = fs.readFileSync(this.modelFile, 'utf8');
            return JSON.parse(content);
        } catch (error) {
            console.log('❌ Failed to load model:', error.message);
            return {};
        }
    }

    saveModel(model) {
        try {
            // Save the model directly to file
            fs.writeFileSync(this.modelFile, JSON.stringify(model, null, 2));
            return true;
        } catch (error) {
            console.log('❌ Failed to save model:', error.message);
            return false;
        }
    }

    addBacklogItem(requirement, description = '', priority = 'medium', domain = 'general') {
        const model = this.loadModel();
        
        if (!model.implementation_plan) {
            model.implementation_plan = {};
        }
        if (!model.implementation_plan.backlogged) {
            model.implementation_plan.backlogged = [];
        }
        
        const newItem = {
            requirement,
            description,
            priority,
            domain,
            status: 'backlogged',
            estimated_effort: '1 week',
            dependencies: [],
            acceptance_criteria: [],
            date_added: new Date().toISOString().split('T')[0]
        };
        
        model.implementation_plan.backlogged.push(newItem);
        
        if (this.saveModel(model)) {
            console.log(`✅ Added backlog item: ${requirement}`);
            return true;
        } else {
            console.log(`❌ Failed to add backlog item: ${requirement}`);
            return false;
        }
    }

    listBacklogItems() {
        const model = this.loadModel();
        const backlog = model.implementation_plan?.backlogged || [];
        
        console.log(`\n📋 Backlog Items (${backlog.length} total):`);
        backlog.forEach((item, index) => {
            const status = item.status || 'unknown';
            const priority = item.priority || 'medium';
            const requirement = item.requirement || 'No title';
            const domain = item.domain || 'unknown';
            
            const statusIcon = {
                'backlogged': '⏳',
                'in_progress': '🔄', 
                'implemented': '✅',
                'blocked': '🚫',
                'cancelled': '❌'
            }[status] || '❓';
            
            const priorityIcon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }[priority] || '⚪';
            
            console.log(`  ${index + 1}. ${statusIcon} ${priorityIcon} ${requirement}`);
            console.log(`     Status: ${status} | Priority: ${priority} | Domain: ${domain}`);
            
            if (item.description) {
                const desc = item.description.length > 80 
                    ? item.description.substring(0, 80) + "..." 
                    : item.description;
                console.log(`     Description: ${desc}`);
            }
            console.log();
        });
        
        return backlog;
    }

    updateBacklogItem(itemId, updates) {
        const model = this.loadModel();
        
        if (!model.implementation_plan?.backlogged) {
            console.log('❌ No backlog items found');
            return false;
        }
        
        // Find item by requirement (title) or index
        let item;
        let itemIndex = -1;
        
        if (typeof itemId === 'number') {
            itemIndex = itemId - 1; // Convert 1-based index to 0-based
            if (itemIndex >= 0 && itemIndex < model.implementation_plan.backlogged.length) {
                item = model.implementation_plan.backlogged[itemIndex];
            }
        } else {
            // Search by requirement text
            itemIndex = model.implementation_plan.backlogged.findIndex(backlogItem => 
                backlogItem.requirement === itemId
            );
            if (itemIndex !== -1) {
                item = model.implementation_plan.backlogged[itemIndex];
            }
        }
        
        if (!item) {
            console.log(`❌ Backlog item not found: ${itemId}`);
            return false;
        }
        
        // Update fields
        Object.entries(updates).forEach(([key, value]) => {
            if (key in item) {
                item[key] = value;
                console.log(`  📝 Updated ${key}: ${value}`);
            } else {
                console.log(`  ⚠️ Unknown field: ${key}`);
            }
        });
        
        if (this.saveModel(model)) {
            console.log(`✅ Updated backlog item: ${item.requirement}`);
            return true;
        } else {
            console.log(`❌ Failed to update backlog item: ${item.requirement}`);
            return false;
        }
    }

    removeBacklogItem(itemId) {
        const model = this.loadModel();
        
        if (!model.implementation_plan?.backlogged) {
            console.log('❌ No backlog items found');
            return false;
        }
        
        // Find item by requirement (title) or index
        let itemIndex = -1;
        
        if (typeof itemId === 'number') {
            itemIndex = itemId - 1; // Convert 1-based index to 0-based
        } else {
            // Search by requirement text
            itemIndex = model.implementation_plan.backlogged.findIndex(backlogItem => 
                backlogItem.requirement === itemId
            );
        }
        
        if (itemIndex === -1 || itemIndex >= model.implementation_plan.backlogged.length) {
            console.log(`❌ Backlog item not found: ${itemId}`);
            return false;
        }
        
        // Remove item
        const removedItem = model.implementation_plan.backlogged.splice(itemIndex, 1)[0];
        
        if (this.saveModel(model)) {
            console.log(`✅ Removed backlog item: ${removedItem.requirement}`);
            return true;
        } else {
            console.log(`❌ Failed to remove backlog item: ${removedItem.requirement}`);
            return false;
        }
    }

    showBacklogStats() {
        const model = this.loadModel();
        const backlog = model.implementation_plan?.backlogged || [];
        
        if (backlog.length === 0) {
            console.log('📊 No backlog items found');
            return {};
        }
        
        // Count by status and priority
        const statusCounts = {};
        const priorityCounts = {};
        const domainCounts = {};
        
        backlog.forEach(item => {
            const status = item.status || 'unknown';
            const priority = item.priority || 'medium';
            const domain = item.domain || 'unknown';
            
            statusCounts[status] = (statusCounts[status] || 0) + 1;
            priorityCounts[priority] = (priorityCounts[priority] || 0) + 1;
            domainCounts[domain] = (domainCounts[domain] || 0) + 1;
        });
        
        console.log('\n📊 Backlog Statistics:');
        console.log(`  📋 Total Items: ${backlog.length}`);
        console.log(`  ⏳ Backlogged: ${statusCounts.backlogged || 0}`);
        console.log(`  🔄 In Progress: ${statusCounts.in_progress || 0}`);
        console.log(`  ✅ Implemented: ${statusCounts.implemented || 0}`);
        console.log(`  🚫 Blocked: ${statusCounts.blocked || 0}`);
        
        console.log(`\n  🔴 Critical: ${priorityCounts.critical || 0}`);
        console.log(`  🟠 High: ${priorityCounts.high || 0}`);
        console.log(`  🟡 Medium: ${priorityCounts.medium || 0}`);
        console.log(`  🟢 Low: ${priorityCounts.low || 0}`);
        
        console.log(`\n  🌐 Domains:`);
        Object.entries(domainCounts).forEach(([domain, count]) => {
            console.log(`    ${domain}: ${count}`);
        });
        
        return {
            total: backlog.length,
            status_counts: statusCounts,
            priority_counts: priorityCounts,
            domain_counts: domainCounts
        };
    }

    searchBacklog(query) {
        const model = this.loadModel();
        const backlog = model.implementation_plan?.backlogged || [];
        
        if (!query) {
            return backlog;
        }
        
        const queryLower = query.toLowerCase();
        const results = backlog.filter(item => {
            const requirement = (item.requirement || '').toLowerCase();
            const description = (item.description || '').toLowerCase();
            const domain = (item.domain || '').toLowerCase();
            
            return requirement.includes(queryLower) || 
                   description.includes(queryLower) || 
                   domain.includes(queryLower);
        });
        
        console.log(`\n🔍 Search Results for '${query}' (${results.length} found):`);
        results.forEach((item, index) => {
            const status = item.status || 'unknown';
            const priority = item.priority || 'medium';
            const requirement = item.requirement || 'No title';
            
            const statusIcon = {
                'backlogged': '⏳',
                'in_progress': '🔄', 
                'implemented': '✅',
                'blocked': '🚫',
                'cancelled': '❌'
            }[status] || '❓';
            
            const priorityIcon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }[priority] || '⚪';
            
            console.log(`  ${index + 1}. ${statusIcon} ${priorityIcon} ${requirement}`);
            console.log(`     Status: ${status} | Priority: ${priority} | Domain: ${item.domain || 'unknown'}`);
        });
        
        return results;
    }
}

function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.log('Usage: node backlog_cli.js [list|add|update|remove|stats|search]');
        console.log('  list   - List all backlog items');
        console.log('  add    - Add new backlog item');
        console.log('  update - Update existing backlog item');
        console.log('  remove - Remove backlog item');
        console.log('  stats  - Show backlog statistics');
        console.log('  search - Search backlog items');
        process.exit(1);
    }
    
    const command = args[0].toLowerCase();
    const manager = new BacklogManager();
    
    switch (command) {
        case 'list':
            manager.listBacklogItems();
            break;
            
        case 'add':
            if (args.length < 3) {
                console.log('❌ Usage: node backlog_cli.js add "Requirement" [description] [priority] [domain]');
                process.exit(1);
            }
            
            const requirement = args[1];
            const description = args[2] || '';
            const priority = args[3] || 'medium';
            const domain = args[4] || 'general';
            
            manager.addBacklogItem(requirement, description, priority, domain);
            break;
            
        case 'update':
            if (args.length < 4) {
                console.log('❌ Usage: node backlog_cli.js update "ID/Requirement" field value');
                console.log('  Example: node backlog_cli.js update "Fix MCP" status in_progress');
                process.exit(1);
            }
            
            const itemId = args[1];
            const field = args[2];
            const value = args[3] || '';
            
            manager.updateBacklogItem(itemId, { [field]: value });
            break;
            
        case 'remove':
            if (args.length < 2) {
                console.log('❌ Usage: node backlog_cli.js remove "ID/Requirement"');
                process.exit(1);
            }
            
            const removeId = args[1];
            manager.removeBacklogItem(removeId);
            break;
            
        case 'stats':
            manager.showBacklogStats();
            break;
            
        case 'search':
            if (args.length < 2) {
                console.log('❌ Usage: node backlog_cli.js search "query"');
                process.exit(1);
            }
            
            const query = args[1];
            manager.searchBacklog(query);
            break;
            
        default:
            console.log(`❌ Unknown command: ${command}`);
            console.log('Available commands: list, add, update, remove, stats, search');
            process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = BacklogManager;
