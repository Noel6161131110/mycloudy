import './App.css'
import Dashboard from './components/ui/Dashboard';
import { Routes, Route, Navigate } from 'react-router-dom';
import VideoPlayer from './components/ui/VideoPlayer/Index';
import AuthUI from './components/ui/Auth/Index';

function App() {

  return (
    <>

      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/video" element={
            <div className="flex items-center justify-center h-screen bg-gray-600 p-6">
              <VideoPlayer videoUrl="http://192.168.0.100:8080/api/v1/file-operations/stream/video/2" />
            </div>
        } />
        <Route path="/auth" element={<AuthUI />} />

  
      </Routes> 
    </>
  )
}


export default App
