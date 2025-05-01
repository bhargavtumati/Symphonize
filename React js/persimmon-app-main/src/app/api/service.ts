"use client";

import { auth } from "../components/firebaseConfig";

const API_URL = process.env.NEXT_PUBLIC_API;

export const apiService = async (endpoint: string, method = "GET", body?: any, isFormData = false) => {
  let idToken = localStorage.getItem("firebaseIdToken");
  if (!idToken) {
    const user = auth.currentUser;
    if (user) {
      try {
        idToken = await user.getIdToken(true);
        localStorage.setItem("firebaseIdToken", idToken);
      } catch (error) {
        console.error("Error getting fresh token:", error);
      }
    }
  }


  const headers: HeadersInit = {};
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }

  if (idToken) {
    headers.Authorization = `Bearer ${idToken}`;
  }

  try {
    // Perform the fetch request with FormData or JSON payload depending on isFormData flag
    const response = await fetch(`${API_URL}api/v1${endpoint}`, {
      method,
      headers,
      body: body ? isFormData ? body : JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
};
