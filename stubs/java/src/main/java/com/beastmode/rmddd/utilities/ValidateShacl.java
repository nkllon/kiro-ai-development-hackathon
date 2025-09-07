package com.beastmode.rmddd.utilities;

import org.eclipse.rdf4j.model.Model;
import org.eclipse.rdf4j.model.util.Models;
import org.eclipse.rdf4j.rio.*;
import org.eclipse.rdf4j.sail.Sail;
import org.eclipse.rdf4j.sail.memory.MemoryStore;
import org.eclipse.rdf4j.sail.shacl.ShaclSail;
import org.eclipse.rdf4j.repository.sail.SailRepository;

import java.io.File;
import java.io.FileInputStream;

/**
 * SHACL validation utility for RM-DDD ontology validation.
 * Provides systematic validation of domain models against SHACL shapes.
 */
public class ValidateShacl {
    
    public static void main(String[] args) throws Exception {
        // Files
        File data = new File("examples/usps-sun.ttl");
        File shapesCore = new File("ontology/shacl/core.shacl.ttl");
        File shapesGov = new File("ontology/shacl/governance.shacl.ttl");
        
        // SHACL store
        Sail shacl = new ShaclSail(new MemoryStore());
        SailRepository repo = new SailRepository(shacl);
        repo.init();
        
        // Load shapes into SHACL sail
        try (var conn = repo.getConnection()) {
            conn.begin();
            conn.add(shapesCore, shapesCore.toURI().toString(), RDFFormat.TURTLE);
            conn.add(shapesGov, shapesGov.toURI().toString(), RDFFormat.TURTLE);
            conn.commit();
            
            // Validate a data graph
            conn.begin();
            conn.add(data, data.toURI().toString(), RDFFormat.TURTLE);
            conn.commit(); // commit triggers validation
        } catch (Exception e) {
            System.err.println("Validation failed: " + e.getMessage());
            throw e;
        } finally {
            repo.shutDown();
        }
        
        System.out.println("Validation OK ✅");
    }
    
    /**
     * Validate RDF data against SHACL shapes programmatically
     * @param dataFile The RDF data file to validate
     * @param shapeFiles Array of SHACL shape files
     * @return ValidationResult containing validation status and any violations
     */
    public static ValidationResult validateFile(File dataFile, File... shapeFiles) {
        ValidationResult result = new ValidationResult();
        
        Sail shacl = new ShaclSail(new MemoryStore());
        SailRepository repo = new SailRepository(shacl);
        
        try {
            repo.init();
            
            try (var conn = repo.getConnection()) {
                // Load SHACL shapes
                conn.begin();
                for (File shapeFile : shapeFiles) {
                    if (shapeFile.exists()) {
                        conn.add(shapeFile, shapeFile.toURI().toString(), RDFFormat.TURTLE);
                    } else {
                        result.addWarning("Shape file not found: " + shapeFile.getPath());
                    }
                }
                conn.commit();
                
                // Validate data
                conn.begin();
                if (dataFile.exists()) {
                    conn.add(dataFile, dataFile.toURI().toString(), RDFFormat.TURTLE);
                    conn.commit(); // This triggers SHACL validation
                } else {
                    result.addError("Data file not found: " + dataFile.getPath());
                }
            }
        } catch (Exception e) {
            result.addError("SHACL validation failed: " + e.getMessage());
        } finally {
            try {
                repo.shutDown();
            } catch (Exception e) {
                result.addWarning("Failed to shutdown repository: " + e.getMessage());
            }
        }
        
        return result;
    }
    
    /**
     * Validate RDF model against SHACL shapes
     * @param dataModel The RDF model to validate
     * @param shapeModels Array of SHACL shape models
     * @return ValidationResult containing validation status and any violations
     */
    public static ValidationResult validateModel(Model dataModel, Model... shapeModels) {
        ValidationResult result = new ValidationResult();
        
        Sail shacl = new ShaclSail(new MemoryStore());
        SailRepository repo = new SailRepository(shacl);
        
        try {
            repo.init();
            
            try (var conn = repo.getConnection()) {
                // Load SHACL shapes
                conn.begin();
                for (Model shapeModel : shapeModels) {
                    conn.add(shapeModel);
                }
                conn.commit();
                
                // Validate data
                conn.begin();
                conn.add(dataModel);
                conn.commit(); // This triggers SHACL validation
            }
        } catch (Exception e) {
            result.addError("SHACL validation failed: " + e.getMessage());
        } finally {
            try {
                repo.shutDown();
            } catch (Exception e) {
                result.addWarning("Failed to shutdown repository: " + e.getMessage());
            }
        }
        
        return result;
    }
}