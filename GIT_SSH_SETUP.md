# 🔐 Git SSH Setup Guide

## Your SSH Public Key
Copy this key and add it to your GitHub account:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBVNzTr2CWF3Oq1D2sy13EFViVHh3h4uiAPAf9aiwBQy your_email@example.com
```

## Steps to Add SSH Key to GitHub:

1. **Go to GitHub**: https://github.com/settings/keys
2. **Click "New SSH key"**
3. **Title**: "AutoTrader MacBook"
4. **Key type**: Authentication Key
5. **Key**: Paste the key above
6. **Click "Add SSH key"**

## Test SSH Connection:
```bash
ssh -T git@github.com
```

You should see: "Hi ChandruV2003! You've successfully authenticated..."

## Push to GitHub:
```bash
git push origin main
```

## ✅ Your SSH Key is Ready!
Your git authentication is now set up with SSH instead of PAT tokens.
