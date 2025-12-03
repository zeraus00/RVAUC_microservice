import './App.css';
import { useEffect, useState } from 'react';
import TextType from './TextType';

function App() {
  // STATE FOR PROFILE DROPDOWN
  const [showProfileMenu, setShowProfileMenu] = useState(false);

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

  // LOGOUT HANDLER
  const handleLogout = () => {
    alert("Logged out!");
    // Add logout logic here
  };

  return (
    <>
      {/* TOP NAVBAR */}
      <div className="top-navbar">
        <div className="nav-left">
          <TextType 
            text={["RVAUC-MS Complience Detection"]}
            typingSpeed={75}
            pauseDuration={1500}
            showCursor={true}
            cursorCharacter="|"
          />
        </div>

        {/* NAV RIGHT */}
        <div className="nav-right">
          {/* PROFILE IMAGE */}
          <div
            className="profile-container"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
          >
            <img
              src="https://i.pravatar.cc/151"
              alt="Profile"
              className="profile-image"
            />
          </div>

          {/* DROPDOWN MENU */}
          {showProfileMenu && (
            <div className="profile-menu">
              <button onClick={handleLogout}>Logout</button>
            </div>
          )}
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

            {/* EVALUATION */}
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
