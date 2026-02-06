"""
MusicXML to Tenuto Converter (v1.0)
===================================

This module translates MusicXML (both .xml text and .mxl compressed archives) 
into the Tenuto v2.0 domain-specific language.

Architecture Overview:
----------------------
1.  **Input Abstraction**: Automatically detects gzip/zip compression (.mxl) and 
    extracts the score data into an in-memory XML tree.
2.  **The Pivot**: MusicXML is hierarchical by Part -> Measure. Tenuto is 
    hierarchical by Measure -> Part (Time-slice oriented). This script pivots 
    the data structure using a `pivot_data` dictionary.
3.  **Inference Engine**: Tenuto relies on "Sticky State" (omitting data that 
    hasn't changed). The `TenutoState` class tracks the context of every voice 
    to minimize output verbosity, strictly adhering to the "Inference Over 
    Redundancy" philosophy.

Usage:
------
    python MusicXMLToTenuto.py input.mxl [output.ten]

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
    """
    Maintains the 'Sticky State' context for a single musical voice.
    
    In Tenuto, if a note has the same duration or octave as the previous note,
    those attributes are omitted. This class tracks that history to determine
    when explicit definitions are required.
    """
    def __init__(self):
        # The last explicitly written duration (e.g., ":4", ":8.")
        # initialized to None so the first note always writes its duration.
        self.last_duration: Optional[str] = None 
        
        # The last explicitly written octave integer (e.g., "4", "5")
        self.last_octave: Optional[str] = None   

    def reset(self):
        """
        Resets state to defaults. 
        
        Note: Currently unused as Tenuto v2 allows state to flow across bar lines.
        If 'Strict Mode' were implemented, this would be called at every measure.
        """
        self.last_duration = None
        self.last_octave = None


# =============================================================================
# Main Converter Class
# =============================================================================

class MusicXMLToTenuto:
    def __init__(self, filepath: str):
        """
        Initializes the converter by loading and parsing the XML tree.

        Args:
            filepath (str): Path to .xml or .mxl file.

        Raises:
            ValueError: If an .mxl archive does not contain a valid XML file.
            ET.ParseError: If the XML is malformed.
        """
        self.filepath = filepath
        
        # --- Step 1: File Ingestion Strategy ---
        # Check if the file is a compressed MusicXML archive (.mxl)
        if filepath.lower().endswith('.mxl'):
            with zipfile.ZipFile(filepath, 'r') as z:
                # Strategy: Valid .mxl files usually contain a META-INF/container.xml 
                # pointing to the rootfile. However, some export tools omit this.
                # Robust Fallback: Scan for the first non-meta .xml file.
                xml_filename = None
                for name in z.namelist():
                    if name.endswith('.xml') and not name.startswith('META-INF'):
                        xml_filename = name
                        break
                
                if not xml_filename:
                    raise ValueError(f"Invalid .mxl file: No root XML found in {filepath}")
                
                # Unzip into memory (BytesIO) to avoid writing temporary files to disk
                with z.open(xml_filename) as f:
                    xml_content = f.read()
                    self.tree = ET.parse(io.BytesIO(xml_content))
        else:
            # Standard text-based XML file
            self.tree = ET.parse(filepath)

        self.root = self.tree.getroot()
        
        # --- Step 2: Namespace Handling ---
        # MusicXML usually defines a default namespace (e.g., xmlns="...").
        # ElementTree prepends this namespace to every tag in {curly_braces}.
        # We detect this prefix once to use in all find() calls.
        if not self.root.tag.startswith('{'):
            self.tag_prefix = ""
        else:
            self.tag_prefix = self.root.tag.split('}')[0] + '}'

        # --- Step 3: Initialize Data Structures ---
        
        # Maps XML Part IDs (e.g., "P1") to Tenuto metadata
        # Structure: { 'P1': {'tenuto_id': 'vln1', 'name': 'Violin', 'state': TenutoState()} }
        self.parts_info: Dict[str, Any] = {} 
        
        # Stores global score metadata (Title, Composer, Copyright)
        self.global_meta: Dict[str, str] = {}
        
        # The Pivot Table: Stores linearized events keyed by [Measure][Instrument]
        # This allows us to write "Measure 1 { Vln: ... Vlc: ... }" effectively.
        self.pivot_data = defaultdict(lambda: defaultdict(list)) 
        
        # Ticks per Quarter Note (MusicXML <divisions>). Defaults to 1 until parsed.
        self.divisions_per_quarter = 1 

    def get_tag(self, elem: ET.Element, tag_name: str) -> Optional[ET.Element]:
        """Helper to find a child tag handling the XML Namespace prefix automatically."""
        return elem.find(f"{self.tag_prefix}{tag_name}")

    def get_text(self, elem: ET.Element, tag_name: str, default: Any = None) -> Any:
        """Helper to safely extract text content from a child tag."""
        t = self.get_tag(elem, tag_name)
        return t.text if t is not None else default

    # =========================================================================
    # Phase 1: Structure Analysis
    # =========================================================================

    def parse_structure(self):
        """
        Scans the XML header to extract global metadata and Part Definitions.
        Populates self.global_meta and self.parts_info.
        """
        # 1. Extract Work Title
        work = self.get_tag(self.root, 'work')
        if work:
            self.global_meta['title'] = self.get_text(work, 'work-title', "Untitled")
        
        # 2. Extract Composer
        ident = self.get_tag(self.root, 'identification')
        if ident:
            creator = self.get_tag(ident, 'creator') 
            if creator is not None:
                self.global_meta['composer'] = creator.text

        # 3. Define Instruments (The Physics)
        part_list = self.get_tag(self.root, 'part-list')
        if part_list:
            for score_part in part_list.findall(f"{self.tag_prefix}score-part"):
                pid = score_part.attrib['id'] # e.g., "P1"
                name = self.get_text(score_part, 'part-name', 'Instrument')
                
                # Sanitization: Convert "Violin I" -> "vln1"
                # Keep only alphanumeric chars, lowercase, limit length for readability
                slug = "".join([c for c in name.lower() if c.isalnum()])[:4]
                if not slug: slug = "inst"
                
                # Collision Detection: Ensure IDs are unique
                # If "vln" exists, next becomes "vln1", then "vln2"
                count = 1
                base_slug = slug
                while any(p['tenuto_id'] == slug for p in self.parts_info.values()):
                    slug = f"{base_slug}{count}"
                    count += 1
                
                # Register the part and initialize its tracking state
                self.parts_info[pid] = {
                    "tenuto_id": slug,
                    "name": name,
                    "state": TenutoState() 
                }

    # =========================================================================
    # Phase 2: Logic Parsing & Tokenization
    # =========================================================================

    def calculate_tenuto_duration(self, duration_ticks: str) -> str:
        """
        Converts MusicXML integer ticks into Tenuto duration syntax.
        
        Formula: 
            Quarters = Ticks / Divisions
            Tenuto Value = 1 / Quarters (mostly)
            
        Args:
            duration_ticks: The integer string from <duration> tag.
            
        Returns:
            String like ":4", ":8", ":16."
        """
        if duration_ticks is None: return ":4"
        
        try:
            quarters = float(duration_ticks) / float(self.divisions_per_quarter)
        except ZeroDivisionError:
            # Fallback if XML is malformed (divisions=0)
            return ":4"
        
        # Map common float values to Tenuto reciprocal syntax
        # Note: 4.0 quarters = Whole Note (:1), 1.0 quarter = Quarter Note (:4)
        if quarters == 4.0: return ":1"
        if quarters == 3.0: return ":2."  # Dotted Half
        if quarters == 2.0: return ":2"   # Half
        if quarters == 1.5: return ":4."  # Dotted Quarter
        if quarters == 1.0: return ":4"   # Quarter
        if quarters == 0.75: return ":8." # Dotted Eighth
        if quarters == 0.5: return ":8"   # Eighth
        if quarters == 0.375: return ":16." # Dotted 16th
        if quarters == 0.25: return ":16"   # 16th
        if quarters == 0.125: return ":32"  # 32nd
        
        # Fallback for tuplets or weird quantization errors.
        # Ideally, we would detect tuplets here, but defaulting to :4 ensures
        # the file is readable, even if rhythmically incorrect.
        return ":4" 

    def parse_pitch(self, note_xml: ET.Element, state: TenutoState) -> str:
        """
        Generates the pitch token (e.g., "c#4") and applies Sticky State inference.

        Args:
            note_xml: The <note> element.
            state: The TenutoState object for the current voice.
        """
        pitch = self.get_tag(note_xml, 'pitch')
        if pitch is None: return "r" # <rest> tags have no pitch
        
        # Extract components
        step = self.get_text(pitch, 'step').lower()
        alter = self.get_text(pitch, 'alter') # -1, 1, etc.
        octave = self.get_text(pitch, 'octave')
        
        # Map numeric alteration to visual accidentals
        acc = ""
        if alter == "1": acc = "#"
        elif alter == "-1": acc = "b"
        elif alter == "2": acc = "x"     # Double Sharp
        elif alter == "-2": acc = "bb"   # Double Flat
        
        token = f"{step}{acc}"
        
        # --- Inference Logic ---
        # If the octave matches the previous note in this voice, omit it.
        # This significantly reduces file size and visual clutter.
        if state.last_octave == octave:
            pass 
        else:
            token += octave
            state.last_octave = octave
            
        return token

    def process_attributes(self, meas_xml: ET.Element) -> List[str]:
        """
        Detects changes in global physics (Key, Time, Tempo) within a measure.
        Updates self.divisions_per_quarter dynamically.
        """
        attrs = self.get_tag(meas_xml, 'attributes')
        meta_changes = []
        
        if attrs is not None:
            # <divisions> can change mid-piece! We must update our divider.
            divs = self.get_text(attrs, 'divisions')
            if divs:
                self.divisions_per_quarter = int(divs)
                
            # Time Signature Change
            time = self.get_tag(attrs, 'time')
            if time is not None:
                beats = self.get_text(time, 'beats')
                beat_type = self.get_text(time, 'beat-type')
                meta_changes.append(f"time: {beats}/{beat_type}")
        
        return meta_changes

    def parse_logic(self):
        """
        The Core Loop: Iterates over Parts -> Measures -> Notes.
        Populates self.pivot_data with the translated Tenuto tokens.
        """
        
        # Iterate over every Part found in the XML
        for part in self.root.findall(f"{self.tag_prefix}part"):
            pid = part.attrib['id']
            # Skip parts that weren't defined in the header (rare but possible)
            if pid not in self.parts_info: continue
            
            p_info = self.parts_info[pid]
            tenuto_id = p_info['tenuto_id']
            state = p_info['state']
            
            measure_index = 1
            
            # Iterate over every Measure in this Part
            for measure in part.findall(f"{self.tag_prefix}measure"):
                
                # 1. Check for Meta/Global changes (Time Sig, etc.)
                # We store this in a special '__meta__' key for the measure.
                meta_updates = self.process_attributes(measure)
                if meta_updates:
                    self.pivot_data[measure_index]['__meta__'] = meta_updates

                # 2. Process Notes (The logic stream)
                current_voice_tokens = []
                notes = measure.findall(f"{self.tag_prefix}note")
                
                i = 0
                while i < len(notes):
                    note = notes[i]
                    
                    # --- Chord Detection Strategy ---
                    # MusicXML stores chords as sequential <note> tags where subsequent
                    # notes contain a <chord/> empty tag. We must look ahead to group them.
                    chord_stack = [note]
                    
                    j = i + 1
                    while j < len(notes):
                        next_note = notes[j]
                        # Check if next note is part of the chord
                        if self.get_tag(next_note, 'chord') is not None:
                            chord_stack.append(next_note)
                            j += 1
                        else:
                            break
                    
                    # Logic for the event duration (taken from the first note of the group)
                    duration_xml = self.get_text(chord_stack[0], 'duration')
                    ten_dur = self.calculate_tenuto_duration(duration_xml)
                    
                    # --- Token Generation ---
                    if len(chord_stack) > 1:
                        # It's a chord: generate [ pitch1 pitch2 ]
                        pitches = [self.parse_pitch(n, state) for n in chord_stack]
                        # Sanitize: Remove 'r' from chords if XML oddly mixes rests/notes
                        pitches = [p for p in pitches if p != 'r']
                        token = f"[{' '.join(pitches)}]"
                    else:
                        # It's a single note
                        token = self.parse_pitch(chord_stack[0], state)
                    
                    # --- Duration Inference ---
                    # If duration matches previous note, omit it (Sticky State)
                    if state.last_duration == ten_dur:
                        pass 
                    else:
                        token += f"{ten_dur}"
                        state.last_duration = ten_dur
                        
                    # --- Articulation & Notations ---
                    # Check for staccato, accents, etc.
                    notations = self.get_tag(chord_stack[0], 'notations')
                    if notations is not None:
                        arts = self.get_tag(notations, 'articulations')
                        if arts is not None:
                            # Map XML tags to Tenuto Dot Modifiers
                            if self.get_tag(arts, 'staccato') is not None: token += ".stacc"
                            if self.get_tag(arts, 'accent') is not None: token += ".acc"
                            if self.get_tag(arts, 'tenuto') is not None: token += ".ten"
                            
                        # Slurs (Start only, Tenuto inference handles the curve)
                        slur = self.get_tag(notations, 'slur')
                        if slur is not None and slur.attrib.get('type') == 'start':
                            token += ".legato" 

                    current_voice_tokens.append(token)
                    
                    # Jump the index forward past the chord members we just processed
                    i = j
                
                # Store the result in the Pivot Table
                self.pivot_data[measure_index][tenuto_id] = current_voice_tokens
                measure_index += 1

    # =========================================================================
    # Phase 3: Code Generation
    # =========================================================================

    def generate_tenuto(self) -> str:
        """
        Transpiles the internal data structures into the final .ten source code.
        """
        lines = []
        lines.append("tenuto {")
        
        # 1. Write Header Meta
        lines.append("  meta {")
        lines.append(f'    tenuto_version: "2.0",')
        for k, v in self.global_meta.items():
            # Escape quotes in values just in case
            safe_val = v.replace('"', '\\"')
            lines.append(f'    {k}: "{safe_val}",')
        lines.append("  }")
        lines.append("")
        
        # 2. Write Instrument Definitions
        lines.append("  %% Instrument Definitions")
        for pid, info in self.parts_info.items():
            lines.append(f'  def {info["tenuto_id"]} "{info["name"]}" style=standard')
        lines.append("")
        
        # 3. Write The Pivot (Score Logic)
        lines.append("  %% Score Logic")
        sorted_measures = sorted(self.pivot_data.keys())
        
        for m_idx in sorted_measures:
            data = self.pivot_data[m_idx]
            
            lines.append(f"  measure {m_idx} {{")
            
            # If we found time sig changes in this measure, write them here
            if '__meta__' in data:
                meta_str = ", ".join(data['__meta__'])
                lines.append(f"    meta {{ {meta_str} }}")
            
            # Write the musical events for every active instrument
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
        
        # Determine Output Filename
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            # Strip extension (like .mxl) and swap with .ten
            base_name, _ = os.path.splitext(input_file)
            output_file = base_name + ".ten"

        try:
            print(f"Reading {input_file}...")
            converter = MusicXMLToTenuto(input_file)
            
            print("Phase 1: Parsing Structure...")
            converter.parse_structure()
            
            print("Phase 2: Converting Logic...")
            converter.parse_logic()
            
            print(f"Phase 3: Writing to {output_file}...")
            tenuto_code = converter.generate_tenuto()
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(tenuto_code)
            
            print("Done! Conversion Successful.")
            
        except Exception as e:
            # Print errors to Standard Error stream for better pipeline handling
            sys.stderr.write(f"Error: {e}\n")
    else:
        print("Usage: python MusicXMLToTenuto.py <file.mxl> [output.ten]")
