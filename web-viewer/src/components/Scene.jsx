import React, { Suspense, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { Stats } from '@react-three/drei'
import Controls from './Controls'
import GaussianSplat from './GaussianSplat'

function Scene({ onPointerLockChange }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const handleLoad = () => {
    console.log('Model loaded successfully')
    setLoading(false)
  }

  const handleError = (err) => {
    console.error('Error loading model:', err)
    setError(err.message)
    setLoading(false)
  }

  return (
    <>
      {loading && (
        <div className="loading-screen">
          <h2>Loading 3D Model...</h2>
          <div className="loading-bar">
            <div className="loading-progress" style={{ width: '50%' }} />
          </div>
          <p style={{ marginTop: '12px', fontSize: '14px', opacity: 0.7 }}>
            This may take a few moments
          </p>
        </div>
      )}

      {error && (
        <div className="error-screen">
          <h2>Error Loading Model</h2>
          <p>{error}</p>
          <p style={{ fontSize: '14px', marginTop: '20px', opacity: 0.7 }}>
            Make sure you have a .splat file in public/models/
          </p>
        </div>
      )}

      <Canvas
        camera={{
          position: [0, 1.6, 5],
          fov: 75,
          near: 0.1,
          far: 1000
        }}
        gl={{
          antialias: true,
          alpha: false
        }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />

        {/* Controls */}
        <Controls onPointerLockChange={onPointerLockChange} />

        {/* 3D Model */}
        <Suspense fallback={null}>
          <GaussianSplat
            onLoad={handleLoad}
            onError={handleError}
          />
        </Suspense>

        {/* Performance stats (development only) */}
        {import.meta.env.DEV && <Stats />}
      </Canvas>
    </>
  )
}

export default Scene
