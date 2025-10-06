#!/usr/bin/env node

/**
 * Project Model Registry Schema Manager
 * Uses JSON Schema validation and schema-driven updates instead of manual manipulation
 */

const Ajv = require('ajv');
const fs = require('fs');
const path = require('path');

class ProjectModelSchemaManager {
  constructor() {
    this.ajv = new Ajv({ 
      allErrors: true, 
      verbose: true,
      strict: false // Allow additional properties
    });
    
    this.schemaPath = path.join(__dirname, '..', 'project_model_registry.schema.json');
    this.modelPath = path.join(__dirname, '..', 'project_model_registry.json');
    
    this.loadSchema();
  }

  /**
   * Load or create the JSON schema for the project model
   */
  loadSchema() {
    try {
      if (fs.existsSync(this.schemaPath)) {
        this.schema = JSON.parse(fs.readFileSync(this.schemaPath, 'utf8'));
        console.log('✅ Loaded existing schema');
      } else {
        this.schema = this.createDefaultSchema();
        this.saveSchema();
        console.log('✅ Created default schema');
      }
    } catch (error) {
      console.log('❌ Error loading schema:', error.message);
      this.schema = this.createDefaultSchema();
    }
  }

  /**
   * Create a default JSON schema for the project model
   */
  createDefaultSchema() {
    return {
      $schema: "http://json-schema.org/draft-07/schema#",
      title: "OpenFlow Playground Project Model Registry",
      description: "Schema for the project model registry",
      type: "object",
      properties: {
        description: { type: "string" },
        author: { type: "string" },
        project_purpose: { type: "object" },
        domain_architecture: {
          type: "object",
          properties: {
            cursor_rules: {
              type: "object",
              properties: {
                description: { type: "string" },
                domains: {
                  type: "array",
                  items: { type: "string" }
                },
                emoji_prefixes: {
                  type: "object",
                  additionalProperties: { type: "string" }
                },
                purpose: { type: "string" }
              },
              required: ["domains"]
            }
          }
        },
        // Domain definitions follow a specific pattern
        domains: {
          type: "object",
          additionalProperties: {
            type: "object",
            properties: {
              patterns: {
                type: "array",
                items: { type: "string" }
              },
              content_indicators: {
                type: "array",
                items: { type: "string" }
              },
              linter: { type: "string" },
              formatter: { type: "string" },
              validator: { type: "string" },
              exclusions: {
                type: "array",
                items: { type: "string" }
              },
              requirements: {
                type: "array",
                items: { type: "string" }
              },
              demo_role: { type: "string" },
              extraction_candidate: { type: "string" },
              reason: { type: "string" },
              extraction_benefits: {
                type: "array",
                items: { type: "string" }
              }
            },
            required: ["patterns", "content_indicators", "requirements", "demo_role"]
          }
        },
        implementation_plan: {
          type: "object",
          properties: {
            backlogged: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  requirement: { type: "string" },
                  status: { type: "string" },
                  domain: { type: "string" },
                  priority: { type: "string" },
                  estimated_effort: { type: "string" },
                  dependencies: {
                    type: "array",
                    items: { type: "string" }
                  },
                  description: { type: "string" },
                  acceptance_criteria: {
                    type: "array",
                    items: { type: "string" }
                  },
                  date_added: { type: "string" }
                },
                required: ["requirement", "status", "domain"]
              }
            }
          }
        }
      },
      required: ["description", "author", "domain_architecture"]
    };
  }

  /**
   * Save the schema to file
   */
  saveSchema() {
    try {
      fs.writeFileSync(this.schemaPath, JSON.stringify(this.schema, null, 2));
      console.log('✅ Schema saved to', this.schemaPath);
    } catch (error) {
      console.log('❌ Error saving schema:', error.message);
    }
  }

  /**
   * Load the current project model
   */
  loadModel() {
    try {
      this.model = JSON.parse(fs.readFileSync(this.modelPath, 'utf8'));
      console.log('✅ Project model loaded');
      return true;
    } catch (error) {
      console.log('❌ Error loading project model:', error.message);
      return false;
    }
  }

  /**
   * Validate the project model against the schema
   */
  validateModel() {
    if (!this.model) {
      console.log('❌ No model loaded');
      return false;
    }

    const validate = this.ajv.compile(this.schema);
    const valid = validate(this.model);

    if (valid) {
      console.log('✅ Project model validates against schema');
      return true;
    } else {
      console.log('❌ Project model validation failed:');
      console.log('Errors:', JSON.stringify(validate.errors, null, 2));
      return false;
    }
  }

  /**
   * Add a new domain definition following the schema
   */
  addDomain(domainName, domainDefinition) {
    if (!this.model) {
      console.log('❌ No model loaded');
      return false;
    }

    // Validate domain definition against schema
    const domainSchema = this.schema.properties.domains.additionalProperties;
    const validateDomain = this.ajv.compile(domainSchema);
    const domainValid = validateDomain(domainDefinition);

    if (!domainValid) {
      console.log('❌ Domain definition does not match schema:');
      console.log('Errors:', JSON.stringify(validateDomain.errors, null, 2));
      return false;
    }

    // Add domain to model
    this.model[domainName] = domainDefinition;

    // Add to cursor_rules domains list if it exists
    if (this.model.domain_architecture && 
        this.model.domain_architecture.cursor_rules && 
        this.model.domain_architecture.cursor_rules.domains) {
      
      if (!this.model.domain_architecture.cursor_rules.domains.includes(domainName)) {
        this.model.domain_architecture.cursor_rules.domains.push(domainName);
        console.log('✅ Added domain to cursor_rules domains list');
      }

      // Add emoji prefix if emoji_prefixes exists
      if (this.model.domain_architecture.cursor_rules.emoji_prefixes) {
        this.model.domain_architecture.cursor_rules.emoji_prefixes[domainName] = '🚨';
        console.log('🚨 Added emoji prefix');
      }
    }

    console.log('✅ Domain added:', domainName);
    return true;
  }

  /**
   * Add a new backlog item following the schema
   */
  addBacklogItem(backlogItem) {
    if (!this.model) {
      console.log('❌ No model loaded');
      return false;
    }

    // Validate backlog item against schema
    const backlogSchema = this.schema.properties.implementation_plan.properties.backlogged.items;
    const validateBacklog = this.ajv.compile(backlogSchema);
    const backlogValid = validateBacklog(backlogItem);

    if (!backlogValid) {
      console.log('❌ Backlog item does not match schema:');
      console.log('Errors:', JSON.stringify(validateBacklog.errors, null, 2));
      return false;
    }

    // Add to backlog
    if (!this.model.implementation_plan) {
      this.model.implementation_plan = {};
    }
    if (!this.model.implementation_plan.backlogged) {
      this.model.implementation_plan.backlogged = [];
    }

    this.model.implementation_plan.backlogged.unshift(backlogItem); // Add to beginning
    console.log('✅ Backlog item added');
    return true;
  }

  /**
   * Save the updated model
   */
  saveModel() {
    try {
      // Validate before saving
      if (!this.validateModel()) {
        console.log('❌ Model validation failed, not saving');
        return false;
      }

      fs.writeFileSync(this.modelPath, JSON.stringify(this.model, null, 2));
      console.log('✅ Project model saved');
      return true;
    } catch (error) {
      console.log('❌ Error saving project model:', error.message);
      return false;
    }
  }

  /**
   * Get schema validation report
   */
  getValidationReport() {
    if (!this.model) {
      return { valid: false, error: 'No model loaded' };
    }

    const validate = this.ajv.compile(this.schema);
    const valid = validate(this.model);

    return {
      valid,
      errors: valid ? [] : validate.errors,
      modelSize: JSON.stringify(this.model).length,
      domainCount: Object.keys(this.model).filter(key => 
        this.model[key] && 
        this.model[key].patterns && 
        Array.isArray(this.model[key].patterns)
      ).length
    };
  }
}

// CLI usage
if (require.main === module) {
  const manager = new ProjectModelSchemaManager();
  
  if (manager.loadModel()) {
    const report = manager.getValidationReport();
    console.log('\n📊 VALIDATION REPORT:');
    console.log('====================');
    console.log('Valid:', report.valid);
    console.log('Model Size:', report.modelSize, 'characters');
    console.log('Domain Count:', report.domainCount);
    
    if (!report.valid) {
      console.log('\n❌ VALIDATION ERRORS:');
      console.log('=====================');
      report.errors.forEach((error, index) => {
        console.log(`${index + 1}. ${error.instancePath}: ${error.message}`);
      });
    }
  }
}

module.exports = ProjectModelSchemaManager;
