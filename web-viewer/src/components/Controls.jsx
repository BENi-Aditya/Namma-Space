import { useEffect, useRef } from 'react'
import { useThree, useFrame } from '@react-three/fiber'
import { PointerLockControls } from '@react-three/drei'
import * as THREE from 'three'

function Controls({ onPointerLockChange }) {
  const { camera, gl } = useThree()
  const controlsRef = useRef()

  // Movement state
  const moveState = useRef({
    forward: false,
    backward: false,
    left: false,
    right: false,
    up: false,
    down: false
  })

  // Velocity
  const velocity = useRef(new THREE.Vector3())
  const direction = useRef(new THREE.Vector3())

  // Movement settings
  const speed = 5.0 // Units per second
  const damping = 0.9 // Deceleration factor

  useEffect(() => {
    const onKeyDown = (event) => {
      switch (event.code) {
        case 'KeyW':
        case 'ArrowUp':
          moveState.current.forward = true
          break
        case 'KeyS':
        case 'ArrowDown':
          moveState.current.backward = true
          break
        case 'KeyA':
        case 'ArrowLeft':
          moveState.current.left = true
          break
        case 'KeyD':
        case 'ArrowRight':
          moveState.current.right = true
          break
        case 'Space':
          moveState.current.up = true
          break
        case 'ShiftLeft':
        case 'ShiftRight':
          moveState.current.down = true
          break
      }
    }

    const onKeyUp = (event) => {
      switch (event.code) {
        case 'KeyW':
        case 'ArrowUp':
          moveState.current.forward = false
          break
        case 'KeyS':
        case 'ArrowDown':
          moveState.current.backward = false
          break
        case 'KeyA':
        case 'ArrowLeft':
          moveState.current.left = false
          break
        case 'KeyD':
        case 'ArrowRight':
          moveState.current.right = false
          break
        case 'Space':
          moveState.current.up = false
          break
        case 'ShiftLeft':
        case 'ShiftRight':
          moveState.current.down = false
          break
      }
    }

    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('keyup', onKeyUp)

    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('keyup', onKeyUp)
    }
  }, [])

  // Update movement every frame
  useFrame((state, delta) => {
    if (!controlsRef.current || !controlsRef.current.isLocked) return

    // Calculate movement direction
    direction.current.z = Number(moveState.current.forward) - Number(moveState.current.backward)
    direction.current.x = Number(moveState.current.right) - Number(moveState.current.left)
    direction.current.y = Number(moveState.current.up) - Number(moveState.current.down)
    direction.current.normalize()

    // Apply acceleration
    if (moveState.current.forward || moveState.current.backward) {
      velocity.current.z -= direction.current.z * speed * delta
    }
    if (moveState.current.left || moveState.current.right) {
      velocity.current.x -= direction.current.x * speed * delta
    }
    if (moveState.current.up || moveState.current.down) {
      velocity.current.y += direction.current.y * speed * delta
    }

    // Apply damping
    velocity.current.x *= damping
    velocity.current.y *= damping
    velocity.current.z *= damping

    // Move camera
    controlsRef.current.moveRight(-velocity.current.x * delta)
    controlsRef.current.moveForward(-velocity.current.z * delta)

    // Vertical movement (up/down)
    camera.position.y += velocity.current.y * delta
  })

  return (
    <PointerLockControls
      ref={controlsRef}
      args={[camera, gl.domElement]}
      onLock={() => onPointerLockChange?.(true)}
      onUnlock={() => onPointerLockChange?.(false)}
    />
  )
}

export default Controls
