import "./App.css";
// FIX 1: Ensure useRef, useState, and useCallback are imported
import { useEffect, useState, useRef, useCallback } from "react";
import { manualLogIn, sessionBroker, logOut } from "./shared/utils";

function App() {
  // --- Refs ---
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);

  // --- State ---
  const [detectedItems, setDetectedItems] = useState({});
  const [studentId, setStudentId] = useState("");
  const [token, setToken] = useState("");
  const [payload, setPayload] = useState(null);
  // Added Name state
  const [studentName, setStudentName] = useState("Waiting for login...");
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [wsStatus, setWsStatus] = useState("Disconnected");
  const [isScanning, setIsScanning] = useState(false); // Scanning defaults to off
  const [isVerifying, setIsVerifying] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [countdown, setCountdown] = useState(null);

  //dropdown profile
  const [dropdownOpen, setDropdownOpen] = useState(false);

  //  --  Ui States --
  const [statusDisplay, setStatusDisplay] = useState({
    text: "Ready.",
    sub: "System idle.",
    color: "white",
  });
  const [isVerifyDisabled, setIsVerifyDisabled] = useState(false);
  const [isRetryDisabled, setIsRetryDisabled] = useState(false);

  // Removed redundant 'boxes' state as it's only used internally by drawBoxes

  // --- Constants ---
  const WS_URL = "ws://localhost:8000/ws/detect/";
  const FRAME_RATE = 200; // 5 FPS

  // --- 0. Session Polling ---
  useEffect(() => {
    if (token) return;

    let cancelled = false;

    const poll = async () => {
      while (!cancelled && !token) {
        const data = await sessionBroker();

        if (data.success) {
          setIsScanning(true);

          const { decoded, token } = data.result;

          setToken(token);
          setPayload(decoded);

          const { surname, firstName } = decoded;
          const fullName = surname + ", " + firstName;
          setStudentName(fullName.toUpperCase());
          return;
        }

        await new Promise((r) => setTimeout(r, 3000));
      }
    };

    poll();
    return () => {
      cancelled = true;
    };
  }, [token]);

  // --- 1. WebSocket Connection ---
  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WS Connected");
      setWsStatus("Connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "detection") {
        setDetectedItems(data.detected_items || {});
        if (canvasRef.current && videoRef.current) {
          drawBoxes(data.boxes);
        }
      } else {
        //  handle verify / confirm actions
        console.log("Evaluation:", data.evaluation);
        setEvaluationResult(data.evaluation);
        setIsScanning(false); // Stop scanning on result
        clearCanvas();
      }
    };

    ws.onclose = () => setWsStatus("Disconnected");

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, []);

  // --- 2. Start Camera (FIXED to use ref) ---
  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: 640, height: 480 },
        });

        // This is the correct way to connect the stream to the video element
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Camera error:", err);
      }
    }
    startCamera();
  }, []);

  // --- 3. Frame Loop (Sending Images) ---
  // Re-defined with useCallback for stability in the useEffect dependency array
  const sendFrame = useCallback(() => {
    const video = videoRef.current;
    if (!video || video.readyState !== 4) return;

    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const ctx = tempCanvas.getContext("2d");
    ctx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    const base64 = tempCanvas.toDataURL("image/jpeg", 0.5);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "frame",
          frame: base64,
        })
      );
    }
  }, []); // Empty dependencies for useCallback

  useEffect(() => {
    if (!isScanning) return;
    const interval = setInterval(sendFrame, FRAME_RATE);
    return () => clearInterval(interval);
  }, [isScanning, sendFrame]); // Added sendFrame to dependencies

  // --- 4. UI Updates
  // verify button disabling
  useEffect(() => {
    const isVerifyDisabled =
      wsStatus === "Disconnected" || !token || isVerifying || evaluationResult;
    setIsVerifyDisabled(isVerifyDisabled);
  }, [wsStatus, token, isVerifying, evaluationResult]);
  //  retry button disabling
  useEffect(() => {
    const isRetryDisabled =
      wsStatus === "Disconnected" || !token || isConfirmed || !isVerifyDisabled;
    setIsRetryDisabled(isRetryDisabled);
  }, [wsStatus, token, isConfirmed, isVerifyDisabled]);

  // --- Helper Functions ---

  const drawBoxes = (boxes) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    // Match canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    boxes.forEach((box) => {
      const [x1, y1, x2, y2] = box.xyxy;
      const label = box.label;
      const conf = (box.conf * 100).toFixed(1);

      ctx.strokeStyle = "#00FF00";
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      ctx.fillStyle = "#00FF00";
      ctx.font = "16px Arial";
      ctx.fillText(`${label} ${conf}%`, x1, y1 - 5);
    });
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  // --- Button Handlers ---

  const handleVerify = async () => {
    if (!token) {
      console.error("User is not logged in.");
      // We will update the status box later to show this error
      return;
    }

    setIsVerifying(true);

    const countdown = 5;

    for (let i = countdown; i > 0; i--) {
      setCountdown(i);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "verify",
          student_id: studentId,
          detected_items: detectedItems,
        })
      );
      setIsConfirming(true);
    } else {
      setIsVerifying(false);
      console.error("System not connected.");
    }
  };

  const handleRetry = () => {
    setIsVerifying(false);
    setIsConfirming(false);
    setEvaluationResult(null);
    setDetectedItems({});
    setIsScanning(true); // Resume scanning
    clearCanvas();
  };

  const handleLogin = async () => {
    // FIX: Use console.log instead of alert()
    if (!studentId) return;

    const logIn = await manualLogIn(studentId);
    if (!logIn.success) {
      setStudentName("Failed logging in: " + logIn.message);
      console.log("Please enter a Student ID to log in.");
      return;
    }

    const { token, decoded } = logIn.result;
    console.log(JSON.stringify(decoded));
    setToken(token);
    setPayload(decoded);
    const { surname, firstName } = decoded;
    const fullName = surname + ", " + firstName;
    setStudentName(fullName.toUpperCase());
    console.log(`Manual login successful for ID: ${studentId}`);
  };

  const handleConfirm = async () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setIsConfirming(false);
      setIsConfirmed(true);
      wsRef.current.send(
        JSON.stringify({
          action: "confirm",
          access_token: token,
          detected_items: detectedItems,
        })
      );
    } else {
      console.error("System not connected.");
    }
  };

  const handleLogOut = async () => {
    if (!token) return;
    const res = await logOut();

    console.log(res.message);

    if (res.success) {
      setToken("");
      setPayload(null);
      setStudentId("");
      setStudentName("Waiting for login...");
      setIsScanning(false);
      setDetectedItems({});
      clearCanvas();
      setIsVerifying(false);
      setIsConfirming(false);
      setIsConfirmed(false);
      setEvaluationResult(null);
    }
  };

  // --- Render Helpers ---
  useEffect(() => {
    const getEvaluationStatus = () => {
      if (wsStatus === "Disconnected") {
        return {
          text: "Disconnected",
          sub: "System is disconnected.",
          color: "#f87171",
        };
      }

      // if (!isScanning && studentId && !evaluationResult)
      //   return {
      //     text: "Scanning Paused",
      //     sub: "Press Retry to scan again.",
      //     color: "yellow",
      //   };

      if (evaluationResult) {
        console.log(JSON.stringify(evaluationResult));
        if (!isConfirmed) {
          //  return type of the yolo microservice
          const { completeness, missing } = evaluationResult;
          return {
            text: completeness ? "COMPLETE" : "INCOMPLETE",
            sub: completeness
              ? "Uniform Compliant"
              : "Missing: " + missing.join(", "),
            color: completeness ? "#4ade80" : "#f87171",
          };
        }

        //  return type of rvaucms
        const { success, message } = evaluationResult;

        if (!success)
          return {
            text: "ERROR",
            sub: "Failed evaluating: " + message,
            color: "#f87171",
          };

        const { isCompliant, reasons } = evaluationResult.result;

        return {
          text: isCompliant ? "COMPLETE" : "INCOMPLETE",
          sub: isCompliant
            ? "Uniform Compliant"
            : "Reasons: " + reasons?.join(", "),
          color: isCompliant ? "#4ade80" : "#f87171",
        };
      }

      return {
        text: isVerifying
          ? "VERIFYING IN..." + countdown
          : isScanning
          ? "SCANNING"
          : "Ready",
        sub: isVerifying
          ? "Verifying detection..."
          : isScanning
          ? "Real-time detection active."
          : "System Idle.",
        color: isScanning ? "#60a5fa" : "white",
      };
    };

    setStatusDisplay(getEvaluationStatus());
  }, [
    wsStatus,
    isConfirmed,
    isScanning,
    isVerifying,
    studentId,
    evaluationResult,
    countdown,
  ]);

  return (
    <>
      <div className="top-navbar">
        <div className="nav-left">
          RVAUC-MS Compliance Detection{" "}
          <span style={{ fontSize: "12px", opacity: 0.7 }}>({wsStatus})</span>
        </div>

        <div className="nav-right">
          {/* PROFILE DROPDOWN */}
          <div className="profile-wrapper">
            <div
              className="profile-container"
              onClick={() => setDropdownOpen((prev) => !prev)}
            >
              <img
                src="https://i.pravatar.cc/150"
                alt="Profile"
                className="profile-image"
              />
            </div>

            {dropdownOpen && (
              <div className="dropdown-menu">
                <div className="dropdown-header-text">
                  <div className="dropdown-title">Profile</div>
                  <div className="dropdown-name">{studentName}</div>
                  <div className="dropdown-role">RVAUC-MS User</div>
                </div>

                <div className="dropdown-section">
                  <div className="dropdown-row">
                    <span>Student Number:</span>
                    <span className="value">
                      {payload?.studentNumber || "---"}
                    </span>
                  </div>
                  <div className="dropdown-row">
                    <span>Department:</span>
                    <span className="value">
                      {payload?.department || "---"}
                    </span>
                  </div>
                  <div className="dropdown-row">
                    <span>Year Level:</span>
                    <span className="value">{payload?.yearLevel || "---"}</span>
                  </div>
                  <div className="dropdown-row">
                    <span>Block:</span>
                    <span className="value">{payload?.block || "---"}</span>
                  </div>
                </div>

                <button className="logout-button" onClick={handleLogOut}>
                  Log out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-container">
        {/* LEFT CAMERA FEED */}
        <div className="camera-section">
          <div className="camera-box" style={{ position: "relative" }}>
            <video
              // FIX 2: Added ref={videoRef} to connect React state to the DOM element
              ref={videoRef}
              id="videoFeed"
              autoPlay
              playsInline
              muted
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
                backgroundColor: "black",
              }}
            ></video>

            {/* CANVAS OVERLAY */}
            <canvas
              ref={canvasRef}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                objectFit: "contain",
                pointerEvents: "none",
              }}
            />
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
                <span className="detail-value">
                  {payload?.studentNumber || "---"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Department</span>
                <span className="detail-value">
                  {payload?.department || "---"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Year Level</span>
                <span className="detail-value">
                  {payload?.yearLevel || "---"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Block</span>
                <span className="detail-value">{payload?.block || "---"}</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Name</span>
                <span className="detail-value">{studentName}</span>
              </div>
            </div>

            {/* EVALUATION BOX */}
            <div className="eval-box">
              <div className="eval-icon">⚙️</div>
              <p className="eval-title">EVALUATION RESULT</p>

              <p className="eval-result" style={{ color: statusDisplay.color }}>
                {statusDisplay.text}
              </p>

              <p className="eval-sub">{statusDisplay.sub}</p>
            </div>

            {/* BUTTONS */}
            <div className="button-row">
              <button
                className="confirm-btn"
                onClick={isConfirming ? handleConfirm : handleVerify}
                disabled={
                  isConfirming ? false : isVerifyDisabled || isConfirmed
                }
                style={{
                  opacity: isConfirming
                    ? 1
                    : isVerifyDisabled || isConfirmed
                    ? 0.5
                    : 1,
                }}
              >
                {isConfirmed
                  ? "Confirmed"
                  : isConfirming
                  ? "Confirm"
                  : "Verify"}
              </button>

              <button
                className="retry-btn"
                onClick={handleRetry}
                disabled={isRetryDisabled}
                style={{ opacity: isRetryDisabled ? 0.5 : 1 }}
              >
                Retry
              </button>
            </div>

            {/* INPUT */}
            <input
              className="student-input"
              placeholder="Student Number (optional)"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
            />

            {/* LOGIN BUTTON */}
            <button
              className="login-btn"
              onClick={handleLogin}
              disabled={wsStatus === "Disconnected" || !!token}
              style={{
                opacity: wsStatus === "Disconnected" || !!token ? 0.5 : 1,
              }}
            >
              Authenticate Log In
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
