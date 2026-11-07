# LughaLLM — Enterprise Pan-African AI Frontend

Enterprise-grade, modern React + TypeScript + Tailwind CSS web application for **LughaLLM**, the sovereign Pan-African Swahili AI foundational model.

## 🌟 Key Features

1. **Enterprise Real-Time SSE Token Streaming**:
   - Native Server-Sent Events (SSE) token streaming connected to `http://127.0.0.1:8000/v1/chat/completions`.
   - Streaming state with automatic reconnect and zero-downtime offline simulation fallback.

2. **System-2 Deep Reasoning Drawer (`<fikiri>`)**:
   - Collapsible drawer for System-2 chain-of-thought and cultural linguistic analysis.
   - Live token count and elapsed reasoning duration metrics.
   - Shimmer and pulsing beacon indicators during real-time generation.

3. **Multi-Turn Conversation Threads**:
   - Sidebar history synchronized with backend `GET /v1/threads` and `POST /v1/threads`.
   - Thread inline rename, deletion with confirmation, and local storage persistence.
   - Quick search and filtering across conversations.

4. **Speech & Audio Integration**:
   - **Speech-to-Text (STT)**: Web Speech API microphone input with Swahili language support (`sw-TZ`, `sw-KE`).
   - **Text-to-Speech (TTS)**: `🔊 Sikiliza Sauti` Swahili speech synthesis playback on assistant messages with playing state animation.

5. **WhatsApp View Simulator**:
   - Instant toggle between modern enterprise dark mode and low-bandwidth WhatsApp 2G green bubble view (`#005c4b`, `#202c33`, blue double checkmarks `✓✓`).

6. **M-Pesa Multi-Currency Micro-Payments**:
   - Live token ledger balance badge.
   - Slide-over billing modal supporting East African currencies:
     - 🇹🇿 **TZS** (Vodacom M-Pesa / Tigo Pesa)
     - 🇰🇪 **KES** (Safaricom M-Pesa)
     - 🇺🇬 **UGX** (MTN / Airtel Money)
     - 🇨🇩 **CDF** (M-Pesa DRC / Airtel)
     - 🇷🇼 **RWF** (MTN MoMo)
   - Real-time conversion to tokens (25 TZS = 1,000 tokens) with simulated Daraja STK Push triggers.

7. **Dialect Grounding**:
   - Switchable dialect presets:
     - 🇹🇿 🇰🇪 **Kiswahili Sanifu** (Standard Official Swahili)
     - 🇰🇪 **Nairobi Sheng** (Urban Youth Slang)
     - 🇨🇩 **DRC Kingwana** (Eastern Congo Trade)
     - 🇺🇬 **Uganda Trade Swahili** (Great Lakes Commercial)
     - 🏝️ **Coastal Swahili** (Kiunguja / Mombasa)
     - ⚡ **Otomatiki** (Automatic Detection)

8. **Keyboard Accessibility**:
   - `Cmd+K` / `Ctrl+K`: Global command palette.
   - `Cmd+O` / `Ctrl+O`: Start new chat.
   - `Cmd+B` / `Ctrl+B`: Open M-Pesa billing modal.
   - `Enter`: Send message.
   - `Shift+Enter`: Multiline text editing.

---

## 🛠️ Development & Build

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server with proxy to backend (http://127.0.0.1:8000)
npm run dev

# Build production bundle with TypeScript type-checking
npm run build

# Preview production build locally
npm run preview
```
