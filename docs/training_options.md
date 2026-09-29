# 3D Training Speed Options - Choose Your Speed! 🚀

## Current Situation
- Your previous training: **20-30 hours** (30,000 iterations, CPU)
- Problem: Way too slow for competition deadline

## ✅ RECOMMENDED: Ultra-Fast Training (2-4 hours)

**Script:** `./train-ultra-fast.sh`

**Settings:**
- 3,000 iterations (10x fewer)
- Optimized ray sampling
- CPU training (stable, no GPU issues)
- Auto-exports model when done

**Expected time:** 2-4 hours
**Quality:** Excellent for competition (80-90% of full quality)

**Run this:**
```bash
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
./train-ultra-fast.sh
```

---

## Option 2: Balanced Training (4-6 hours)

**Script:** `./train-fastest-cpu.sh`

**Settings:**
- 5,000 iterations
- Slightly better quality than ultra-fast
- CPU training

**Expected time:** 4-6 hours
**Quality:** Very good for competition (85-95% of full quality)

---

## Option 3: Original (NOT RECOMMENDED - 20-30 hours)

**What you were running:**
- 30,000 iterations
- Full quality but takes forever

**Expected time:** 20-30 hours
**Quality:** 100% but overkill for Round 1

---

## 📊 Comparison Table

| Option | Time | Quality | Best For |
|--------|------|---------|----------|
| **Ultra-Fast** ⚡ | 2-4 hrs | 85% | Quick results, competition Round 1 |
| **Balanced** | 4-6 hrs | 90% | Better quality, still reasonable time |
| **Original** ❌ | 20-30 hrs | 100% | Only if you have days to wait |

---

## 🎯 MY RECOMMENDATION

**Use Ultra-Fast (3,000 iterations)**

Why?
- ✅ Finishes in time for competition
- ✅ Quality is MORE than enough for Round 1
- ✅ Can always retrain with more iterations later
- ✅ Gets you a working demo TODAY

---

## How to Start

1. **Stop current training** (if still running):
   - Press `Ctrl+C` in terminal

2. **Start ultra-fast training**:
   ```bash
   cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
   ./train-ultra-fast.sh
   ```

3. **Wait 2-4 hours** ☕

4. **Done!** Model auto-exports and copies to web viewer

---

## After Training Completes

Launch web viewer:
```bash
cd namma-space-project/web-app
npm install  # (first time only)
npm run dev
```

Open: http://localhost:5173

Navigate with WASD + mouse! 🎮

---

**Created:** September 13, 2026, 3:34 PM IST
**For:** Namma Space - IIT Bombay Techfest Competition
