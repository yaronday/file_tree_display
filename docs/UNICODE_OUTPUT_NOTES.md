# Windows Unicode Output Notes

This tool uses Unicode characters (tree branches, connectors, box-drawing glyphs) to render directory structures.  
These characters work correctly on **macOS**, **Linux**, **Windows Terminal**, **WSL**, and most modern UTF-8 terminals.  

However, **Windows PowerShell and CMD have known limitations** when Unicode output is **redirected to a file**.  

This means commands like:

```powershell
ftd -stream > out.txt
ftd -stream | Out-File out.txt
ftd --printout > tree.txt
```

may produce mojibake such as:

```
Γפ£ΓפאΓפא
Γפג Γפ£ΓפאΓפא
```

This is **not** a bug in `ftd` or Python — it is a limitation of **Windows’ redirection layer**,   
which forces legacy OEM encodings (CP437/CP850/CP862) regardless of the program’s output encoding.  

Even valid UTF-8 output is reinterpreted as an OEM code page, resulting in corrupted text.  

---

# What *does* work on Windows

### **1. Interactive printing (terminal shows Unicode correctly)**

```powershell
ftd
ftd --printout
ftd -stream
```

Works correctly in:

* Windows Terminal (recommended)
* PowerShell 7+
* CMD (with UTF-8 mode enabled)
* Git Bash
* WSL

---

### **2. Saving output using PowerShell’s UTF-8 API**

PowerShell provides a UTF-8-aware command that bypasses OEM redirection:

```powershell
ftd -stream | Set-Content -Encoding UTF8 out.txt
```

or:

```powershell
ftd --printout | Set-Content -Encoding utf8 output.txt
```

This reliably produces correct UTF-8 output.

---

### **3. Running from UTF-8 shells**

* Git Bash
* WSL (Ubuntu, Debian, etc.)
* MSYS2
* MinGW

All support UTF-8 redirection correctly:

```bash
ftd -stream > out.txt
ftd --printout > tree.txt
```

---

## What does *not* work (Windows limitation)

### **Redirecting stdout directly with `>` or `Out-File`**

```powershell
ftd -stream > out.txt
ftd --printout > out.txt
ftd -stream | Out-File out.txt
```

This does **not** produce valid UTF-8 and cannot be fixed from within this tool, because:

* Windows forces the OEM console encoding on redirected output
* PowerShell interprets incoming bytes incorrectly
* BOMs do not help in redirected output
* Python cannot override the encoding of the Windows redirection layer

This behavior is documented in Windows and PowerShell issue trackers as “by design.”

---

## Recommended Workflow for Windows Users

### **Option A — The recommended method**

```powershell
ftd -stream | Set-Content -Encoding UTF8 out.txt
```

### **Option B — Use Windows Terminal + PowerShell 7+**

PowerShell 7 handles Unicode output more consistently.

### **Option C — Use Git Bash or WSL**

UTF-8 works flawlessly in those environments.

---

### Note: 
The extra function ensure_utf8_stdout() is intentionally not unit-tested.  
It interacts with OS-level console streams and exhibits platform-dependent behavior, making unit tests unreliable.  
Its correctness is ensured through manual verification on Windows, macOS, and Linux.  

# Summary

Windows legacy console redirection (`>`) does **not** support UTF-8 output from CLI tools, including Python programs.  
`ftd` outputs correct Unicode, but redirection through PowerShell/CMD applies non-UTF-8 encodings, causing corruption.

---
