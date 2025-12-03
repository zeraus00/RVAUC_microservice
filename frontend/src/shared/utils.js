import axios from "axios";
import { jwtDecode } from "jwt-decode";

const stationName = "station1";
const sessionBrokerToken =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGF0aW9uTmFtZSI6InN0YXRpb24xIiwiaWF0IjoxNzY0NzAwNDc1LCJleHAiOjIwODAyNzY0NzV9.pXbCchvsc9uP5E6bbMzcHQZHHL90yFdcCijTKp7oHgM";

export const sessionBrokerClient = axios.create({
  baseURL: "http://localhost:2620/session-broker",
  withCredentials: true,
});

sessionBrokerClient.interceptors.request.use(
  (config) => {
    // means the request not a retry, it's the first attempt.
    if (!config.headers["Authorization"]) {
      //  use a new token to make the request.
      config.headers["Authorization"] = `Bearer ${sessionBrokerToken}`;
    }
    return config;
  },
  (err) => {
    Promise.reject(err);
  }
);

export const manualSignIn = async (studentNumber) => {
  console.log("manual sign in for student: " + studentNumber);

  const data = await sessionBrokerClient
    .post("/sign-in", {
      method: "studentNumber",
      identifier: studentNumber,
      stationName,
    })
    .then((response) => response.data)
    .catch(
      (error) =>
        error.response?.data ?? { success: false, message: error.message }
    );

  return data;
};

/**
  * Decoded should be of the form:
    role: z.literal(Data.Records.roles.student),
    studentNumber: z.string(),
    department: z.string(),
    yearLevel: z.number(),
    block: z.string(),
   */
const decodeToken = (data) => {
  try {
    if (data.success) {
      const token = data.result;

      const decoded = jwtDecode(token);
      return { success: true, result: { token, decoded } };
    } else return data;
  } catch (error) {
    console.log(JSON.stringify(error));
    return { success: false, message: "Failed decoding token." };
  }
};

//  note session broker will eventually branch off to microservice
export const sessionBroker = async () => {
  console.log("retrieving session...");

  const data = await sessionBrokerClient
    .get("/get-active-session/" + stationName)
    .then((response) => response.data)
    .catch(
      (error) =>
        error.response?.data ?? { success: false, message: error.message }
    );

  return decodeToken(data);
};
