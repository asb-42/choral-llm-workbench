# Choral LLM Workbench - Known Issues & Limitations

## Critical Issues Requiring Alternative UI Framework

### 🚫 Visual Score Preview Under Gradio

**Status:** NOT IMPLEMENTABLE with current Gradio framework  
**Priority:** HIGH - Requires complete UI framework change  
**Impact:** Core visualization feature unavailable

#### Problem Description
The requirement to display MusicXML files as readable musical notation with real-time cursor synchronization is fundamentally incompatible with Gradio's limitations:

1. **Static Image Generation**: Gradio can only display static images; real-time cursor movement requires dynamic canvas rendering
2. **No Musical Notation Libraries**: Gradio lacks integration with music notation libraries (LilyPond, VexFlow, etc.)
3. **Synchronization Limitations**: Audio playback cursor synchronization requires JavaScript event handling not available in Gradio
4. **Interactive Score Elements**: Click-to-play, measure highlighting, and note selection are impossible

#### Technical Root Causes

**Gradio Framework Limitations:**
- No real-time canvas manipulation
- No JavaScript integration for interactive elements  
- Static component model prevents dynamic score rendering
- Limited to pre-defined input/output components

**Missing Integrations:**
- No LilyPond rendering pipeline
- No VexFlow/Mei.js JavaScript integration
- No Web Audio API for precise timing
- No SVG manipulation for score elements

#### Required Solution
**Complete UI Framework Migration** from Gradio to a modern web framework with:

```
✅ React/Vue.js frontend with JavaScript audio handling
✅ Web Audio API integration for precise timing
✅ LilyPond/VexFlow for score rendering  
✅ Real-time canvas manipulation for cursor
✅ Interactive score elements (click, hover, select)
✅ WebSocket integration for real-time updates
```

#### Implementation Roadmap

**Phase 1: Foundation**
- [ ] Choose alternative UI framework (React/Vue + FastAPI)
- [ ] Set up Web Audio API integration
- [ ] Implement basic MusicXML parsing

**Phase 2: Score Rendering**  
- [ ] Integrate LilyPond or VexFlow for notation
- [ ] Implement real-time cursor positioning
- [ ] Add interactive score elements

**Phase 3: Audio Integration**
- [ ] Web Audio API for playback with precise timing
- [ ] Voice separation and individual playback
- [ ] Real-time audio-visual synchronization

---

## Current Workarounds

### ✅ Working: Text-based Score Information
- Display part names, measure counts, basic metadata
- Audio generation for individual voices and master
- File upload and parsing functionality

### ⚠️ Limited: Static Score "Preview"
- Simple matplotlib visualization (not real notation)
- No musical accuracy or readability
- No interactivity or synchronization
- Educational/demo purposes only

---

## Other Technical Debt

### Audio Generation Dependencies
- **FluidSynth Integration**: Complex setup requiring system soundfonts
- **MIDI Conversion**: Additional processing layer adds complexity
- **Real-time Playback**: Limited by Gradio's static audio components

### Performance Considerations
- Large score files cause memory issues
- Real-time rendering blocked by Gradio's request-response model
- No streaming or progressive loading support

---

## Recommended Next Steps

### Immediate (This Session)
1. **Implement working audio-only preview** without visual score
2. **Focus on functional audio features** (voice separation, playback)
3. **Document limitations clearly** for future development

### Medium Term (Next Development Cycle)
1. **Plan UI framework migration** from Gradio
2. **Research alternative score rendering solutions**
3. **Prototype React/Vue + FastAPI architecture**

### Long Term (Future Development)
1. **Complete rewrite** with modern web stack
2. **Professional music notation integration**
3. **Real-time interactive features**

---

## Technical Notes

### Why Not Workarounds Within Gradio?
- JavaScript injection not possible in Gradio components
- Custom HTML/CSS limited and unreliable
- External libraries (LilyPond, VexFlow) require browser integration
- Real-time updates blocked by Gradio's polling mechanism

### Alternative Approaches Considered
1. **Static Score Images**: Generated offline, no interactivity
2. **Text-based Notation**: Limited musical representation
3. **External Score Viewer**: Separate application, poor UX
4. **Gradio Custom Components**: Requires extensive Gradio source modification

**Conclusion:** All workarounds provide suboptimal user experience; proper solution requires framework change.

---

*Last Updated: 2026-01-06*
*Status: Active Development - Audio Features Working, Visual Features Blocked*