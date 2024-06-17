from neo4j import GraphDatabase

def create_neo4j_graph(driver, extracted_info):
    with driver.session() as session:
        lines = extracted_info.strip().split('\n')
        for line in lines:
            if line.startswith("NDT Tool:"):
                current_tool = line.split(": ")[1]
            elif line.startswith("Related Deterioration Mechanisms:"):
                mechanisms = line.split(": ")[1]
                for mechanism in mechanisms.split(", "):
                    try:
                        deterioration, material = mechanism.rsplit(" (", 1)
                        material = material.rstrip(")")
                        create_relationships(session, current_tool, deterioration, material)
                    except ValueError:
                        print(f"Skipping malformed mechanism entry: {mechanism}")

def create_relationships(session, tool, mechanism, material):
    session.run("""
    MERGE (t:NDTTool {name: $tool})
    MERGE (m:DeteriorationMechanism {name: $mechanism})
    MERGE (mat:Material {name: $material})
    MERGE (m)-[:AFFECTS]->(mat)
    MERGE (t)-[:DETECTS]->(m)
    MERGE (t)-[:USED_FOR]->(mat)
    """, tool=tool, mechanism=mechanism, material=material)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "eklil@2017"))

# Use the previously saved files
with open('concrete_graph.txt', 'r') as f:
    concrete_info = f.read()

with open('wood_graph.txt', 'r') as f:
    wood_info = f.read()

with open('bricks_graph.txt', 'r') as f:
    bricks_info = f.read()

with open('metal_graph.txt', 'r') as f:
    metal_info = f.read()

with open('ndt_relationships.txt', 'r') as f:
    relationships_info = f.read()

with open('ndt-extracted.txt', 'r') as f:
    ndt_info = f.read()

create_neo4j_graph(driver, concrete_info)
create_neo4j_graph(driver, wood_info)
create_neo4j_graph(driver, bricks_info)
create_neo4j_graph(driver, metal_info)
create_neo4j_graph(driver, relationships_info)

create_neo4j_graph(driver, ndt_info)