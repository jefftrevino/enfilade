# -*- coding: utf-8 -*-
#This file creates a chart of chords, chosen according to a pitch-dependent probability table, for a carillon with an arbitrary range.
#Next, it became primarily the code that avoids ledger lines via additional staves. 1/27/13
#Possible model: default behavior is piano staff; octave_treble = True, octave_bass = True, splits = 
#returns "piano_staff" containing n staffs.
from abjad import *
from random import randint, seed, choice

#seed the random number generator
seed(1)

#split a single voice to two staffs
def replace_note_below_split_with_skip(note, split_pitch):
    if split_pitch.chromatic_pitch_number > note.written_pitch.chromatic_pitch_number:
            skiptools.replace_leaves_in_expr_with_skips(note)

def remove_chord_pitches_below_split(chord, split_pitch):
    index = chord.parent.index( chord )
    for note in reversed(chord):
        if split_pitch.chromatic_pitch_number > note.written_pitch.chromatic_pitch_number:
            note_index = chord.written_pitches.index( note )
            chord.pop(note_index)
    if 0 == len(chord.written_pitches):
        skip = skiptools.Skip(duration)
        chord.parent[ index:index+1 ] = skip
        
def replace_note_above_split_with_skip(note, split_pitch):
    if split_pitch.chromatic_pitch_number <= note.written_pitch.chromatic_pitch_number:
           skiptools.replace_leaves_in_expr_with_skips(note)

def remove_chord_pitches_above_split(chord, split_pitch):
    index = chord.parent.index( chord )
    popped = 0
    for note in reversed(chord):
        if split_pitch.chromatic_pitch_number <= note.written_pitch.chromatic_pitch_number:
            note_index = chord.written_pitches.index( note )
            chord.pop(note_index)
            popped = 1
    if 0 == len(chord.written_pitches):
        skip = leaftools.make_tied_leaf( Skip, chord.written_duration )
        chord.parent[ index:index+1 ] = skip

def remove_pitches_below_split_in_components(voice, split_pitch):
    for note in iterationtools.iterate_notes_in_expr(voice.leaves):
        replace_note_below_split_with_skip(note, split_pitch)
    for chord in iterationtools.iterate_chords_in_expr(voice.leaves):
        remove_chord_pitches_below_split(chord, split_pitch)

def remove_pitches_above_split_in_components(voice, split_pitch):
    for note in iterationtools.iterate_notes_in_expr(voice.leaves):
        replace_note_above_split_with_skip(note, split_pitch)
    for chord in iterationtools.iterate_chords_in_expr(voice.leaves):
        remove_chord_pitches_above_split(chord, split_pitch)

def split_components_to_three_staffs(components):
    braced_staffs = scoretools.PianoStaff()
    treble_staff = Staff()
    treble_staff.name = "treble"
    bass_staff = Staff()
    bass_staff.name = "bass"
    copies = componenttools.copy_components_and_covered_spanners( components )
    treble_voice = Voice(copies)
    copies = componenttools.copy_components_and_covered_spanners( components )
    bass_voice = Voice(copies)
    remove_pitches_below_split_in_components(treble_voice, split_pitch)
    remove_pitches_above_split_in_components(bass_voice, split_pitch)
    bass_staff.extend(bass_voice[:])
    treble_staff.extend(treble_voice[:])
    contexttools.ClefMark('bass')(bass_staff)
    braced_staffs.extend([treble_staff,bass_staff])
    copies = componenttools.copy_components_and_covered_spanners( [braced_staffs[0][0]] )
    upper_treble_voice = Voice(copies)
    remove_pitches_below_split_in_components(upper_treble_voice, split_pitch = pitchtools.NamedChromaticPitch("f'''") )
    remove_pitches_above_split_in_components( braced_staffs[0][0], split_pitch = pitchtools.NamedChromaticPitch("f'''") )
    third_staff = Staff([upper_treble_voice])
    third_staff.name = "upper_treble"
    contexttools.ClefMark("treble^8")(third_staff)
    braced_staffs.insert(0, third_staff)
    #piano_staff.override.stem.transparent = True
    return braced_staffs

#layout and formatting   
def format_score(score):
    score.set.proportional_notation_duration = schemetools.SchemeMoment(1, 16)
    score.set.tuplet_full_length = True
    score.override.spacing_spanner.uniform_stretching = True
    score.override.spacing_spanner.strict_note_spacing = True
    score.set.tuplet_full_length = True
    score.override.tuplet_bracket.padding = 2
    score.override.tuplet_bracket.staff_padding = 4
    score.override.tuplet_number.text = schemetools.Scheme('tuplet-number::calc-fraction-text')
    score.override.time_signature.stencil = False
    score.override.span_bar.stencil = False
    marktools.LilyPondCommandMark("set Timing.defaultBarType = \"invisible\"")(score)
    score.override.bar_number.transparent = True
    
def format_lilypond_file(lilypond_file):
    lilypond_file.paper_block.paper_width = 8.5 * 25.4
    lilypond_file.paper_block.paper_height = 11 * 25.4
    lilypond_file.paper_block.left_margin = 1.5 * 25.4
    lilypond_file.paper_block.right_margin = 1.5 * 25.4
    lilypond_file.paper_block.top_margin = .5 * 25.4
    lilypond_file.paper_block.ragged_bottom = False
    lilypond_file.global_staff_size = 16
    lilypond_file.layout_block.indent = 0
    #lilypond_file.header_block.title = markuptools.Markup("Pendula for Edgar Allan Poe")
    lilypond_file.layout_block.ragged_right = False
    lilypond_file.paper_block.system_system_spacing = layouttools.make_spacing_vector(0, 0, 16, 0)


#composition
def choose_distance_from_range_low(seed_interval):
    interval_width = seed_interval.number
    choice = randint(0, interval_width)
    return choice
    
def get_pitch_set_from_pitch_range_tuple( pitch_range_tuple ):
    numeric_pitch_range_tuple = (numeric_pitch_range_low, numeric_pitch_range_high)
    pitches = [ ]
    for value in range( numeric_pitch_range_tuple[0], numeric_pitch_range_tuple[1] ):
        pitch = pitchtools.NamedChromaticPitch(value)
        pitches.append(pitch)
    return pitches

def make_chord( bottom_pitch_number, numeric_pitch_range_high ):
    pitch_number = bottom_pitch_number
    bottom_pitch = pitchtools.NamedChromaticPitch( pitch_number  )
    bottom_interval_choices = [5, 7, 9]
    chord = Chord( [ bottom_pitch ], Duration(1,4) )
    bottom_interval_ambitus = choice(bottom_interval_choices)
    next_to_bottom_pitch = bottom_pitch + bottom_interval_ambitus
    chord.append( next_to_bottom_pitch )
    added_pitch = next_to_bottom_pitch
    while added_pitch.chromatic_pitch_number <= int(numeric_pitch_range_high * 2/3) :
        #pitch = choose_pitch_from_weighted_table(pitch)
        sizes = [ 3, 4 ]
        interval_size = choice(sizes)
        current_pitch = added_pitch + interval_size
        chord.append( current_pitch  )
        added_pitch = current_pitch
    while added_pitch.chromatic_pitch_number <= int(numeric_pitch_range_high) :
        #pitch = choose_pitch_from_weighted_table(pitch)
        sizes = [ 1, 2 ]
        interval_size = choice(sizes)
        current_pitch = added_pitch + interval_size
        chord.append( current_pitch  )
        added_pitch = current_pitch
    return chord   

def make_chords(number_of_chords, pitch_range_tuple):
    numeric_pitch_range_low = pitchtools.chromatic_pitch_name_to_chromatic_pitch_number( pitch_range_tuple[0] )
    numeric_pitch_range_high = pitchtools.chromatic_pitch_name_to_chromatic_pitch_number( pitch_range_tuple[1] )
    chords = [ ]
    for x in range(number_of_chords):
        distance_from_range_low = choose_distance_from_range_low( pitchtools.HarmonicChromaticInterval(7) )
        bottom_pitch_number = numeric_pitch_range_low + distance_from_range_low
        chord = make_chord( bottom_pitch_number, numeric_pitch_range_high )
        chords.append(chord)
    return chords

def make_braced_staffs():
    braced_staffs = scoretools.PianoStaff()
    treble_staff = Staff()
    treble_staff.name = "treble"
    bass_staff = Staff()
    bass_staff.name = "bass"
    contexttools.ClefMark('bass')(bass_staff)
    braced_staffs.extend([treble_staff,bass_staff])
    upper_treble_staff = Staff()
    upper_treble_staff.name = "upper_treble"
    third_staff = Staff([upper_treble_voice])
    third_staff.name = "upper_treble"
    contexttools.ClefMark("treble^8")(third_staff)
    braced_staffs.insert(0, third_staff)
    return braced_staffs

#def place_tuplet_on_staffs( component, braced_staffs ):
 #   for component in tuplet:
  #      place_componenet_on_staffs( component, braced_staffs )

def place_rest_on_staffs(component, braced_staffs):
    for staff in braced_staffs:
        copy = componenttools.copy_components_and_covered_spanners( component )
        staff.append( copy )

def place_note_on_staffs( component, braced_staffs ):
    staff_change_mark = get_staff_change_mark( component ) 
    braced_staffs[0].append( component )
    if staff_change_mark:
        braced_staffs[0][-1].append( staff_change_mark )


#def place_component_on_staffs(component, braced_staffs):
 #   #if 1 < len(component):
  #   #   place_tuplet_on_staffs( component, braced_staffs )
  #  elif isinstance(component, Rest):    
  #      place_rest_on_staffs(component, braced_staffs)
  #  elif isinstance(component, Note):
  #      place_note_on_staffs(component, braced_staffs)
  #  elif isinstance(component, Chord):
  #      place_note_on_staffs(component, braced_staffs) 

def add_voice_to_braced_staffs( voice, braced_staffs ):
 #   #treat this like an fft -- go through the components of the voice and put them on four (assume four) staffs, according to range boundaries; rests just go on all staffs.
    for staff in braced_staffs:
        copies = componenttools.copy_components_and_covered_spanners( [voice] )
        staff.extend(copies)
     #   filter_staff_by_clef(staff)


def get_range_bounds( voice ):
    pitch_numbers = [ x.written_pitch.chromatic_pitch_number for x in iterationtools.iterate_components_and_grace_containers_in_expr( voice.leaves, (Note, Chord) ) ]
    low = min(pitch_numbers)
    high = max(pitch_numbers)
    return (low, high)

def make_staffs_from_range_bounds( voice ):
    braced_staffs = scoretools.PianoStaff()
    treble_staff = Staff()
    treble_staff.name = "treble"
    bass_staff = Staff()
    bass_staff.name = "bass"
    contexttools.ClefMark('bass')(bass_staff)
    braced_staffs.extend([treble_staff,bass_staff])
    range_tuple = get_range_bounds( voice )
    if 29 < range_tuple[1]:
        upper_staff = Staff()
        upper_staff.name = "upper_treble"
        contexttools.ClefMark("treble^8")(upper_staff)
        braced_staffs.insert(0, upper_staff)
    if -27 > range_tuple[0]:
        lower_staff = Staff()
        lower_staff.name = "lower_bass"
        contexttools.ClefMark("bass_8")(lower_staff)
        braced_staffs.append( lower_staff )
    return braced_staffs
    
    

def voice_to_staffs_to_reduce_ledger_lines( voice ):
    braced_staffs = make_staffs_from_range_bounds( voice )
    #add_voice_to_braced_staffs( voice, braced_staffs )
    split_components_to_three_staffs(voice[:])
    return braced_staffs
    

def make_score( list_of_leaves):
    voice = Voice( list_of_leaves )
    braced_staffs = voice_to_staffs_to_reduce_ledger_lines( voice )
    score = Score( [braced_staffs] )
    format_score(score)
    return score

def make_lilypond_file( list_of_leaves):
    score = make_score( list_of_leaves)
    lilypond_file = lilypondfiletools.make_basic_lilypond_file(score)
    format_lilypond_file(lilypond_file)
    return lilypond_file

def make_chord_chart(number_of_chords, pitch_range_tuple):
    chords = make_chords(number_of_chords, pitch_range_tuple)
    lilypond_file = make_lilypond_file(chords)
    show(lilypond_file)
    play(lilypond_file)

0123456
0213243546

0213

def arpeggiate_chord( chord ):
    notes = [ ]
    pitches = chord.written_pitches
    ordered_pitches = [ ]
    for pitch in pitches:
        ordered_pitches.append( pitch )
    ordered_pitches.reverse()
    for pitch in ordered_pitches:
        note = Note(pitch, Duration(1,16))
        notes.append( note )
    return notes
        
def arpeggiate_chords( chords ):
    arpeggios = [ ]
    for chord in chords:
        arpeggio = arpeggiate_chord( chord )
        arpeggios.append( arpeggio )
    return arpeggios
        
def arpeggiate_chord_chart(number_of_chords, pitch_range_tuple):
    chords = make_chords(number_of_chords, pitch_range_tuple)
    arpeggios = arpeggiate_chords( chords )
    arpeggios = sequencetools.flatten_sequence( arpeggios )
    lilypond_file = make_lilypond_file( arpeggios )
    show(lilypond_file)
    play(lilypond_file)

arpeggiate_chord_chart(20, ("c", "c''''") )