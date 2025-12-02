
Charles
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
    <>
      {/* TOP NAVBAR */}
      <div className="top-navbar">
        <div className="nav-left">
          RVAUC-MS Compliance Detection
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-container">

        {/* LEFT CAMERA FEED */}
        <div className="camera-section">
          <div className="camera-box">
            <video
              id="videoFeed"
              autoPlay
              playsInline
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            ></video>
          </div>
        </div>

        {/* RIGHT SIDE PANEL */}
        <div className="side-panel-wrapper">
          <div className="side-panel">

            {/* STUDENT PROFILE CARD */}
            <div className="card">
              <div className="card-title">
                <span>Student Profile</span>
                <span className="badge">READ-ONLY</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Student Number</span>
                <span className="detail-value">...</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Department</span>
                <span className="detail-value">...</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Year Level</span>
                <span className="detail-value">...</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Block</span>
                <span className="detail-value">...</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Name</span>
                <span className="detail-value">...</span>
              </div>
            </div>

            {/* EVALUATION BOX */}
            <div className="eval-box">
              <div className="eval-icon">⚙️</div>
              <p className="eval-title">EVALUATION RESULT</p>
              <p className="eval-result">Ready</p>
              <p className="eval-sub">System Idle. Awaiting Scan.</p>
            </div>

            {/* BUTTONS */}
            <div className="button-row">
              <button className="confirm-btn">Verify</button>
              <button className="retry-btn">Retry</button>
            </div>

            {/* INPUT */}
            <input
              className="student-input"
              placeholder="Student Number (optional)"
            />

            {/* LOGIN BUTTON */}
            <button className="login-btn">Authenticate Log In</button>

          </div>
        </div>

      </div>
    </>
  );
}

export default App;