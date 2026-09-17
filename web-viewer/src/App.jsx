import React, { useState } from 'react'
import Scene from './components/Scene'
import Instructions from './components/Instructions'
import './App.css'

function App() {
  const [pointerLocked, setPointerLocked] = useState(false)

  return (
    <div className="app">
      <Scene onPointerLockChange={setPointerLocked} />
      {!pointerLocked && <Instructions />}
    </div>
  )
}

export default App
