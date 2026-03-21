# ElevenLabs API Key Setup

## Add to Vercel Environment Variables

The ElevenLabs API key has been provided. To add it to your Vercel deployment:

### Steps:

1. Go to https://vercel.com/dashboard
2. Select your project: **lasalle-spelling-bee**
3. Click **Settings** → **Environment Variables**
4. Add the following environment variable:

```
Name: ELEVENLABS_API_KEY
Value: sk_6b6f78d7842617c2e1686cc3effe368d2d55dc8e62be80da
```

5. Click **Save**
6. Redeploy the application (or wait for next push to trigger auto-deploy)

### How It Works

The application now uses this fallback chain for audio generation:

1. **Google Cloud Text-to-Speech** (primary) - High quality neural voices
2. **ElevenLabs API** (fallback) - If Google Cloud is unavailable
3. **Edge TTS** (fallback) - If both above fail
4. **Silent playback** - If all TTS methods fail (game continues)

With the ElevenLabs API key configured, users will get high-quality audio from either Google Cloud or ElevenLabs, with Edge TTS as a final fallback.

### Security Note

- ✅ The .env file is in .gitignore (not committed to GitHub)
- ✅ API key is stored securely in Vercel environment variables
- ✅ Only accessible to the backend (not exposed to frontend)

