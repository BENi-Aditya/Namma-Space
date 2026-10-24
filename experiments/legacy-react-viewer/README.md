# Namma Space - Web Viewer

3D Indoor Navigation System for IIT Bombay Techfest 2026-27

## Overview

This is the web-based viewer component that displays photorealistic 3D reconstructions of indoor spaces with first-person navigation controls.

## Features

- **First-Person Navigation**: WASD + mouse controls for intuitive movement
- **Gaussian Splatting**: Photorealistic 3D rendering using state-of-the-art techniques
- **Web-Based**: Runs in browser, no installation required
- **Responsive**: Works on desktop and mobile devices

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

### Project Structure

```
web-viewer/
├── public/
│   └── models/          # Place your .splat files here
│       └── demo.splat   # Default model (if available)
├── src/
│   ├── components/
│   │   ├── Scene.jsx           # Main 3D scene setup
│   │   ├── Controls.jsx        # WASD first-person controls
│   │   ├── GaussianSplat.jsx   # Gaussian Splat loader
│   │   └── Instructions.jsx    # UI instructions overlay
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

### Adding Your 3D Model

1. **Process your video** using the reconstruction pipeline:
   ```bash
   cd ..
   ./process_video.sh data/raw-videos/your_room.mp4 your_room
   ```

2. **Copy the generated .splat file**:
   ```bash
   cp exports/models/your_room/*.splat web-viewer/public/models/demo.splat
   ```

3. **Start the viewer**:
   ```bash
   cd web-viewer
   npm run dev
   ```

4. **Open browser** to http://localhost:5173

### Controls

| Key | Action |
|-----|--------|
| **W** | Move forward |
| **S** | Move backward |
| **A** | Strafe left |
| **D** | Strafe right |
| **Mouse** | Look around (pointer locked) |
| **ESC** | Release pointer lock |
| **Space** | Move up (fly mode) |
| **Shift** | Move down (fly mode) |

### Configuration

Edit `src/components/Controls.jsx` to adjust movement settings:

```javascript
const speed = 5.0        // Movement speed (units per second)
const damping = 0.9      // Deceleration (0-1, lower = more slippery)
```

Edit `src/components/GaussianSplat.jsx` to change initial camera position:

```javascript
initialCameraPosition: [0, 1.6, 5]  // [x, y, z]
initialCameraLookAt: [0, 1, 0]      // [x, y, z]
```

## Dependencies

### Core Libraries
- **React 18** - UI framework
- **Three.js** - 3D graphics library
- **React Three Fiber** - React renderer for Three.js
- **@react-three/drei** - Three.js utilities and helpers

### 3D Reconstruction
- **@mkkellogg/gaussian-splats-3d** - Gaussian Splatting renderer

### Navigation (Round 2)
- **rbush** - Spatial indexing for POI search
- **fuse.js** - Fuzzy search for POI names
- **yuka** - AI/pathfinding library

## Performance

### Optimization Tips

1. **Model Size**: Keep .splat files under 500MB for web deployment
2. **Frame Rate**: Target 60fps on desktop, 30fps on mobile
3. **Loading**: Use progressive loading for large models
4. **Compression**: Enable Draco compression for glTF files

### Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome/Edge | ✅ Full | Recommended |
| Firefox | ✅ Full | Good performance |
| Safari | ⚠️ Partial | May have WebGL issues |
| Mobile Chrome | ✅ Full | Reduced quality on older devices |
| Mobile Safari | ⚠️ Partial | iOS 15+ required |

## Troubleshooting

### Model Not Loading

**Problem**: Black screen or "Error loading model"  
**Solution**: 
- Check that `public/models/demo.splat` exists
- Verify file path in `GaussianSplat.jsx`
- Check browser console for errors

### Poor Performance

**Problem**: Low frame rate, stuttering  
**Solution**:
- Reduce model complexity during reconstruction
- Lower camera far plane distance
- Disable Stats component in production
- Use smaller .splat file

### Controls Not Working

**Problem**: Can't move or look around  
**Solution**:
- Click on screen to lock pointer
- Check browser console for JavaScript errors
- Ensure keyboard events are not blocked by browser

## Deployment

### GitHub Pages

```bash
# Build production bundle
npm run build

# Deploy to GitHub Pages (requires gh-pages package)
npm install -D gh-pages
npx gh-pages -d dist
```

### Vercel/Netlify

1. Connect repository to Vercel/Netlify
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy

## Round 1 Deliverables Checklist

- [ ] 3D model loads successfully
- [ ] WASD controls work smoothly
- [ ] Mouse look is responsive
- [ ] Frame rate above 30fps
- [ ] Works in Chrome, Firefox, Safari
- [ ] Deployed to public URL
- [ ] Demo video recorded (3-5 minutes)
- [ ] Technical abstract written

## Next Steps (Round 2)

1. **POI System** - Add clickable markers and search
2. **Navigation** - Implement pathfinding with Yuka
3. **Minimap** - Show 2D overhead view
4. **UI Polish** - Better loading states and error handling

## Resources

- **Three.js Docs**: https://threejs.org/docs/
- **React Three Fiber**: https://docs.pmnd.rs/react-three-fiber
- **Gaussian Splats 3D**: https://github.com/mkkellogg/GaussianSplats3D
- **Nerfstudio**: https://docs.nerf.studio/

## License

MIT License - Built for IIT Bombay Techfest 2026-27

## Authors

Namma Space Team  
IIT Bombay Techfest Competition

---

**Last Updated**: September 8, 2026  
**Version**: 1.0.0 (Round 1)
