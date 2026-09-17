import { useEffect, useRef, useState } from 'react'
import { useThree } from '@react-three/fiber'
import * as GaussianSplats3D from '@mkkellogg/gaussian-splats-3d'

function GaussianSplat({ onLoad, onError }) {
  const { scene, gl } = useThree()
  const viewerRef = useRef(null)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    // Check if model file exists
    const modelPath = '/models/demo.splat' // Default demo model path

    // Create Gaussian Splat viewer
    const viewer = new GaussianSplats3D.Viewer({
      cameraUp: [0, 1, 0],
      initialCameraPosition: [0, 1.6, 5],
      initialCameraLookAt: [0, 1, 0],
      renderer: gl,
      camera: null, // We'll use Three.js camera from Canvas
      useBuiltInControls: false, // We use custom controls
      sceneRevealMode: GaussianSplats3D.SceneRevealMode.Instant,
      sharedMemoryForWorkers: false,
      integerBasedSort: true,
      halfPrecisionCovariancesOnGPU: true,
      dynamicScene: false,
      webXRMode: GaussianSplats3D.WebXRMode.None,
      renderMode: GaussianSplats3D.RenderMode.Always,
      antialiased: true
    })

    viewerRef.current = viewer

    // Load the splat file
    viewer.addSplatScene(modelPath, {
      showLoadingUI: false,
      progressiveLoad: true,
      rotation: [0, 0, 0, 1], // Quaternion [x, y, z, w]
      position: [0, 0, 0],
      scale: [1, 1, 1]
    })
    .then(() => {
      console.log('Gaussian Splat loaded successfully')
      setIsLoaded(true)
      onLoad?.()

      // Start rendering
      viewer.start()
    })
    .catch((error) => {
      console.error('Failed to load Gaussian Splat:', error)
      onError?.(error)
    })

    // Cleanup
    return () => {
      if (viewerRef.current) {
        viewerRef.current.dispose()
      }
    }
  }, [gl, onLoad, onError])

  // Note: The viewer manages its own rendering, so we don't return any JSX
  // The splat scene is rendered directly to the WebGL context
  return null
}

export default GaussianSplat
