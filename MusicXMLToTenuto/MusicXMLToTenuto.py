"""
MusicXML to Tenuto Converter (v1.1 - With Dynamics)
===================================================

Changes in v1.1:
- Added 'Sequential Stream Parsing' in parse_logic to catch <direction> tags.
- Added support for Dynamics (.pp, .ff, .mp, etc.).
- Robust handling of mixed XML tags (attributes, notes, directions).

"""

import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
import zipfile
import io
import os
from typing import Optional, Dict, List, Any

# =============================================================================
# State Management
# =============================================================================

class TenutoState:
    """Tracks the 'Sticky State' for a specific voice."""
    def __init__(self):
        self.last_duration: Optional[str] = None 
        self.last_octave: Optional[str] = None   

    def reset(self):
        self.last_duration = None
        self.last_octave = None


# =============================================================================
# Main Converter Class
# =============================================================================

class MusicXMLToTenuto:
    def __init__(self, filepath: str):
        self.filepath = filepath
        
        # --- File Ingestion ---
        if filepath.lower().endswith('.mxl'):
            with zipfile.ZipFile(filepath, 'r') as z:
                xml_filename = None
                for name in z.namelist():
                    if name.endswith('.xml') and not name.startswith('META-INF'):
                        xml_filename = name
                        break
                if not xml_filename:
                    raise ValueError(f"Invalid .mxl file: No root XML found.")
                with z.open(xml_filename) as f:
                    self.tree = ET.parse(io.BytesIO(f.read()))
        else:
            self.tree = ET.parse(filepath)

        self.root = self.tree.getroot()
        
        # --- Namespace Handling ---
        if not self.root.tag.startswith('{'):
            self.tag_prefix = ""
        else:
            self.tag_prefix = self.root.tag.split('}')[0] + '}'

        # --- Data Structures ---
        self.parts_info: Dict[str, Any] = {} 
        self.global_meta: Dict[str, str] = {}
        self.pivot_data = defaultdict(lambda: defaultdict(list)) 
        self.divisions_per_quarter = 1 

    def get_tag(self, elem: ET.Element, tag_name: str) -> Optional[ET.Element]:
        return elem.find(f"{self.tag_prefix}{tag_name}")

    def get_text(self, elem: ET.Element, tag_name: str, default: Any = None) -> Any:
        t = self.get_tag(elem, tag_name)
        return t.text if t is not None else default

    # =========================================================================
    # Phase 1: Structure Analysis
    # =========================================================================

    def parse_structure(self):
        # 1. Title
        work = self.get_tag(self.root, 'work')
        if work:
            self.global_meta['title'] = self.get_text(work, 'work-title', "Untitled")
        
        # 2. Composer
        ident = self.get_tag(self.root, 'identification')
        if ident:
            creator = self.get_tag(ident, 'creator') 
            if creator is not None:
                self.global_meta['composer'] = creator.text

        # 3. Instruments
        part_list = self.get_tag(self.root, 'part-list')
        if part_list:
            for score_part in part_list.findall(f"{self.tag_prefix}score-part"):
                pid = score_part.attrib['id']
                name = self.get_text(score_part, 'part-name', 'Instrument')
                
                slug = "".join([c for c in name.lower() if c.isalnum()])[:4]
                if not slug: slug = "inst"
                
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

    # =========================================================================
    # Phase 2: Logic Parsing & Tokenization
    # =========================================================================

    def calculate_tenuto_duration(self, duration_ticks: str) -> str:
        if duration_ticks is None: return ":4"
        try:
            quarters = float(duration_ticks) / float(self.divisions_per_quarter)
        except ZeroDivisionError:
            return ":4"
        
        if quarters == 4.0: return ":1"
        if quarters == 3.0: return ":2."
        if quarters == 2.0: return ":2"
        if quarters == 1.5: return ":4."
        if quarters == 1.0: return ":4"
        if quarters == 0.75: return ":8."
        if quarters == 0.5: return ":8"
        if quarters == 0.375: return ":16."
        if quarters == 0.25: return ":16"
        if quarters == 0.125: return ":32"
        return ":4" 

    def parse_pitch(self, note_xml: ET.Element, state: TenutoState) -> str:
        pitch = self.get_tag(note_xml, 'pitch')
        if pitch is None: return "r"
        
        step = self.get_text(pitch, 'step').lower()
        alter = self.get_text(pitch, 'alter')
        octave = self.get_text(pitch, 'octave')
        
        acc = ""
        if alter == "1": acc = "#"
        elif alter == "-1": acc = "b"
        elif alter == "2": acc = "x"
        elif alter == "-2": acc = "bb"
        
        token = f"{step}{acc}"
        
        if state.last_octave == octave:
            pass 
        else:
            token += octave
            state.last_octave = octave
            
        return token

    def parse_dynamic(self, direction_xml: ET.Element) -> Optional[str]:
        """
        Drills down into <direction> -> <direction-type> -> <dynamics>
        Returns the Tenuto dot-modifier (e.g., ".pp") or None.
        """
        dt = self.get_tag(direction_xml, 'direction-type')
        if dt is None: return None
        
        # Check for Dynamics
        dyn = self.get_tag(dt, 'dynamics')
        if dyn is not None:
            # The XML tag name itself is the dynamic (e.g., <p/>, <ff/>)
            # We take the first child of the dynamics tag
            if len(dyn) > 0:
                tag_name = dyn[0].tag.replace(self.tag_prefix, "")
                return f".{tag_name}" # .p, .ff, .sfz
                
        return None

    def process_attributes(self, meas_xml: ET.Element) -> List[str]:
        attrs = self.get_tag(meas_xml, 'attributes')
        meta_changes = []
        if attrs is not None:
            divs = self.get_text(attrs, 'divisions')
            if divs: self.divisions_per_quarter = int(divs)
            time = self.get_tag(attrs, 'time')
            if time is not None:
                beats = self.get_text(time, 'beats')
                beat_type = self.get_text(time, 'beat-type')
                meta_changes.append(f"time: {beats}/{beat_type}")
        return meta_changes

    def parse_logic(self):
        """
        The Core Loop: Iterates over children of the Measure to preserve order
        of Dynamics vs Notes.
        """
        
        for part in self.root.findall(f"{self.tag_prefix}part"):
            pid = part.attrib['id']
            if pid not in self.parts_info: continue
            
            p_info = self.parts_info[pid]
            tenuto_id = p_info['tenuto_id']
            state = p_info['state']
            
            measure_index = 1
            
            for measure in part.findall(f"{self.tag_prefix}measure"):
                
                # 1. Global Attributes
                meta_updates = self.process_attributes(measure)
                if meta_updates:
                    self.pivot_data[measure_index]['__meta__'] = meta_updates

                # 2. Sequential Stream Processing
                current_voice_tokens = []
                
                # We collect dynamics found BEFORE a note, then apply them to the note.
                pending_attributes = []
                
                # Iterating children directly ensures we see <direction> before <note>
                # However, <note><chord/> tags are siblings. We must be careful.
                
                # We collect all elements first to handle index skipping for chords
                elements = list(measure)
                i = 0
                while i < len(elements):
                    elem = elements[i]
                    tag = elem.tag.replace(self.tag_prefix, "")
                    
                    if tag == 'direction':
                        # Try to parse a dynamic
                        dyn = self.parse_dynamic(elem)
                        if dyn:
                            pending_attributes.append(dyn)
                        
                        i += 1
                        continue
                        
                    elif tag == 'note':
                        # Check if this is a chord member (has <chord/> tag)
                        # The FIRST note of a chord group absorbs the previous dynamics
                        # Subsequent notes in the chord inherit them implicitly via the chord object
                        
                        chord_stack = [elem]
                        j = i + 1
                        while j < len(elements):
                            next_elem = elements[j]
                            next_tag = next_elem.tag.replace(self.tag_prefix, "")
                            if next_tag == 'note' and self.get_tag(next_elem, 'chord') is not None:
                                chord_stack.append(next_elem)
                                j += 1
                            elif next_tag == 'note':
                                # It's a new note, stop.
                                break
                            else:
                                # It's a direction/backup/forward, stop chord collection but don't consume index
                                # Actually, <forward> or <backup> breaks chords anyway.
                                break

                        # Logic for duration (from first note)
                        duration_xml = self.get_text(chord_stack[0], 'duration')
                        ten_dur = self.calculate_tenuto_duration(duration_xml)
                        
                        # Pitch Generation
                        if len(chord_stack) > 1:
                            pitches = [self.parse_pitch(n, state) for n in chord_stack]
                            pitches = [p for p in pitches if p != 'r']
                            token = f"[{' '.join(pitches)}]"
                        else:
                            token = self.parse_pitch(chord_stack[0], state)
                        
                        # Sticky Duration
                        if state.last_duration == ten_dur:
                            pass 
                        else:
                            token += f"{ten_dur}"
                            state.last_duration = ten_dur
                        
                        # --- Apply Pending Dynamics ---
                        if pending_attributes:
                            # Attach .pp .acc etc to this token
                            token += "".join(pending_attributes)
                            # Clear buffer
                            pending_attributes = []

                        # Articulations (Standard notations inside the note tag)
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
                        
                        # Jump index past chord
                        i = j
                        continue

                    # Skip other tags (backup, forward, print, barline)
                    i += 1
                
                self.pivot_data[measure_index][tenuto_id] = current_voice_tokens
                measure_index += 1

    # =========================================================================
    # Phase 3: Code Generation
    # =========================================================================

    def generate_tenuto(self) -> str:
        lines = []
        lines.append("tenuto {")
        
        lines.append("  meta {")
        lines.append(f'    tenuto_version: "2.0",')
        for k, v in self.global_meta.items():
            safe_val = v.replace('"', '\\"')
            lines.append(f'    {k}: "{safe_val}",')
        lines.append("  }")
        lines.append("")
        
        lines.append("  %% Instrument Definitions")
        for pid, info in self.parts_info.items():
            lines.append(f'  def {info["tenuto_id"]} "{info["name"]}" style=standard')
        lines.append("")
        
        lines.append("  %% Score Logic")
        sorted_measures = sorted(self.pivot_data.keys())
        
        for m_idx in sorted_measures:
            data = self.pivot_data[m_idx]
            lines.append(f"  measure {m_idx} {{")
            
            if '__meta__' in data:
                meta_str = ", ".join(data['__meta__'])
                lines.append(f"    meta {{ {meta_str} }}")
            
            for pid, info in self.parts_info.items():
                tid = info['tenuto_id']
                if tid in data:
                    events = " ".join(data[tid])
                    lines.append(f"    {tid}: {events} |")
            lines.append("  }")
            lines.append("")
            
        lines.append("}")
        return "\n".join(lines)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            base_name, _ = os.path.splitext(input_file)
            output_file = base_name + ".ten"

        try:
            print(f"Reading {input_file}...")
            converter = MusicXMLToTenuto(input_file)
            
            print("Phase 1: Parsing Structure...")
            converter.parse_structure()
            
            print("Phase 2: Converting Logic (with Dynamics)...")
            converter.parse_logic()
            
            print(f"Phase 3: Writing to {output_file}...")
            tenuto_code = converter.generate_tenuto()
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(tenuto_code)
            print("Done!")
            
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
    else:
        print("Usage: python MusicXMLToTenuto.py <file.mxl> [output.ten]")
