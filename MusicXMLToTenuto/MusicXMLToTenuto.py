import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
import zipfile
import io
import os

class TenutoState:
    """Tracks the 'Sticky State' for a specific voice to optimize output."""
    def __init__(self):
        self.last_duration = None # e.g., "4" or "8."
        self.last_octave = None   # e.g., 4
        
    def reset(self):
        pass

class MusicXMLToTenuto:
    def __init__(self, filepath):
        # --- Handle Compressed .mxl files ---
        if filepath.lower().endswith('.mxl'):
            with zipfile.ZipFile(filepath, 'r') as z:
                # Find the main XML file inside the container
                xml_filename = None
                for name in z.namelist():
                    if name.endswith('.xml') and not name.startswith('META-INF'):
                        xml_filename = name
                        break
                
                if not xml_filename:
                    raise ValueError("Could not find a valid .xml file inside the .mxl archive.")
                
                with z.open(xml_filename) as f:
                    xml_content = f.read()
                    self.tree = ET.parse(io.BytesIO(xml_content))
        else:
            # Standard text file
            self.tree = ET.parse(filepath)
        # ----------------------------------------

        self.root = self.tree.getroot()
        
        # Handle Namespace (MusicXML files often have xmlns="...")
        if not self.root.tag.startswith('{'):
            self.tag_prefix = ""
        else:
            self.tag_prefix = self.root.tag.split('}')[0] + '}'

        # Data Stores
        self.parts_info = {} # {xml_id: {tenuto_id, name}}
        self.global_meta = {}
        # pivot_data[measure_num][tenuto_id] = [EventString, EventString...]
        self.pivot_data = defaultdict(lambda: defaultdict(list)) 
        self.divisions_per_quarter = 1 

    def get_tag(self, elem, tag_name):
        return elem.find(f"{self.tag_prefix}{tag_name}")

    def get_text(self, elem, tag_name, default=None):
        t = self.get_tag(elem, tag_name)
        return t.text if t is not None else default

    def parse_structure(self):
        """Phase 1: Parse Meta and Definitions"""
        # 1. Meta
        work = self.get_tag(self.root, 'work')
        if work:
            self.global_meta['title'] = self.get_text(work, 'work-title', "Untitled")
        
        ident = self.get_tag(self.root, 'identification')
        if ident:
            creator = self.get_tag(ident, 'creator') 
            if creator is not None:
                self.global_meta['composer'] = creator.text

        # 2. Part Definitions
        part_list = self.get_tag(self.root, 'part-list')
        if part_list:
            for score_part in part_list.findall(f"{self.tag_prefix}score-part"):
                pid = score_part.attrib['id']
                name = self.get_text(score_part, 'part-name', 'Instrument')
                
                # Generate a Tenuto-friendly ID (e.g., "Violin I" -> "vln1")
                slug = "".join([c for c in name.lower() if c.isalnum()])[:4]
                if not slug: slug = "inst"
                
                # Handle duplicates
                count = 1
                base_slug = slug
                while any(p['tenuto_id'] == slug for p in self.parts_info.values()):
                    slug = f"{base_slug}{count}"
                    count += 1
                
                self.parts_info[pid] = {
                    "tenuto_id": slug,
                    "name": name,
                    "state": TenutoState() 
                }

    def calculate_tenuto_duration(self, duration_ticks):
        """Converts XML ticks to Tenuto duration string."""
        if duration_ticks is None: return ":4"
        
        try:
            quarters = float(duration_ticks) / float(self.divisions_per_quarter)
        except ZeroDivisionError:
            return ":4"
        
        # Standard mappings
        if quarters == 4.0: return ":1"
        if quarters == 3.0: return ":2."
        if quarters == 2.0: return ":2"
        if quarters == 1.5: return ":4."
        if quarters == 1.0: return ":4"
        if quarters == 0.75: return ":8."
        if quarters == 0.5: return ":8"
        if quarters == 0.375: return ":16." # Dotted 16th
        if quarters == 0.25: return ":16"
        if quarters == 0.125: return ":32"
        
        return ":4" # Fallback

    def parse_pitch(self, note_xml, state):
        """Parses pitch and applies Sticky State logic."""
        pitch = self.get_tag(note_xml, 'pitch')
        if pitch is None: return "r" # It's a rest
        
        step = self.get_text(pitch, 'step').lower()
        alter = self.get_text(pitch, 'alter')
        octave = self.get_text(pitch, 'octave')
        
        # Calculate Accidental
        acc = ""
        if alter == "1": acc = "#"
        elif alter == "-1": acc = "b"
        elif alter == "2": acc = "x"
        elif alter == "-2": acc = "bb"
        
        token = f"{step}{acc}"
        
        # Sticky Octave Logic
        if state.last_octave == octave:
            pass 
        else:
            token += octave
            state.last_octave = octave
            
        return token

    def process_attributes(self, meas_xml):
        """Updates global physics like divisions or time signature."""
        attrs = self.get_tag(meas_xml, 'attributes')
        meta_changes = []
        
        if attrs is not None:
            # Update Divisions
            divs = self.get_text(attrs, 'divisions')
            if divs:
                self.divisions_per_quarter = int(divs)
                
            # Time Signature
            time = self.get_tag(attrs, 'time')
            if time is not None:
                beats = self.get_text(time, 'beats')
                beat_type = self.get_text(time, 'beat-type')
                meta_changes.append(f"time: {beats}/{beat_type}")
                
        return meta_changes

    def parse_logic(self):
        """Phase 2: Linearize MusicXML Logic"""
        
        for part in self.root.findall(f"{self.tag_prefix}part"):
            pid = part.attrib['id']
            if pid not in self.parts_info: continue
            
            p_info = self.parts_info[pid]
            tenuto_id = p_info['tenuto_id']
            state = p_info['state']
            
            measure_index = 1
            
            for measure in part.findall(f"{self.tag_prefix}measure"):
                # 1. Check for Meta changes
                meta_updates = self.process_attributes(measure)
                if meta_updates:
                    self.pivot_data[measure_index]['__meta__'] = meta_updates

                # 2. Process Notes
                current_voice_tokens = []
                
                notes = measure.findall(f"{self.tag_prefix}note")
                i = 0
                while i < len(notes):
                    note = notes[i]
                    
                    # Handle Chord (look ahead)
                    chord_stack = [note]
                    
                    # Look ahead for <chord/> tags
                    j = i + 1
                    while j < len(notes):
                        next_note = notes[j]
                        if self.get_tag(next_note, 'chord') is not None:
                            chord_stack.append(next_note)
                            j += 1
                        else:
                            break
                    
                    # Logic for the primary note
                    duration_xml = self.get_text(chord_stack[0], 'duration')
                    ten_dur = self.calculate_tenuto_duration(duration_xml)
                    
                    # Construct Pitch Token(s)
                    if len(chord_stack) > 1:
                        # Chord
                        pitches = [self.parse_pitch(n, state) for n in chord_stack]
                        # Remove 'r' from chords if mixed (weird XML edge case)
                        pitches = [p for p in pitches if p != 'r']
                        token = f"[{' '.join(pitches)}]"
                    else:
                        # Single
                        token = self.parse_pitch(chord_stack[0], state)
                    
                    # Sticky Duration Logic
                    if state.last_duration == ten_dur:
                        pass # Omit duration
                    else:
                        token += f"{ten_dur}"
                        state.last_duration = ten_dur
                        
                    # Handle Notations
                    notations = self.get_tag(chord_stack[0], 'notations')
                    if notations is not None:
                        arts = self.get_tag(notations, 'articulations')
                        if arts is not None:
                            if self.get_tag(arts, 'staccato') is not None: token += ".stacc"
                            if self.get_tag(arts, 'accent') is not None: token += ".acc"
                            if self.get_tag(arts, 'tenuto') is not None: token += ".ten"
                            
                        slur = self.get_tag(notations, 'slur')
                        if slur is not None and slur.attrib.get('type') == 'start':
                            token += ".legato" 

                    current_voice_tokens.append(token)
                    i = j
                
                self.pivot_data[measure_index][tenuto_id] = current_voice_tokens
                measure_index += 1

    def generate_tenuto(self):
        """Phase 3: Render Output"""
        lines = []
        lines.append("tenuto {")
        
        # Meta Block
        lines.append("  meta {")
        lines.append(f'    tenuto_version: "2.0",')
        for k, v in self.global_meta.items():
            lines.append(f'    {k}: "{v}",')
        lines.append("  }")
        lines.append("")
        
        # Defs Block
        lines.append("  %% Instrument Definitions")
        for pid, info in self.parts_info.items():
            lines.append(f'  def {info["tenuto_id"]} "{info["name"]}" style=standard')
        lines.append("")
        
        # Logic Stream (Pivot)
        lines.append("  %% Score Logic")
        sorted_measures = sorted(self.pivot_data.keys())
        
        for m_idx in sorted_measures:
            data = self.pivot_data[m_idx]
            
            lines.append(f"  measure {m_idx} {{")
            
            # Write Measure Meta
            if '__meta__' in data:
                meta_str = ", ".join(data['__meta__'])
                lines.append(f"    meta {{ {meta_str} }}")
            
            # Write Part Data
            for pid, info in self.parts_info.items():
                tid = info['tenuto_id']
                if tid in data:
                    events = " ".join(data[tid])
                    lines.append(f"    {tid}: {events} |")
            
            lines.append("  }")
            lines.append("")
            
        lines.append("}")
        return "\n".join(lines)

# --- Execution ---
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        
        # Auto-generate output filename if not provided
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            # Strip extension (like .mxl) and add .ten
            base_name, _ = os.path.splitext(input_file)
            output_file = base_name + ".ten"

        try:
            print(f"Reading {input_file}...")
            converter = MusicXMLToTenuto(input_file)
            
            print("Parsing structure...")
            converter.parse_structure()
            
            print("Converting logic...")
            converter.parse_logic()
            
            print(f"Writing to {output_file}...")
            tenuto_code = converter.generate_tenuto()
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(tenuto_code)
            
            print("Done! Success.")
            
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
    else:
        print("Usage: python MusicXMLToTenuto.py <file.mxl> [output.ten]")
