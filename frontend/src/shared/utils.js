import axios from "axios";
import jwt from "jsonwebtoken";
import { jwtDecode } from "jwt-decode";

const createToken = () => {
  const STATION_SECRET =
    "1d6020fbd5de871d2eacf3726f73f7e267d25087e8aba1e984020cc98703ee1404cc03082583ab4311d6f4a2fee69817c2e1b08d472358adfa68cde57ec0f30b";
  const token = jwt.sign({ stationName: "station1" }, STATION_SECRET, {
    expiresIn: "1m",
  });

  return token;
};

export const rvaucmsClient = axios.create({
  baseURL: "http://localhost:2620/session-broker/sign-in",
  withCredentials: true,
});

rvaucmsClient.interceptors.request.use(
  (config) => {
    // means the request not a retry, it's the first attempt.
    if (!config.headers["Authorization"]) {
      //  use a new token to make the request.
      config.headers["Authorization"] = `Bearer ${createToken()}`;
    }
    return config;
  },
  (err) => {
    Promise.reject(err);
  }
);

export const getSession = async () => {
  const data = await rvaucmsClient
    .get("/session-broker", {
      params: { stationName: "station1" },
    })
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
