import axios from "axios";
import { jwtDecode } from "jwt-decode";

const rvaucmsToken =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0aW9uTmFtZSI6InN0YXRpb24xIiwiaWF0IjoxNzY0NzAwNDc1LCJleHAiOjIwODAyNzY0NzV9.pXbCchvsc9uP5E6bbMzcHQZHHL90yFdcCijTKp7oHgM";

export const rvaucmsClient = axios.create({
  baseURL: "http://localhost:2620/session-broker/get-active-session",
  withCredentials: true,
});

rvaucmsClient.interceptors.request.use(
  (config) => {
    // means the request not a retry, it's the first attempt.
    if (!config.headers["Authorization"]) {
      //  use a new token to make the request.
      config.headers["Authorization"] = `Bearer ${rvaucmsToken}`;
    }
    return config;
  },
  (err) => {
    Promise.reject(err);
  }
);

export const sessionBroker = async () => {
  console.log("retrieving session...");

  const data = await rvaucmsClient
    .get("/station1")
    .then((response) => response.data)
    .catch((error) => {
      if (error.response) return error.response.data;

      return { success: false, message: error.message };
    });

  if (data.success) {
    const token = data.result;
    const decoded = jwtDecode(token);
    return { success: true, result: decoded };
  } else return data;
};
