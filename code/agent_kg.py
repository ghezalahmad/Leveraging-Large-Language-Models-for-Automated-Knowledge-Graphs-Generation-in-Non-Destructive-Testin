from neo4j import GraphDatabase
import re
from striprtf.striprtf import rtf_to_text

# Connect to the Neo4j database
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "eklil@2017"))

# Function to read RTF file
def read_rtf_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return rtf_to_text(content)

# Function to parse the content of RTF file
def parse_rtf_content(content):
    return [line.strip() for line in content.split('\n') if line.strip()]

def create_material_nodes(tx):
    materials = ["Concrete", "Steel", "Wood", "Bricks"]
    for material in materials:
        tx.run("MERGE (m:Material {name: $name})", name=material)

def create_deterioration_nodes(tx, material, deterioration, physical_change, ndt_method):
    tx.run("MERGE (m:Material {name: $material}) "
           "MERGE (d:DeteriorationMechanism {name: $deterioration}) "
           "MERGE (p:PhysicalChange {name: $physical_change}) "
           "MERGE (n:NDTMethod {name: $ndt_method}) "
           "MERGE (m)-[:HAS_DETERIORATION_MECHANISM]->(d) "
           "MERGE (d)-[:CAUSES_PHYSICAL_CHANGE]->(p) "
           "MERGE (p)-[:DETECTED_BY]->(n)",
           material=material, deterioration=deterioration, physical_change=physical_change, ndt_method=ndt_method)

def load_data():
    with driver.session() as session:
        # Create material nodes
        session.write_transaction(create_material_nodes)

        # Load and parse data for each material
        materials_data = {
            'Concrete': [
                "Concrete; corrosion; cracking; visual inspection",
                "Concrete; corrosion; spalling; ultrasonic testing",
                "Concrete; corrosion; discoloration; infrared thermography",
                "Concrete; freeze-thaw cycles; cracking; visual inspection",
                "Concrete; freeze-thaw cycles; spalling; ultrasonic testing",
                "Concrete; freeze-thaw cycles; discoloration; infrared thermography",
                "Concrete; chemical attack; cracking; visual inspection",
                "Concrete; chemical attack; spalling; ultrasonic testing",
                "Concrete; chemical attack; discoloration; infrared thermography",
                "Concrete; changes in microstructure; cracking; visual inspection",
                "Concrete; changes in microstructure; spalling; ultrasonic testing",
                "Concrete; changes in microstructure; discoloration; infrared thermography",
                "Concrete; changes in mechanical properties; cracking; visual inspection",
                "Concrete; changes in mechanical properties; spalling; ultrasonic testing",
                "Concrete; changes in mechanical properties; discoloration; infrared thermography",
                "Concrete; dimensional changes; cracking; visual inspection",
                "Concrete; dimensional changes; spalling; ultrasonic testing",
                "Concrete; dimensional changes; discoloration; infrared thermography",
                "Concrete; corrosion; cracking; half-cell potential measurement",
                "Concrete; corrosion; spalling; half-cell potential measurement",
                "Concrete; corrosion; discoloration; half-cell potential measurement",
                "Concrete; freeze-thaw cycles; cracking; ultrasonic pulse velocity",
                "Concrete; freeze-thaw cycles; spalling; ultrasonic pulse velocity",
                "Concrete; freeze-thaw cycles; discoloration; ultrasonic pulse velocity",
                "Concrete; chemical attack; cracking; permeation test",
                "Concrete; chemical attack; spalling; permeation test",
                "Concrete; chemical attack; discoloration; permeation test",
                "Concrete; extreme temperature changes; cracking; resonant frequency methods",
                "Concrete; extreme temperature changes; spalling; resonant frequency methods",
                "Concrete; extreme temperature changes; discoloration; resonant frequency methods",
                "Concrete; mechanical loading; cracking; impact-echo method",
                "Concrete; mechanical loading; spalling; impact-echo method",
                "Concrete; mechanical loading; voids; impact-echo method",
                "Concrete; mechanical loading; delamination; impact-echo method",
                "Concrete; moisture ingress; cracking; chloride-ion permeability test",
                "Concrete; moisture ingress; spalling; chloride-ion permeability test",
                "Concrete; moisture ingress; discoloration; chloride-ion permeability test",
                "Concrete; corrosion; cracking; half-cell potential test",
                "Concrete; corrosion; spalling; half-cell potential test",
                "Concrete; freeze-thaw cycles; cracking; visual inspection",
                "Concrete; freeze-thaw cycles; spalling; visual inspection",
                "Concrete; chemical attack; discoloration; visual inspection",
                "Concrete; chemical attack; cracking; ultrasonic testing",
                "Concrete; carbonation; cracking; ultrasonic testing",
                "Concrete; carbonation; spalling; infrared thermography",
                "Concrete; chloride ion content; cracking; infrared thermography",
                "Concrete; chloride ion content; spalling; acoustic techniques",
                "Concrete; changes in microstructure; cracking; acoustic techniques",
                "Concrete; changes in microstructure; spalling; rebound hammer",
                "Concrete; changes in mechanical properties; cracking; pullout test",
                "Concrete; changes in mechanical properties; spalling; pull-off test",
                "Concrete; dimensional changes; cracking; penetration resistance methods",
                "Concrete; dimensional changes; spalling; ultrasonic pulse velocity method",
            ],
            'Steel': [
                "Steel; corrosion; thinning; ultrasonic testing",
                "Steel; corrosion; pitting; eddy current testing",
                "Steel; fatigue; cracking; radiographic testing",
                "Steel; stress corrosion cracking; cracking; eddy current testing",
                "Steel; corrosion; changes in microstructure; visual testing",
                "Steel; fatigue; changes in mechanical properties; eddy current testing",
                "Steel; stress corrosion cracking; dimensional changes; acoustic emission",
                "Steel; corrosion; pitting; ultrasonic testing",
                "Steel; corrosion; cracking; ultrasonic testing",
                "Steel; fatigue; cracking; eddy current testing",
                "Steel; corrosion; thinning; eddy current testing",
                "Steel; corrosion; cracking; eddy current testing",
                "Steel; fatigue; cracking; acoustic emission",
                "Steel; stress corrosion cracking; cracking; acoustic emission",
                "Steel; corrosion; thinning; x-radiography",
                "Steel; corrosion; pitting; x-radiography",
                "Steel; corrosion; cracking; x-radiography",
                "Steel; fatigue; cracking; x-radiography",
                "Steel; stress corrosion cracking; cracking; x-radiography",
                "Steel; corrosion; thinning; laser-based technique",
                "Steel; corrosion; pitting; laser-based technique",
                "Steel; corrosion; cracking; laser-based technique",
                "Steel; fatigue; cracking; laser-based technique",
                "Steel; stress corrosion cracking; cracking; laser-based technique",
                "Steel; stress corrosion cracking; cracking; visual testing",
                "Steel; residual stresses; changes in mechanical properties; ultrasonic critical refracted longitudinal waves",
                "Steel; fatigue; cracking; guided ultrasonic wave procedure",
                "Steel; corrosion; thinning; radiographic testing",
                "Steel; corrosion; thinning; acoustic emissions",
                "Steel; fatigue; cracking; ultrasonic testing",
                "Steel; fatigue; cracking; acoustic emissions",
                "Steel; stress corrosion cracking; cracking; radiographic testing",
                "Steel; stress corrosion cracking; cracking; ultrasonic testing",
                "Steel; stress corrosion cracking; cracking; acoustic emissions",
                "Steel; corrosion; pitting; radiographic testing",
                "Steel; corrosion; pitting; acoustic emissions",
                "Steel; fatigue; changes in microstructure; radiographic testing",
                "Steel; fatigue; changes in microstructure; ultrasonic testing",
                "Steel; fatigue; changes in microstructure; eddy current testing",
                "Steel; fatigue; changes in microstructure; acoustic emissions",
                "Steel; stress corrosion cracking; changes in microstructure; radiographic testing",
                "Steel; stress corrosion cracking; changes in microstructure; ultrasonic testing",
                "Steel; stress corrosion cracking; changes in microstructure; eddy current testing",
                "Steel; stress corrosion cracking; changes in microstructure; acoustic emissions",
                "Steel; corrosion; changes in mechanical properties; radiographic testing",
                "Steel; corrosion; changes in mechanical properties; ultrasonic testing",
                "Steel; corrosion; changes in mechanical properties; eddy current testing",
                "Steel; corrosion; changes in mechanical properties; acoustic emissions",
                "Steel; fatigue; changes in mechanical properties; radiographic testing",
                "Steel; fatigue; changes in mechanical properties; ultrasonic testing",
                "Steel; fatigue; changes in mechanical properties; acoustic emissions",
                "Steel; stress corrosion cracking; changes in mechanical properties; radiographic testing",
                "Steel; stress corrosion cracking; changes in mechanical properties; ultrasonic testing",
                "Steel; stress corrosion cracking; changes in mechanical properties; eddy current testing",
                "Steel; stress corrosion cracking; changes in mechanical properties; acoustic emissions",
                "Steel; corrosion; dimensional changes; radiographic testing",
                "Steel; corrosion; dimensional changes; ultrasonic testing",
                "Steel; corrosion; dimensional changes; eddy current testing",
                "Steel; corrosion; dimensional changes; acoustic emissions",
                "Steel; fatigue; dimensional changes; radiographic testing",
                "Steel; fatigue; dimensional changes; ultrasonic testing",
                "Steel; fatigue; dimensional changes; eddy current testing",
                "Steel; fatigue; dimensional changes; acoustic emissions",
                "Steel; stress corrosion cracking; dimensional changes; radiographic testing",
                "Steel; stress corrosion cracking; dimensional changes; ultrasonic testing",
                "Steel; stress corrosion cracking; dimensional changes; eddy current testing",
                "Steel; stress corrosion cracking; dimensional changes; acoustic emissions",
                "Steel; corrosion; pitting; radiographic inspection",
                "Steel; fatigue; dimensional changes; acoustic emission",
                "Steel; corrosion; changes in mechanical properties; radiographic inspection",
                "Steel; fatigue; changes in mechanical properties; acoustic emission",
                "Steel; corrosion; changes in microstructure; radiographic inspection",
                "Steel; fatigue; pitting; acoustic emission",
                "Steel; fatigue; changes in mechanical properties; acoustic emission testing",
                "Steel; corrosion; changes in microstructure; eddy current testing",
                "Steel; fatigue; changes in microstructure; x-ray diffraction analysis",
                "Steel; fatigue; dimensional changes; acoustic emission testing",
                "Steel; corrosion; changes in microstructure; ultrasonic testing",
            ],
            'Wood': [
                "Wood; fungal decay; changes in structure geometry; visual inspection",
                "Wood; fungal decay; changes in material macro- & microstructure; ultrasonic testing",
                "Wood; insect attack; discontinuity of material; visual inspection",
                "Wood; insect attack; changes in structure geometry; ultrasonic testing",
                "Wood; UV exposure; surface roughness; visual inspection",
                "Wood; UV exposure; erosion of early-wood; visual inspection",
                "Wood; mechanical wear; crack formation; visual inspection",
                "Wood; mechanical wear; delamination; visual inspection",
                "Wood; moisture changes; crack formation; visual inspection",
                "Wood; moisture changes; delamination; visual inspection",
                "Wood; mechanical long-term load; changes in mechanical parameters; visual inspection",
                "Wood; mechanical long-term load; changes in structure geometry; visual inspection",
                "Wood; fungal decay; changes in density; electrical resistance",
                "Wood; fungal decay; changes in material macro- & microstructure; computed tomography",
                "Wood; insect attack; discontinuity of material; acoustic emission",
                "Wood; insect attack; changes in structure geometry; computed tomography",
                "Wood; insect attack; changes in material macro- & microstructure; X-ray imaging",
                "Wood; insect attack; changes in mechanical parameters; acoustic emission",
                "Wood; insect attack; changes in structure geometry; acoustic emission",
                "Wood; insect attack; changes in material macro- & microstructure; drilling resistance",
                "Wood; insect attack; changes in mechanical parameters; eigenfrequency measurements",
                "Wood; insect attack; changes in structure geometry; video image correlation",
                "Wood; insect attack; changes in material macro- & microstructure; thermography",
                "Wood; insect attack; changes in chemical constitution; chemical analyses using spectroscopy",
                "Wood; insect attack; changes in structure geometry; visual inspection",
                "Wood; insect attack; changes in material macro- & microstructure; classical microscopic methods",
                "Wood; insect attack; changes in structure geometry; strain measurements",
                "Wood; insect attack; changes in material macro- & microstructure; colour measurements",
                "Wood; insect attack; changes in structure geometry; delamination surveys",
                "Wood; insect attack; changes in material macro- & microstructure; computed tomography",
                "Wood; fungal decay; changes in structure geometry; X-ray/synchrotron",
                "Wood; fungal decay; changes in material macro- & microstructure; X-ray/synchrotron",
                "Wood; fungal decay; mechanical parameters; X-ray/synchrotron",
                "Wood; fungal decay; discontinuity of material; X-ray/synchrotron",
                "Wood; fungal decay; water & gas resistance; X-ray/synchrotron",
                "Wood; fungal decay; chemical constitution; X-ray/synchrotron",
                "Wood; oxidation; changes in structure geometry; Colour measurement/gloss level",
                "Wood; oxidation; changes in material macro- & microstructure; Colour measurement/gloss level",
                "Wood; oxidation; mechanical parameters; Colour measurement/gloss level",
                "Wood; oxidation; discontinuity of material; Colour measurement/gloss level",
                "Wood; oxidation; water & gas resistance; Colour measurement/gloss level",
                "Wood; oxidation; chemical constitution; Colour measurement/gloss level",
                "Wood; mechanical load; changes in structure geometry; Optical imaging methods (video image correlation)",
                "Wood; mechanical load; changes in material macro- & microstructure; Optical imaging methods (video image correlation)",
                "Wood; mechanical load; mechanical parameters; Optical imaging methods (video image correlation)",
                "Wood; mechanical load; discontinuity of material; Optical imaging methods (video image correlation)",
                "Wood; mechanical load; water & gas resistance; Optical imaging methods (video image correlation)",
                "Wood; mechanical load; chemical constitution; Optical imaging methods (video image correlation)",
                "Wood; moisture content; changes in structure geometry; Moisture measurement",
                "Wood; moisture content; changes in material macro- & microstructure; Moisture measurement",
                "Wood; moisture content; mechanical parameters; Moisture measurement",
                "Wood; moisture content; discontinuity of material; Moisture measurement",
                "Wood; moisture content; water & gas resistance; Moisture measurement",
                "Wood; moisture content; chemical constitution; Moisture measurement",
                "Wood; rot; changes in structure geometry; Electric resistance measurements",
                "Wood; rot; changes in material macro- & microstructure; Electric resistance measurements",
                "Wood; rot; mechanical parameters; Electric resistance measurements",
                "Wood; rot; discontinuity of material; Electric resistance measurements",
                "Wood; rot; water & gas resistance; Electric resistance measurements",
                "Wood; rot; chemical constitution; Electric resistance measurements",
                "Wood; knots; changes in structure geometry; Thermography",
                "Wood; knots; changes in material macro- & microstructure; Thermography",
                "Wood; knots; mechanical parameters; Thermography",
                "Wood; knots; discontinuity of material; Thermography",
                "Wood; knots; water & gas resistance; Thermography",
                "Wood; knots; chemical constitution; Thermography",
                "Wood; delamination; changes in structure geometry; Thermography",
                "Wood; delamination; changes in material macro- & microstructure; Thermography",
                "Wood; delamination; mechanical parameters; Thermography",
                "Wood; delamination; discontinuity of material; Thermography",
                "Wood; delamination; water & gas resistance; Thermography",
                "Wood; delamination; chemical constitution; Thermography",
                "Wood; fungal decay; mechanical parameters; thermography",
                "Wood; insect attack; discontinuity of material; radiography",
                "Wood; insect attack; water & gas resistance; neutron imaging",
                "Wood; UV exposure; chemical constitution; near-infrared spectroscopy",
            ],
            'Bricks': [
                "Bricks; salt crystallization; spalling; ultrasonic testing",
                "Bricks; weathering; cracking; visual inspection",
                "Bricks; weathering; spalling; visual inspection",
                "Bricks; weathering; efflorescence; visual inspection",
                "Bricks; salt crystallization; cracking; visual inspection",
                "Bricks; salt crystallization; spalling; visual inspection",
                "Bricks; salt crystallization; efflorescence; visual inspection",
                "Bricks; weathering; cracking; ultrasonic testing",
                "Bricks; weathering; spalling; ultrasonic testing",
                "Bricks; weathering; efflorescence; ultrasonic testing",
                "Bricks; salt crystallization; cracking; ultrasonic testing",
                "Bricks; salt crystallization; efflorescence; ultrasonic testing",
                "Bricks; weathering; cracking; infrared thermography",
                "Bricks; weathering; spalling; infrared thermography",
                "Bricks; weathering; efflorescence; infrared thermography",
                "Bricks; salt crystallization; cracking; infrared thermography",
                "Bricks; salt crystallization; spalling; infrared thermography",
                "Bricks; salt crystallization; efflorescence; infrared thermography",
                "Bricks; weathering; dimensional changes; visual inspection",
                "Bricks; salt crystallization; dimensional changes; ultrasonic testing",
                "Bricks; weathering; dimensional changes; ultrasonic testing",
                "Bricks; weathering; dimensional changes; infrared thermography",
                "Bricks; salt crystallization; dimensional changes; visual inspection",
                "Bricks; salt crystallization; dimensional changes; infrared thermography",
                "Bricks; weathering; cracking; impact-echo testing",
                "Bricks; salt crystallization; spalling; impact-echo testing",
                "Bricks; weathering; efflorescence; moisture meters",
                "Bricks; salt crystallization; efflorescence; moisture meters"
            ]
        }

        for material, data_entries in materials_data.items():
            for entry in data_entries:
                parts = entry.split(';')
                if len(parts) == 4:
                    mat, deterioration, physical_change, ndt_method = parts
                    session.write_transaction(create_deterioration_nodes, mat.strip(), deterioration.strip(), physical_change.strip(), ndt_method.strip())

if __name__ == "__main__":
    # Clear existing content
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    # Load new data
    load_data()
