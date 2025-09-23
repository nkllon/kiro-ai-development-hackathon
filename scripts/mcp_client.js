#!/usr/bin/env node
/**
 * MCP Client for Google Calendar Server
 * Uses the official @modelcontextprotocol/sdk
 */

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { spawn } = require('child_process');

class GoogleCalendarMCPClient {
    constructor() {
        this.client = null;
        this.transport = null;
    }

    async connect() {
        console.log('🔌 Connecting to Google Calendar MCP Server...');
        
        try {
            // Connect to the MCP server running in Docker
            const serverProcess = spawn('docker', [
                'exec', '-i', 'google_calendar_mcp', 'google-calendar-mcp'
            ], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            // Create transport
            this.transport = new StdioClientTransport({
                stdin: serverProcess.stdin,
                stdout: serverProcess.stdout,
                stderr: serverProcess.stderr
            });

            // Create client
            this.client = new Client({
                name: "beast-mode-calendar-client",
                version: "1.0.0"
            }, {
                capabilities: {}
            });

            // Connect
            await this.client.connect(this.transport);
            console.log('✅ Connected to MCP server');
            
            return true;
        } catch (error) {
            console.error('❌ Failed to connect:', error.message);
            return false;
        }
    }

    async listTools() {
        console.log('\n🔧 Listing available tools...');
        
        try {
            const response = await this.client.listTools();
            console.log('Available tools:');
            response.tools.forEach(tool => {
                console.log(`  - ${tool.name}: ${tool.description}`);
            });
            return response.tools;
        } catch (error) {
            console.error('❌ Failed to list tools:', error.message);
            return [];
        }
    }

    async callTool(name, args = {}) {
        console.log(`\n🛠️  Calling tool: ${name}`);
        console.log(`   Arguments: ${JSON.stringify(args, null, 2)}`);
        
        try {
            const response = await this.client.callTool({
                name: name,
                arguments: args
            });
            
            console.log('✅ Tool response:');
            console.log(JSON.stringify(response, null, 2));
            return response;
        } catch (error) {
            console.error('❌ Tool call failed:', error.message);
            return null;
        }
    }

    async testCalendarOperations() {
        console.log('\n📅 Testing calendar operations...');
        
        // List calendars
        await this.callTool('list_calendars');
        
        // Get events from primary calendar
        await this.callTool('get_events', {
            calendar_id: 'primary',
            max_results: 5
        });
        
        // Get today's events
        const today = new Date().toISOString().split('T')[0];
        await this.callTool('get_events', {
            calendar_id: 'primary',
            time_min: `${today}T00:00:00Z`,
            time_max: `${today}T23:59:59Z`
        });
    }

    async disconnect() {
        if (this.client) {
            await this.client.close();
            console.log('🔌 Disconnected from MCP server');
        }
    }
}

async function main() {
    console.log('🚀 Google Calendar MCP Client Test');
    console.log('=' .repeat(50));
    
    const client = new GoogleCalendarMCPClient();
    
    try {
        // Connect to server
        if (!await client.connect()) {
            process.exit(1);
        }
        
        // List available tools
        await client.listTools();
        
        // Test calendar operations
        await client.testCalendarOperations();
        
        console.log('\n✅ All tests completed successfully');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down...');
    process.exit(0);
});

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { GoogleCalendarMCPClient };