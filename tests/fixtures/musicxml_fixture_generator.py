"""
Test fixtures for Semantic Diff testing
Creates minimal MusicXML files with known musical transformations
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom


def create_musicxml(parts_data, score_title="Test Score"):
    """Create basic MusicXML structure with given parts data"""
    
    # Create root scorewise element
    scorewise = ET.Element("score-partwise", version="4.0")
    
    # Add score header
    work = ET.SubElement(scorewise, "work")
    work.set("work-title", score_title)
    
    partlist = ET.SubElement(scorewise, "part-list")
    
    # Create parts
    for i, (part_name, measures_data) in enumerate(parts_data):
        # Add part to part list
        part_list_item = ET.SubElement(partlist, "score-part")
        part_list_item.set("id", f"P{i+1}")
        part_list_item.set("name", part_name)
        
        # Create part
        part = ET.SubElement(scorewise, "part")
        part.set("id", f"P{i+1}")
        
        # Add measures
        for j, (time_sig, notes) in enumerate(measures_data):
            measure = ET.SubElement(part, "measure")
            measure.set("number", str(j+1))
            
            # Add attributes (time signature)
            if time_sig:
                attributes = ET.SubElement(measure, "attributes")
                time = ET.SubElement(attributes, "time")
                beats_elem = ET.SubElement(time, "beats")
                beats_elem.text = time_sig.split('/')[0]
                beat_type = ET.SubElement(time, "beat-type")
                beat_type.text = time_sig.split('/')[1]
            
            # Add notes
            for note_data in notes:
                if note_data is None:  # Rest
                    rest = ET.SubElement(measure, "rest")
                    measure.append(rest)
                else:  # Note
                    note = ET.SubElement(measure, "note")
                    pitch = ET.SubElement(note, "pitch")
                    step = ET.SubElement(pitch, "step")
                    step.text = note_data['step']
                    alter = ET.SubElement(pitch, "alter")
                    alter.text = str(note_data.get('alter', 0))
                    octave = ET.SubElement(pitch, "octave")
                    octave.text = str(note_data['octave'])
                    
                    duration = ET.SubElement(note, "duration")
                    duration.text = str(note_data['duration'])
                    measure.append(note)
    
    return scorewise


def prettify_xml(element):
    """Convert XML element to pretty string"""
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# Note definitions
C4 = {'step': 'C', 'octave': 4, 'duration': 4}      # Quarter note
D4 = {'step': 'D', 'octave': 4, 'duration': 4}      
E4 = {'step': 'E', 'octave': 4, 'duration': 4}      
F4 = {'step': 'F', 'octave': 4, 'duration': 4}      
G4 = {'step': 'G', 'octave': 4, 'duration': 4}      
A4 = {'step': 'A', 'octave': 4, 'duration': 4}      
B4 = {'step': 'B', 'octave': 4, 'duration': 4}      

D4_sharp = {'step': 'D', 'octave': 4, 'alter': 1, 'duration': 4}
F4_sharp = {'step': 'F', 'octave': 4, 'alter': 1, 'duration': 4}

# Transposed versions (+2 semitones)
D4 = {'step': 'D', 'octave': 4, 'duration': 4}      
E4 = {'step': 'E', 'octave': 4, 'duration': 4}      
F4_sharp = {'step': 'F', 'octave': 4, 'alter': 1, 'duration': 4}      
G4 = {'step': 'G', 'octave': 4, 'duration': 4}      
A4 = {'step': 'A', 'octave': 4, 'duration': 4}      
B4 = {'step': 'B', 'octave': 4, 'duration': 4}      
C5 = {'step': 'C', 'octave': 5, 'duration': 4}      

# Transposed versions (+2 semitones)
D4 = {'step': 'D', 'octave': 4, 'duration': 4}      
E4 = {'step': 'E', 'octave': 4, 'duration': 4}      
F4_sharp = {'step': 'F', 'octave': 4, 'alter': 1, 'duration': 4}      
G4 = {'step': 'G', 'octave': 4, 'duration': 4}      
A4 = {'step': 'A', 'octave': 4, 'duration': 4}      
B4 = {'step': 'B', 'octave': 4, 'duration': 4}      
C5 = {'step': 'C', 'octave': 5, 'duration': 4}      

# Rhythm simplified versions
C4_whole = {'step': 'C', 'octave': 4, 'duration': 16}     # Whole note
C4_half = {'step': 'C', 'octave': 4, 'duration': 2}        # Half note
C4_quarter = {'step': 'C', 'octave': 4, 'duration': 1}       # Quarter note