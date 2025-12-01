import './App.css';
import { useEffect } from 'react';

function App() {
  
  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" }
        });
        document.getElementById("videoFeed").srcObject = stream;
      } catch (err) {
        console.error("Camera error:", err);
      }
    }

    startCamera();
  }, []);
  
  return (
    <div className="main-container">
      
      {/* LEFT CAMERA FEED */}
      <div className="camera-section">
        <div className="camera-box">
          <video id="videoFeed" autoPlay playsInline style={{ width: "100%", height: "100%", objectFit: "cover" }}></video>
        </div>
      </div>

      {/* RIGHT SIDE PANEL */}
      <div className="side-panel">

        <div className="panel-title">
          RVAUC-MS Compliance Detection
        </div>

        <div className="panel-box student-details">
          <p><strong>Student Details</strong></p>
          <p>Student Number</p>
          <p>Department</p>
          <p>Year Level</p>
          <p>Block</p>
          <p>Name</p>
        </div>

        <div className="panel-box result-box">
          Compliance Evaluation Result
        </div>

        <div className="button-row">
          <button className="confirm-btn">Confirm</button>
          <button className="retry-btn">Retry</button>
        </div>

        <input 
          className="student-input" 
          placeholder="Student Number Input (optional)"
        />

        <button className="login-btn">Log in</button>

      </div>
    </div>
  );
}

export default App;
