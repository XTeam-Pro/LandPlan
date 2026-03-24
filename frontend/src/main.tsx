import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { captureUtmParams } from './utils/utm'
import './index.css'

// Capture UTM parameters from URL on initial load
captureUtmParams()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
