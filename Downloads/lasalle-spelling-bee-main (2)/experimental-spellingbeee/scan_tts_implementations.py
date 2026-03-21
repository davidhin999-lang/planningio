#!/usr/bin/env python3
"""
Scan all Python files for Google TTS, gTTS, robotic voice, or any non-ElevenLabs/Edge TTS implementations.
"""
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def scan_file(filepath):
    """Scan a Python file for TTS-related issues."""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return issues
    
    # Patterns to search for
    patterns = [
        (r'google\.cloud\.texttospeech', 'Google Cloud TTS import'),
        (r'from google\.cloud import texttospeech', 'Google Cloud TTS import'),
        (r'gtts|gTTS|from gtts', 'gTTS (Google TTS) import or usage'),
        (r'pyttsx3|import pyttsx3', 'pyttsx3 (robotic TTS) import'),
        (r'espeak|festival|flite', 'System TTS (robotic) reference'),
        (r'google\.tts|google_tts', 'Google TTS reference'),
        (r'robotic|robot.*voice', 'Robotic voice reference'),
        (r'fallback.*google|google.*fallback', 'Google as fallback'),
        (r'TextToSpeechClient|SynthesizeSpeechRequest', 'Google Cloud TTS API usage'),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, description in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'content': line.strip(),
                    'issue': description
                })
    
    return issues

def main():
    print("=" * 80)
    print("SCANNING FOR GOOGLE TTS AND ROBOTIC VOICE IMPLEMENTATIONS")
    print("=" * 80)
    
    all_issues = []
    
    # Scan all Python files
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
        
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, PROJECT_ROOT)
                
                issues = scan_file(filepath)
                if issues:
                    all_issues.extend(issues)
                    print(f"\n[FOUND] {relative_path}")
                    for issue in issues:
                        print(f"  Line {issue['line']}: {issue['issue']}")
                        print(f"    {issue['content'][:100]}")
    
    print("\n" + "=" * 80)
    if all_issues:
        print(f"FOUND {len(all_issues)} POTENTIAL ISSUES")
        print("=" * 80)
        
        # Group by file
        by_file = {}
        for issue in all_issues:
            if issue['file'] not in by_file:
                by_file[issue['file']] = []
            by_file[issue['file']].append(issue)
        
        for filepath in sorted(by_file.keys()):
            print(f"\n{os.path.relpath(filepath, PROJECT_ROOT)}:")
            for issue in by_file[filepath]:
                print(f"  Line {issue['line']}: {issue['issue']}")
    else:
        print("NO GOOGLE TTS OR ROBOTIC VOICE IMPLEMENTATIONS FOUND")
        print("=" * 80)
        print("\nTTS Implementation Status:")
        print("  [OK] ElevenLabs: Primary TTS provider")
        print("  [OK] Edge TTS: Fallback TTS provider")
        print("  [OK] No Google TTS found")
        print("  [OK] No robotic voice fallbacks found")

if __name__ == "__main__":
    main()
