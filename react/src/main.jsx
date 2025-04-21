import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './front_end.css'
import App from './front_end.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
