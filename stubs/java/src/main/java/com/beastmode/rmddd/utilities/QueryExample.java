package com.beastmode.rmddd.utilities;

import org.apache.jena.query.*;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.riot.RDFDataMgr;

/**
 * SPARQL query example for RM-DDD ontology querying.
 * Demonstrates how to query RDF data using Apache Jena.
 */
public class QueryExample {
    
    public static void main(String[] args) {
        Model m = RDFDataMgr.loadModel("examples/personal-ontology.ttl");
        
        String q = """
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?label WHERE {
                ?r skos:prefLabel "Accounts Payable Module"@en .
                ?r skos:altLabel ?label .
            }
            """;
        
        try (QueryExecution qe = QueryExecutionFactory.create(q, m)) {
            qe.execSelect().forEachRemaining(rs ->
                System.out.println("alias: " + rs.getLiteral("label").getString())
            );
        }
    }
    
    /**
     * Execute a SPARQL SELECT query against an RDF model
     * @param model The RDF model to query
     * @param sparqlQuery The SPARQL query string
     * @return ResultSet containing query results
     */
    public static ResultSet executeSelectQuery(Model model, String sparqlQuery) {
        try (QueryExecution qe = QueryExecutionFactory.create(sparqlQuery, model)) {
            return qe.execSelect();
        }
    }
    
    /**
     * Execute a SPARQL CONSTRUCT query against an RDF model
     * @param model The RDF model to query
     * @param sparqlQuery The SPARQL CONSTRUCT query string
     * @return Model containing constructed triples
     */
    public static Model executeConstructQuery(Model model, String sparqlQuery) {
        try (QueryExecution qe = QueryExecutionFactory.create(sparqlQuery, model)) {
            return qe.execConstruct();
        }
    }
    
    /**
     * Execute a SPARQL ASK query against an RDF model
     * @param model The RDF model to query
     * @param sparqlQuery The SPARQL ASK query string
     * @return boolean result of the ASK query
     */
    public static boolean executeAskQuery(Model model, String sparqlQuery) {
        try (QueryExecution qe = QueryExecutionFactory.create(sparqlQuery, model)) {
            return qe.execAsk();
        }
    }
    
    /**
     * Find all alternative labels for a given preferred label
     * @param model The RDF model to search
     * @param preferredLabel The preferred label to search for
     * @return ResultSet containing alternative labels
     */
    public static ResultSet findAlternativeLabels(Model model, String preferredLabel) {
        String query = String.format("""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?altLabel WHERE {
                ?resource skos:prefLabel "%s"@en .
                ?resource skos:altLabel ?altLabel .
            }
            """, preferredLabel);
        
        return executeSelectQuery(model, query);
    }
    
    /**
     * Find all concepts in a specific domain context
     * @param model The RDF model to search
     * @param domainContext The domain context to filter by
     * @return ResultSet containing concepts in the domain
     */
    public static ResultSet findConceptsInDomain(Model model, String domainContext) {
        String query = String.format("""
            PREFIX bm: <http://beastmode.com/ontology/core#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?concept ?label WHERE {
                ?concept bm:domainContext "%s" .
                ?concept skos:prefLabel ?label .
            }
            """, domainContext);
        
        return executeSelectQuery(model, query);
    }
    
    /**
     * Validate that a concept has required properties
     * @param model The RDF model to validate
     * @param conceptUri The URI of the concept to validate
     * @return boolean indicating if concept has required properties
     */
    public static boolean validateConceptProperties(Model model, String conceptUri) {
        String query = String.format("""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX bm: <http://beastmode.com/ontology/core#>
            ASK {
                <%s> skos:prefLabel ?label .
                <%s> bm:domainContext ?context .
            }
            """, conceptUri, conceptUri);
        
        return executeAskQuery(model, query);
    }
}