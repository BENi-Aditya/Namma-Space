import React from 'react'

function Instructions() {
  return (
    <div className="instructions">
      <h1>Namma Space</h1>
      <p>3D Indoor Navigation System</p>

      <div className="controls">
        <h2>Controls</h2>
        <div className="control-item">
          <span className="control-key">W A S D</span>
          <span>Move around</span>
        </div>
        <div className="control-item">
          <span className="control-key">Mouse</span>
          <span>Look around</span>
        </div>
        <div className="control-item">
          <span className="control-key">ESC</span>
          <span>Exit navigation</span>
        </div>
      </div>

      <div className="click-prompt">
        Click anywhere to start exploring
      </div>
    </div>
  )
}

export default Instructions
