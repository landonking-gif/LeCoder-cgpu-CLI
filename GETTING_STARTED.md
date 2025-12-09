# Getting Started with LeCoder cGPU

A 2-minute guide to running code on free Colab GPUs from your terminal.

## Step 1: Install (30 seconds)

```bash
npm install -g lecoder-cgpu
```

**Requirements**: Node.js 18+ (Check with `node --version`)

## Step 2: Connect (1 minute)

```bash
lecoder-cgpu connect
```

This will:
1. Open Google OAuth in your browser
2. Ask for Colab + Drive permissions
3. Connect to a GPU runtime
4. Drop you into an interactive shell

## Step 3: Run Code (30 seconds)

### Option A: In the Interactive Shell
```python
import torch
print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Option B: From Your Terminal
```bash
lecoder-cgpu run "python your_script.py"
```

## That's It! 🎉

You're now running code on free Colab GPUs from your terminal.

---

## Next Steps

### Transfer Files
```bash
# Upload
lecoder-cgpu upload local_file.py /content/remote_file.py

# Download
lecoder-cgpu download /content/results.csv ./results.csv
```

### Check Status
```bash
lecoder-cgpu status  # See GPU info & connection
lecoder-cgpu logs    # View execution history
```

### Manage Notebooks
```bash
lecoder-cgpu notebook list              # List your notebooks
lecoder-cgpu notebook create "My ML"    # Create new notebook
```

### Multiple Sessions (Colab Pro)
```bash
lecoder-cgpu sessions list              # View all sessions
lecoder-cgpu sessions switch <id>       # Switch active session
```

---

## Common Issues

### "Authentication failed"
```bash
lecoder-cgpu logout
lecoder-cgpu connect
```

### "Command not found"
```bash
# Check installation
npm list -g lecoder-cgpu

# Reinstall if needed
npm install -g lecoder-cgpu
```

### "Runtime not available"
- Check [Colab Status](https://colab.research.google.com/)
- Try CPU runtime: `lecoder-cgpu connect --cpu`
- Wait a few minutes and retry

---

## Learn More

- 📚 [Complete Documentation](./README.md)
- 🔧 [Troubleshooting Guide](./TROUBLESHOOTING.md)
- 📖 [API Reference](./docs/api-reference.md)
- 🤖 [AI Agent Integration](./docs/agent-integration.md)

---

## Need Help?

- 🐛 [Report a Bug](https://github.com/aryateja2106/LeCoder-cgpu-CLI/issues)
- 💬 [Ask a Question](https://github.com/aryateja2106/LeCoder-cgpu-CLI/discussions)
- 📧 Security: aryateja2106@gmail.com

---

**Happy GPU Computing! 🚀**
