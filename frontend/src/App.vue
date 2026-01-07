<template>
  <div class="app">
    <h1>Choral LLM Workbench – MVP</h1>

    <section class="upload">
      <h2>MusicXML Upload</h2>
      <input type="file" @change="onFileSelected" accept=".xml,.musicxml,.mxl" />
      <div v-if="scoreInfo" class="score-info">
        <p>Score: {{ scoreInfo.fileName || scoreId }}</p>
        <p>Parts: {{ scoreInfo.parts ?? scoreInfo.partCount ?? 0 }}</p>
        <p>Measures: {{ scoreInfo.measures ?? scoreInfo.measureCount ?? 0 }}</p>
      </div>
    </section>

    <section class="llm">
      <h2>LLM Konfiguration</h2>
      <div class="row">
        <label>LLM Model</label>
        <select v-model="selectedModel">
          <option v-for="m in models" :key="m.name" :value="m.name">{{ m.name }}</option>
        </select>
      </div>
      <div class="prompts-grid">
        <div class="voice" v-for="v in voices" :key="v">
          <label>{{ v }} Prompt</label>
          <textarea v-model="prompts[v]" rows="3"></textarea>
        </div>
      </div>
      <div class="row tuning-row">
        <label>Base Tuning (Hz)</label>
        <select v-model.number="tuning">
          <option v-for="t in tuningOptions" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="row actions-row">
        <button class="harmonize" @click="harmonize">Harmonize</button>
        <button class="undo" @click="undo" style="margin-left: 8px;">Undo</button>
        <button class="redo" @click="redo" style="margin-left: 8px;">Redo</button>
        <button class="audio" @click="generateAudio" style="margin-left: 8px;">Generate Audio</button>
      </div>
    </section>

    <section class="preview" v-if="preview">
      <h2>Live Score Preview</h2>
      <ul class="drag-list" @dragover.prevent @drop="onDrop">
        <li v-for="(m, idx) in dragOrder" :key="m" draggable="true" @dragstart="dragStart(idx)" :data-index="idx">M{{ m }}</li>
      </ul>
    </section>

    <section class="history-visual" v-if="history && history.length > 0">
      <h2>History</h2>
      <div class="history-bar" style="display:flex;gap:6px;align-items:center;"> 
        <span v-for="(h,i) in history" :key="i" class="hist-seg" :style="{background: i%2? '#ddd':'#bbb', width: 20+'px', height: 12+'px'}"></span>
      </div>
    </section>

    <section class="results" v-if="results">
      <h2>LLM Suggestions</h2>
      <pre>{{ results }}</pre>
      <button @click="exportScore">Export MusicXML</button>
      <button @click="generateAudio" style="margin-left: 8px;">Generate Audio</button>
    </section>

    <section class="audio" v-if="audios.length">
      <h2>Audio Preview</h2>
      <div v-for="(a, idx) in audios" :key="idx" class="audio-row">
        <div>{{ a.label }}</div>
        <audio :src="a.src" controls></audio>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { ref, reactive, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const scoreId = ref<string | null>(null)
    const scoreInfo = ref<any>(null)

    const models = ref<Array<{ name: string; provider?: string }>>([])
    const selectedModel = ref<string>('mistral-7b')
    const tuningOptions = [432, 440, 443]
    const tuning = ref<number>(432)

    const prompts = reactive<{ [voice: string]: string }>({ S: 'Make Soprano more romantic', A: 'Make Alto more bright', T: 'Make Tenor warmer', B: 'Make Bass solid' })
    const voices = ['S', 'A', 'T', 'B']

    const results = ref<any>(null)
    const audios = ref<Array<{ label: string; src: string }>>([])

    const preview = ref<any>(null)
    const history = ref<any[]>([])
    const dragOrder = ref<number[]>([])
    const draggedIndex = ref<number | null>(null)

    onMounted(async () => {
      try {
        const r = await fetch('/api/llm/models')
        if (r.ok) {
          const j = await r.json()
          models.value = j.models ?? []
        } else {
          models.value = [{ name: 'mistral-7b' }]
        }
      } catch {
        models.value = [{ name: 'mistral-7b' }]
      }
    })

    // File upload
    const onFileSelected = async (e: Event) => {
      const target = e.target as HTMLInputElement
      const file = target?.files?.[0]
      if (!file) return
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch('/api/score/upload', { method: 'POST', body: fd })
      if (res.ok) {
        const data = await res.json()
        scoreId.value = data.scoreId
        scoreInfo.value = data
        await fetchPreview();
      }
    }

    const fetchPreview = async () => {
      if (!scoreId.value) return
      const res = await fetch(`/api/harmonize/preview?scoreId=${scoreId.value}`)
      if (res.ok) {
        const data = await res.json()
        preview.value = data
        dragOrder.value = data.order ?? []
        history.value = data.current?.history ?? []
      }
    }

    // Harmonize
    const harmonize = async () => {
      if (!scoreId.value) return
      const payload = { scoreId: scoreId.value, prompts, tuning: tuning.value, model: selectedModel.value }
      const res = await fetch('/api/harmonize', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (res.ok) {
        const data = await res.json()
        results.value = data
        await fetchPreview()
        audios.value = []
      }
    }

    // Undo/Redo
    const undo = async () => {
      if (!scoreId.value) return
      const res = await fetch('/api/harmonize/undo', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scoreId: scoreId.value }) })
      if (res.ok) {
        const data = await res.json()
        results.value = data
        history.value = data.history ?? []
      }
    }

    const redo = async () => {
      if (!scoreId.value) return
      const res = await fetch('/api/harmonize/redo', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scoreId: scoreId.value }) })
      if (res.ok) {
        const data = await res.json()
        results.value = data
        history.value = data.history ?? []
      }
    }

    // Drag & Drop handlers
    const dragStart = (idx: number) => {
      draggedIndex.value = idx
    }
    const onDrop = (dropIndex: number) => {
      if (draggedIndex.value == null) return
      const arr = [...dragOrder.value]
      const [moved] = arr.splice(draggedIndex.value, 1)
      arr.splice(dropIndex, 0, moved)
      dragOrder.value = arr
      draggedIndex.value = null
      // Persist new order via backend
      if (scoreId.value) {
        fetch('/api/harmonize/reorder-measures', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scoreId: scoreId.value, order: arr }) })
      }
    }

    const exportScore = async () => {
      if (!scoreId.value) return
      const res = await fetch('/api/score/export', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scoreId: scoreId.value, format: 'musicxml' }) })
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'score_export.musicxml'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      }
    }

    const generateAudio = async () => {
      if (!scoreId.value) return
      const payload = { scoreId: scoreId.value, voices, tuning: tuning.value, duration: 15 }
      const res = await fetch('/api/harmonize/generate-audio-per-voice', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (res.ok) {
        const data = await res.json()
        if (data?.perVoiceAudios) {
          audios.value = data.perVoiceAudios.map((x: any) => ({ label: x.voice, src: x.src }))
        }
      }
    }

    const ready = () => true

    return { onFileSelected, harmonize, undo, redo, exportScore, generateAudio, dragOrder, dragStart, onDrop, ready, models, selectedModel, tuningOptions, tuning, prompts, results, scoreId, scoreInfo, audios, preview, history, onDrop as _onDrop }
  }
}
</script>

<style>
.app { max-width: 1100px; margin: 0 auto; padding: 16px; font-family: Arial, sans-serif; }
section { border: 1px solid #ddd; padding: 12px; border-radius: 8px; margin-bottom: 12px; }
label { display: block; font-weight: bold; margin-bottom: 6px; }
input[type="file"] { display: block; }
textarea { width: 100%; min-height: 60px; }
select { padding: 6px; }
button { padding: 8px 12px; margin-top: 6px; }
.drag-list { list-style: none; padding: 0; display: flex; gap: 6px; align-items: center; }
.drag-list li { padding: 6px 10px; border: 1px solid #aaa; border-radius: 4px; cursor: move; background: #f5f5f5; }
.history-bar { height: 6px; background: #ddd; border-radius: 3px; overflow: hidden; }
.hist-seg { height: 6px; }
</style>
