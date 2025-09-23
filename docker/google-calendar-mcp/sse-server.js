#!/usr/bin/env node

/**
 * SSE MCP Server Wrapper
 * Wraps STDIO-based MCP servers to provide SSE (Server-Sent Events) interface
 * Beast Mode compliant implementation
 */

const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3500;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        server: 'google-calendar-mcp-sse-wrapper'
    });
});

// Ready check endpoint
app.get('/ready', (req, res) => {
    res.json({ 
        status: 'ready', 
        timestamp: new Date().toISOString(),
        mcp_server: '@cocal/google-calendar-mcp'
    });
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
    res.json({
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: new Date().toISOString()
    });
});

// SSE endpoint for MCP communication
app.get('/sse', (req, res) => {
    console.log(`${new Date().toISOString()}: SSE connection established`);
    
    // Set SSE headers
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    });

    // Send initial connection event
    res.write(`data: ${JSON.stringify({
        type: 'connection',
        status: 'connected',
        timestamp: new Date().toISOString()
    })}\n\n`);

    // Spawn the MCP server process
    const mcpProcess = spawn('npx', ['@cocal/google-calendar-mcp'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
            ...process.env,
            GOOGLE_OAUTH_CREDENTIALS: process.env.GOOGLE_OAUTH_CREDENTIALS || '/home/mcpuser/.config/google-calendar-mcp/gcp-oauth.keys.json'
        }
    });

    console.log(`${new Date().toISOString()}: MCP process spawned with PID ${mcpProcess.pid}`);

    // Handle MCP server output
    mcpProcess.stdout.on('data', (data) => {
        const message = data.toString().trim();
        if (message) {
            console.log(`${new Date().toISOString()}: MCP stdout: ${message}`);
            res.write(`data: ${JSON.stringify({
                type: 'mcp_output',
                data: message,
                timestamp: new Date().toISOString()
            })}\n\n`);
        }
    });

    mcpProcess.stderr.on('data', (data) => {
        const message = data.toString().trim();
        if (message) {
            console.log(`${new Date().toISOString()}: MCP stderr: ${message}`);
            res.write(`data: ${JSON.stringify({
                type: 'mcp_error',
                data: message,
                timestamp: new Date().toISOString()
            })}\n\n`);
        }
    });

    mcpProcess.on('close', (code) => {
        console.log(`${new Date().toISOString()}: MCP process exited with code ${code}`);
        res.write(`data: ${JSON.stringify({
            type: 'mcp_exit',
            code: code,
            timestamp: new Date().toISOString()
        })}\n\n`);
        res.end();
    });

    mcpProcess.on('error', (error) => {
        console.error(`${new Date().toISOString()}: MCP process error:`, error);
        res.write(`data: ${JSON.stringify({
            type: 'mcp_process_error',
            error: error.message,
            timestamp: new Date().toISOString()
        })}\n\n`);
        res.end();
    });

    // Handle client disconnect
    req.on('close', () => {
        console.log(`${new Date().toISOString()}: SSE client disconnected`);
        if (mcpProcess && !mcpProcess.killed) {
            mcpProcess.kill();
        }
    });

    // Handle MCP requests from client
    req.on('data', (data) => {
        if (mcpProcess && mcpProcess.stdin.writable) {
            mcpProcess.stdin.write(data);
        }
    });
});

// POST endpoint for MCP requests
app.post('/mcp', (req, res) => {
    console.log(`${new Date().toISOString()}: MCP request received:`, req.body);
    
    // Spawn MCP process for single request
    const mcpProcess = spawn('npx', ['@cocal/google-calendar-mcp'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
            ...process.env,
            GOOGLE_OAUTH_CREDENTIALS: process.env.GOOGLE_OAUTH_CREDENTIALS || '/home/mcpuser/.config/google-calendar-mcp/gcp-oauth.keys.json'
        }
    });

    let output = '';
    let error = '';

    mcpProcess.stdout.on('data', (data) => {
        output += data.toString();
    });

    mcpProcess.stderr.on('data', (data) => {
        error += data.toString();
    });

    mcpProcess.on('close', (code) => {
        if (code === 0) {
            try {
                const result = JSON.parse(output);
                res.json(result);
            } catch (e) {
                res.json({ output: output.trim(), raw: true });
            }
        } else {
            res.status(500).json({ 
                error: 'MCP process failed', 
                code: code, 
                stderr: error.trim(),
                stdout: output.trim()
            });
        }
    });

    // Send request to MCP process
    if (req.body) {
        mcpProcess.stdin.write(JSON.stringify(req.body) + '\n');
        mcpProcess.stdin.end();
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`${new Date().toISOString()}: SSE MCP Server listening on port ${PORT}`);
    console.log(`${new Date().toISOString()}: Health check: http://localhost:${PORT}/health`);
    console.log(`${new Date().toISOString()}: SSE endpoint: http://localhost:${PORT}/sse`);
    console.log(`${new Date().toISOString()}: MCP endpoint: http://localhost:${PORT}/mcp`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log(`${new Date().toISOString()}: Received SIGTERM, shutting down gracefully`);
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log(`${new Date().toISOString()}: Received SIGINT, shutting down gracefully`);
    process.exit(0);
});