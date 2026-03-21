# TTS Configuration Guide

## 🎙️ Text-to-Speech System

The Spelling Bee game uses a **dual TTS system** that ensures **no robotic TTS** is ever used:

### **Primary: ElevenLabs API**
- **Voice**: Bella (21m00Tcm4TlvDq8ikWAM)
- **Quality**: Premium, natural-sounding
- **Settings**: Stability 0.75, Similarity Boost 0.75
- **Required**: `ELEVENLABS_API_KEY` environment variable

### **Fallback: Microsoft Edge TTS**
- **Voice**: en-US-JennyNeural
- **Quality**: Natural neural voice
- **Availability**: Built-in, no API key required
- **Reliability**: Always available as backup

### **❌ NEVER USED: Robotic TTS**
- **Old system**: Basic robotic voices
- **Status**: Completely eliminated
- **Fallback**: Not allowed - system fails rather than uses robotic TTS

## 🔧 Configuration

### **Environment Variables**
```bash
# ElevenLabs (Optional but recommended)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Optional: defaults to Bella

# Edge TTS (Automatic - no config needed)
# Built-in Microsoft Edge TTS voices
```

### **TTS Priority System**
1. **Try ElevenLabs** (if API key available)
2. **Fallback to Edge TTS** (always available)
3. **Critical Error** (if both fail) - never uses robotic TTS

## 🚀 Setup Instructions

### **Option 1: ElevenLabs + Edge TTS (Recommended)**
1. Get ElevenLabs API key from https://elevenlabs.io/
2. Set environment variable: `ELEVENLABS_API_KEY=your_key`
3. System will use ElevenLabs primarily, Edge TTS as fallback

### **Option 2: Edge TTS Only**
1. No environment variables needed
2. System will use Edge TTS exclusively
3. Still natural voice quality, no robotic TTS

## 🎯 Audio Quality Comparison

| TTS System | Quality | Speed | Reliability | Cost |
|------------|---------|-------|-------------|------|
| ElevenLabs | ⭐⭐⭐⭐⭐ | Fast | High | Usage-based |
| Edge TTS | ⭐⭐⭐⭐ | Fast | Excellent | Free |
| Robotic TTS | ⭐ | Fast | High | Free |

## 🔍 Monitoring

The system logs which TTS service is being used:
- `[TTS] ElevenLabs success` - Using ElevenLabs
- `[TTS] Edge TTS fallback success` - Using Edge TTS
- `[TTS] CRITICAL: Both failed` - System failure (no robotic fallback)

## 🛠️ Troubleshooting

### **ElevenLabs Issues**
- Check API key validity
- Verify API limits/quota
- Network connectivity to elevenlabs.io

### **Edge TTS Issues**
- Edge TTS should always work
- Check system audio permissions
- Verify edge-tts Python package installation

### **Critical TTS Failure**
- Both services down simultaneously
- Network connectivity issues
- System configuration problems

## 📝 Implementation Notes

- **No robotic TTS fallback** - system fails gracefully instead
- **Caching system** prevents repeated API calls
- **Automatic fallback** ensures reliability
- **Error handling** provides clear diagnostic messages

## 🔄 Migration Path

If you have existing robotic TTS audio files:
1. Run `fix_robotic_words.py` to regenerate with natural voices
2. Or delete old audio files to force regeneration
3. System will automatically use natural TTS for new generations
