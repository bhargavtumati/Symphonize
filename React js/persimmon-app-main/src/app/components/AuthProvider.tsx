"use client";

import { ReactNode, useEffect } from "react";
import { auth } from "./firebaseConfig";
import { onIdTokenChanged, onAuthStateChanged } from "firebase/auth";

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Provides Firebase authentication state to children components.
 *
 * Listens for auth state changes and stores the user's Firebase ID token in
 * local storage. Also refreshes the ID token automatically every 60 minutes
 * without requiring a page refresh.
 */
const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  useEffect(() => {
    let refreshInterval: NodeJS.Timeout | null = null;

    const updateToken = async (user: any) => {
      if (user) {
        try {
          const idToken = await user.getIdToken(true); // Force refresh the token
          localStorage.setItem("firebaseIdToken", idToken);
          document.cookie = `firebaseIdToken=${idToken}; path=/; secure; samesite=strict; max-age=86400`;
        } catch (error) {
          console.error("Error refreshing token:", error);
        }
      }
    };

    const authListener = onIdTokenChanged(auth, (user) => {
      if (user) {
        updateToken(user);

        // Set up a token refresh interval (every 55 minutes to prevent expiration)
        if (refreshInterval) clearInterval(refreshInterval);
        refreshInterval = setInterval(() => updateToken(user), 55 * 60 * 1000);
      } else {
        localStorage.removeItem("firebaseIdToken");
        document.cookie = "firebaseIdToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";

        // Clear interval if user logs out
        if (refreshInterval) {
          clearInterval(refreshInterval);
          refreshInterval = null;
        }
      }
    });

    return () => {
      console.log("AuthProvider unmounting");
      authListener();
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, []);

  return <>{children}</>;
};

export default AuthProvider;

/**
 * Returns the currently signed-in user's email.
 */
export const getCurrentUserEmail = () => {
  return new Promise((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        unsubscribe();
        resolve(user.email);
      } else {
        unsubscribe();
        reject(new Error("No user is signed in"));
      }
    });
  });
};
