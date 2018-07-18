from src.graph_db import GraphDB
from src.sparql_query import SPARQLQuery
import json

db = "http://dbpedia.org/sparql"

query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbr: <http://dbpedia.org/resource/>
SELECT ?univ
WHERE {
  ?univ rdf:type dbo:University .
  ?univ dbo:campus dbr:Urban_area .
  ?univ foaf:name ?name .
  ?univ dbo:facultySize ?faculty .
  FILTER (?faculty > 4000) .
} ORDER BY ?name LIMIT 20
"""

frame = {
  "@id": {},
  "@type": "dbo:University",
  "dbo:city": {
    "@id": {},
    "dbo:area": {
      "@value": {}
    }
  }
}

graph = GraphDB(db)
q = SPARQLQuery(query, frame)
res = graph.query(q)

print(json.dumps(res.nested_jsonld, indent=2))