package com.beastmode.rmddd.utilities;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RDFFormat;
import org.apache.jena.vocabulary.OWL;
import org.apache.jena.vocabulary.RDF;
import org.apache.jena.vocabulary.RDFS;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

/**
 * Utility class for Protégé integration and ontology management.
 * Provides methods to prepare ontologies for Protégé editing and validation.
 */
public class ProtegeIntegration {
    
    // Common namespace prefixes
    public static final String BM_NS = "http://nkllon.dev/beastmaster#";
    public static final String ONTOLOGY_BASE = "http://nkllon.dev/ontology/beastmaster/";
    public static final String VERSION = "0.8";
    
    /**
     * Add proper ontology headers to a TTL file for Protégé compatibility
     * @param inputFile The input TTL file
     * @param outputFile The output TTL file with headers
     * @param ontologyName The name of the ontology module
     * @param imports List of imported ontology URIs
     * @throws IOException if file operations fail
     */
    public static void addOntologyHeaders(File inputFile, File outputFile, 
                                        String ontologyName, List<String> imports) throws IOException {
        
        // Load existing model
        Model model = RDFDataMgr.loadModel(inputFile.getPath());
        
        // Create ontology resource
        String ontologyIRI = ONTOLOGY_BASE + ontologyName;
        String versionIRI = ontologyIRI + "/" + VERSION;
        
        Resource ontology = model.createResource(ontologyIRI);
        ontology.addProperty(RDF.type, OWL.Ontology);
        ontology.addProperty(model.createProperty(OWL.NS + "versionIRI"), 
                           model.createResource(versionIRI));
        
        // Add imports
        Property owlImports = model.createProperty(OWL.NS + "imports");
        for (String importUri : imports) {
            ontology.addProperty(owlImports, model.createResource(importUri));
        }
        
        // Add common annotations
        ontology.addProperty(RDFS.label, ontologyName + " Ontology");
        ontology.addProperty(RDFS.comment, 
            "Beast Mode " + ontologyName + " ontology module v" + VERSION);
        
        // Write to output file
        try (FileOutputStream out = new FileOutputStream(outputFile)) {
            RDFDataMgr.write(out, model, RDFFormat.TURTLE_PRETTY);
        }
    }
    
    /**
     * Create a profile ontology that imports all v0.8 modules
     * @param outputFile The output profile ontology file
     * @param moduleNames List of module names to import
     * @throws IOException if file operations fail
     */
    public static void createProfileOntology(File outputFile, List<String> moduleNames) throws IOException {
        Model model = ModelFactory.createDefaultModel();
        
        // Set up prefixes
        model.setNsPrefix("owl", OWL.NS);
        model.setNsPrefix("rdfs", RDFS.getURI());
        model.setNsPrefix("bm", BM_NS);
        
        // Create profile ontology
        String profileIRI = ONTOLOGY_BASE + "profile";
        Resource profile = model.createResource(profileIRI);
        profile.addProperty(RDF.type, OWL.Ontology);
        profile.addProperty(model.createProperty(OWL.NS + "versionIRI"), 
                          model.createResource(profileIRI + "/" + VERSION));
        
        // Add metadata
        profile.addProperty(RDFS.label, "Beast Mode Complete Profile");
        profile.addProperty(RDFS.comment, 
            "Complete Beast Mode ontology profile importing all v" + VERSION + " modules");
        
        // Import all modules
        Property owlImports = model.createProperty(OWL.NS + "imports");
        for (String moduleName : moduleNames) {
            String moduleIRI = ONTOLOGY_BASE + moduleName + "/" + VERSION;
            profile.addProperty(owlImports, model.createResource(moduleIRI));
        }
        
        // Write profile ontology
        try (FileOutputStream out = new FileOutputStream(outputFile)) {
            RDFDataMgr.write(out, model, RDFFormat.TURTLE_PRETTY);
        }
    }
    
    /**
     * Validate ontology structure for Protégé compatibility
     * @param ontologyFile The ontology file to validate
     * @return ValidationResult with any compatibility issues
     */
    public static ValidationResult validateProtegeCompatibility(File ontologyFile) {
        ValidationResult result = new ValidationResult();
        
        try {
            Model model = RDFDataMgr.loadModel(ontologyFile.getPath());
            
            // Check for ontology declaration
            boolean hasOntologyDeclaration = model.contains(null, RDF.type, OWL.Ontology);
            if (!hasOntologyDeclaration) {
                result.addError("Missing owl:Ontology declaration - required for Protégé");
            }
            
            // Check for version IRI
            Property versionIRI = model.createProperty(OWL.NS + "versionIRI");
            boolean hasVersionIRI = model.contains(null, versionIRI, (Resource) null);
            if (!hasVersionIRI) {
                result.addWarning("Missing owl:versionIRI - recommended for ontology versioning");
            }
            
            // Check for proper namespace usage
            if (!model.getNsPrefixMap().containsKey("owl")) {
                result.addWarning("Missing owl: prefix declaration");
            }
            
            if (!model.getNsPrefixMap().containsKey("rdfs")) {
                result.addWarning("Missing rdfs: prefix declaration");
            }
            
            // Check for labels and comments
            boolean hasLabels = model.contains(null, RDFS.label, (String) null);
            if (!hasLabels) {
                result.addWarning("No rdfs:label properties found - recommended for human-readable names");
            }
            
        } catch (Exception e) {
            result.addError("Failed to load ontology: " + e.getMessage());
        }
        
        return result;
    }
    
    /**
     * Generate a complete Beast Mode ontology setup for Protégé
     * @param baseDirectory The base directory for ontology files
     * @throws IOException if file operations fail
     */
    public static void setupProtegeEnvironment(File baseDirectory) throws IOException {
        // Create directory structure
        File ontologyDir = new File(baseDirectory, "ontology");
        File coreDir = new File(ontologyDir, "core");
        File alignmentDir = new File(ontologyDir, "alignment");
        File examplesDir = new File(baseDirectory, "examples");
        
        coreDir.mkdirs();
        alignmentDir.mkdirs();
        examplesDir.mkdirs();
        
        // Create profile ontology
        List<String> modules = Arrays.asList("core", "governance", "temporal", "security", 
                                           "events", "bridges", "personal", "alignment");
        
        File profileFile = new File(ontologyDir, "beastmaster-profile.ttl");
        createProfileOntology(profileFile, modules);
        
        // Create README for Protégé users
        File readmeFile = new File(ontologyDir, "PROTEGE-README.md");
        createProtegeReadme(readmeFile);
        
        System.out.println("Protégé environment setup complete in: " + baseDirectory.getAbsolutePath());
        System.out.println("Open beastmaster-profile.ttl in Protégé to get started");
    }
    
    /**
     * Create a README file with Protégé usage instructions
     * @param readmeFile The README file to create
     * @throws IOException if file operations fail
     */
    private static void createProtegeReadme(File readmeFile) throws IOException {
        String content = """
            # Beast Mode Ontology - Protégé Setup
            
            ## Quick Start
            
            1. **Open Protégé** → File → Open → `beastmaster-profile.ttl`
            2. **Set Ontology IRI** in Active Ontology tab if not already set
            3. **Start Reasoner** → Reasoner → HermiT (or ELK for faster performance)
            4. **Use DL Query tab** to test queries like `bm:PersonalOntology`
            
            ## File Structure
            
            - `beastmaster-profile.ttl` - Main profile importing all modules
            - `core/` - Core ontology modules
            - `alignment/` - Alignment mathematics ontology
            - `../examples/` - Example data and personal ontologies
            
            ## Common Protégé Issues & Fixes
            
            ### Nothing shows up / red squiggles
            - Check you're editing the right ontology in Active Ontology tab
            - Ensure ontology IRI is properly set
            
            ### Missing terms
            - You loaded a module without its imports
            - Add missing imports in Active Ontology → Ontology imports
            
            ### Reasoner freezes
            - Switch to ELK reasoner for better performance
            - Disable unsatisfiable explanations
            - Check for cycles or punning issues
            
            ### Ugly prefixes
            - Go to Preferences → Prefixes
            - Add: bm, gov, bridge, skos, etc.
            
            ### SHACL confusion
            - Protégé is OWL-first, use Java/RDF4J for SHACL validation
            - Run `mvn test` to validate SHACL constraints
            
            ## Recommended Workflow
            
            1. **Edit ontology** in Protégé with reasoning enabled
            2. **Save changes** and run Java tests: `mvn test`
            3. **Validate SHACL** constraints pass before committing
            4. **Keep individuals/examples** in separate files for clean TBox
            
            ## Ontology Structure
            
            Each module should have:
            - Proper ontology declaration with IRI and version IRI
            - Appropriate owl:imports for dependencies  
            - Human-friendly labels and comments using SKOS vocabulary
            - Clear separation between TBox (schema) and ABox (instances)
            
            ## Integration with Java
            
            - Run `mvn test` to validate all ontology files
            - SHACL validation happens automatically in CI/CD
            - SPARQL queries can be tested programmatically
            - Use `ValidateShacl.java` for custom validation scenarios
            """;
        
        java.nio.file.Files.write(readmeFile.toPath(), content.getBytes());
    }
    
    /**
     * Main method for command-line usage
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("Usage: ProtegeIntegration <setup|validate> [directory]");
            return;
        }
        
        String command = args[0];
        
        try {
            switch (command) {
                case "setup":
                    File baseDir = args.length > 1 ? new File(args[1]) : new File(".");
                    setupProtegeEnvironment(baseDir);
                    break;
                    
                case "validate":
                    File ontologyFile = args.length > 1 ? new File(args[1]) : 
                                       new File("ontology/beastmaster-profile.ttl");
                    ValidationResult result = validateProtegeCompatibility(ontologyFile);
                    
                    if (result.isValid()) {
                        System.out.println("✅ Ontology is Protégé-compatible");
                    } else {
                        System.out.println("❌ Protégé compatibility issues found:");
                        result.getErrors().forEach(error -> System.out.println("  ERROR: " + error));
                        result.getWarnings().forEach(warning -> System.out.println("  WARNING: " + warning));
                    }
                    break;
                    
                default:
                    System.out.println("Unknown command: " + command);
                    System.out.println("Available commands: setup, validate");
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}