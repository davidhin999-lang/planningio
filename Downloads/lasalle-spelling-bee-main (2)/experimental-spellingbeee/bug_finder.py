#!/usr/bin/env python3
"""
Comprehensive bug finder for the spelling bee application.
Analyzes code for common issues, logic errors, and potential problems.
"""
import os
import re
import sys
from pathlib import Path

class BugFinder:
    def __init__(self, project_root):
        self.project_root = project_root
        self.bugs = []
        self.warnings = []
        self.info = []
    
    def add_bug(self, file, line, issue, severity="HIGH"):
        self.bugs.append({
            "file": file,
            "line": line,
            "issue": issue,
            "severity": severity
        })
    
    def add_warning(self, file, line, issue):
        self.warnings.append({
            "file": file,
            "line": line,
            "issue": issue
        })
    
    def add_info(self, file, line, issue):
        self.info.append({
            "file": file,
            "line": line,
            "issue": issue
        })
    
    def check_python_files(self):
        """Check Python files for common issues."""
        print("[*] Checking Python files...")
        
        python_files = [
            os.path.join(self.project_root, "app.py"),
            os.path.join(self.project_root, "words.py"),
        ]
        
        for filepath in python_files:
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            filename = os.path.basename(filepath)
            
            for i, line in enumerate(lines, 1):
                # Check for bare except
                if re.search(r'except\s*:', line):
                    self.add_warning(filename, i, "Bare except clause - should specify exception type")
                
                # Check for TODO/FIXME comments
                if re.search(r'#\s*(TODO|FIXME|BUG|HACK)', line):
                    self.add_info(filename, i, f"Found: {line.strip()}")
                
                # Check for potential None dereference
                if '.get(' in line and 'or' not in line and '{}' not in line:
                    if 'default' not in line:
                        self.add_warning(filename, i, "Potential None dereference without default")
                
                # Check for hardcoded values
                if re.search(r'(password|api_key|secret)\s*=\s*["\']', line, re.IGNORECASE):
                    self.add_bug(filename, i, "Hardcoded credentials found!", "CRITICAL")
                
                # Check for print statements (should use logging)
                if re.match(r'\s*print\(', line) and '__name__' not in line:
                    self.add_warning(filename, i, "Using print() instead of logging")
    
    def check_javascript_files(self):
        """Check JavaScript files for common issues."""
        print("[*] Checking JavaScript files...")
        
        js_files = [
            os.path.join(self.project_root, "static", "script.js"),
        ]
        
        for filepath in js_files:
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            filename = os.path.basename(filepath)
            
            for i, line in enumerate(lines, 1):
                # Check for console.log (should be removed in production)
                if 'console.log' in line and 'DEBUG' not in line:
                    self.add_info(filename, i, f"Debug log: {line.strip()[:60]}")
                
                # Check for eval usage
                if 'eval(' in line:
                    self.add_bug(filename, i, "eval() usage - security risk!", "CRITICAL")
                
                # Check for TODO/FIXME
                if re.search(r'//\s*(TODO|FIXME|BUG|HACK)', line):
                    self.add_info(filename, i, f"Found: {line.strip()}")
                
                # Check for potential null dereference
                if '.fetch(' in line and '.catch' not in lines[min(i+5, len(lines)-1)]:
                    self.add_warning(filename, i, "Fetch without error handling nearby")
    
    def check_logic_issues(self):
        """Check for logic issues in app.py."""
        print("[*] Checking logic issues...")
        
        app_path = os.path.join(self.project_root, "app.py")
        if not os.path.exists(app_path):
            return
        
        with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for duplicate function definitions
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        duplicates = [f for f in set(functions) if functions.count(f) > 1]
        if duplicates:
            for dup in duplicates:
                matches = [i+1 for i, line in enumerate(lines) if f'def {dup}(' in line]
                for match in matches:
                    self.add_bug("app.py", match, f"Duplicate function definition: {dup}", "HIGH")
        
        # Check for potential infinite loops
        for i, line in enumerate(lines, 1):
            if 'while True' in line:
                self.add_warning("app.py", i, "Infinite loop - ensure proper exit condition")
        
        # Check for race conditions in file operations
        for i, line in enumerate(lines, 1):
            if 'open(' in line and 'with' not in lines[max(0, i-2):i]:
                self.add_warning("app.py", i, "File opened without 'with' statement")
    
    def check_security_issues(self):
        """Check for security vulnerabilities."""
        print("[*] Checking security issues...")
        
        app_path = os.path.join(self.project_root, "app.py")
        if not os.path.exists(app_path):
            return
        
        with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            # Check for SQL injection patterns
            if 'query' in line.lower() and '%' in line and 'format' in line:
                self.add_warning("app.py", i, "Potential SQL injection - use parameterized queries")
            
            # Check for path traversal
            if 'request.args' in line or 'request.form' in line:
                if 'os.path.join' in line or 'open(' in line:
                    self.add_warning("app.py", i, "User input used in file operations - check for path traversal")
    
    def report(self):
        """Generate bug report."""
        print("\n" + "="*70)
        print("BUG FINDER REPORT")
        print("="*70)
        
        if self.bugs:
            print(f"\n[CRITICAL ISSUES] {len(self.bugs)} bugs found:")
            for bug in self.bugs:
                try:
                    print(f"  {bug['severity']:8} | {bug['file']:20} L{bug['line']:4} | {bug['issue']}")
                except UnicodeEncodeError:
                    print(f"  {bug['severity']:8} | {bug['file']:20} L{bug['line']:4} | [encoding issue]")
        
        if self.warnings:
            print(f"\n[WARNINGS] {len(self.warnings)} warnings:")
            for warn in self.warnings[:10]:  # Show first 10
                try:
                    print(f"  {warn['file']:20} L{warn['line']:4} | {warn['issue']}")
                except UnicodeEncodeError:
                    print(f"  {warn['file']:20} L{warn['line']:4} | [encoding issue]")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if self.info:
            print(f"\n[INFO] {len(self.info)} info items (debug logs):")
            print(f"  Found {len(self.info)} console.log statements in script.js")
        
        print("\n" + "="*70)
        print(f"Summary: {len(self.bugs)} bugs, {len(self.warnings)} warnings, {len(self.info)} info items")
        print("="*70)

def main():
    project_root = r"c:\Users\deifh\Downloads\CascadeProjects\windsurf-project\lasalle-spelling-bee"
    
    finder = BugFinder(project_root)
    finder.check_python_files()
    finder.check_javascript_files()
    finder.check_logic_issues()
    finder.check_security_issues()
    finder.report()

if __name__ == "__main__":
    main()
