import { useState, useEffect, useCallback } from "react"

const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second

export const useOtpless = () => {
  const [jwtToken, setJwtToken] = useState("")
  const [isVerified, setIsVerified] = useState(false)
  const [error, setError] = useState("")
  const [isSDKLoaded, setIsSDKLoaded] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  const loadOtplessSDK = useCallback(() => {
    return new Promise<void>((resolve, reject) => {
      if (document.getElementById("otpless-sdk")) {
        resolve()
        return
      }

      const script = document.createElement("script")
      script.id = "otpless-sdk"
      script.src = "https://otpless.com/v4/headless.js"
      script.setAttribute("data-appid", process.env.NEXT_PUBLIC_OTPLESS_KEY || "")
      document.head.appendChild(script)

      script.onload = () => {
        console.log("OTPless SDK script loaded successfully")
        setIsSDKLoaded(true)
        resolve()
      }

      script.onerror = () => {
        console.error("Failed to load OTPless SDK script")
        setError("Failed to load OTPless SDK. Please try again later.")
        reject(new Error("Failed to load OTPless SDK"))
      }
    })
  }, [])

  const initializeOTPless = useCallback(() => {
    return new Promise<void>((resolve, reject) => {
      if (typeof window === "undefined") {
        console.warn("Window is undefined, cannot initialize OTPless")
        reject(new Error("Window is undefined"))
        return
      }

      if (window.OTPless && window.OTPless.initiate && window.OTPless.verify) {
        resolve()
        return
      }

      const initializeAttempt = () => {
        if (window.OTPless) {
          const callback = (eventCallback: any) => {
            const ONETAP = () => {
              const { response } = eventCallback
              setJwtToken(response.sessionInfo.sessionToken)
              setIsVerified(true)
              setError("")
            }

            const OTP_AUTO_READ = () => {
              const {
                response: { otp },
              } = eventCallback
              console.log("OTP_AUTO_READ event:", { otp })
            }

            const FAILED = () => {
              const { response } = eventCallback
              setError("Verification failed. Please try again.")
              console.log("FAILED event:", { response })
            }

            const FALLBACK_TRIGGERED = () => {
              const { response } = eventCallback
              console.log("FALLBACK_TRIGGERED event:", { response })
            }

            const EVENTS_MAP: { [key: string]: () => void } = {
              ONETAP,
              OTP_AUTO_READ,
              FAILED,
              FALLBACK_TRIGGERED,
            }

            if ("responseType" in eventCallback) {
              EVENTS_MAP[eventCallback.responseType]()
            }
          }

          window.OTPless = new (window as any).OTPless(callback)
          resolve()
        } else {
          if (retryCount < MAX_RETRIES) {
            setRetryCount((prevCount) => prevCount + 1)
            setTimeout(initializeAttempt, RETRY_DELAY)
          } else {
            setError("Failed to initialize OTPless. Please refresh the page and try again.")
            reject(new Error("OTPless initialization failed after max retries"))
          }
        }
      }

      initializeAttempt()
    })
  }, [retryCount])

  useEffect(() => {
    loadOtplessSDK()
      .then(() => initializeOTPless())
      .catch((error) => {
        console.error("Error during OTPless setup:", error)
        setError("Failed to set up OTPless. Please refresh the page and try again.")
      })

    return () => {
      const scriptElement = document.getElementById("otpless-sdk")
      if (scriptElement) {
        document.head.removeChild(scriptElement)
      }
    }
  }, [loadOtplessSDK, initializeOTPless])

  const initiateOtp = useCallback(
    async (phoneNumber: string) => {
      try {
        await initializeOTPless()
        if (window.OTPless && window.OTPless.initiate) {
          window.OTPless.initiate({
            channel: "PHONE",
            phone: phoneNumber,
            countryCode: "+91",
          })
        } else {
          throw new Error("OTPless.initiate is not available")
        }
      } catch (error) {
        console.error("Error initiating OTP:", error)
        setError("Failed to initiate OTP. Please try again.")
      }
    },
    [initializeOTPless],
  )

  const verifyOtp = useCallback(
    async (phoneNumber: string, otp: string) => {
      try {
        await initializeOTPless()
        if (window.OTPless && window.OTPless.verify) {
          window.OTPless.verify({
            channel: "PHONE",
            phone: phoneNumber,
            otp: otp,
            countryCode: "+91",
          })
        } else {
          throw new Error("OTPless.verify is not available")
        }
      } catch (error) {
        console.error("Error verifying OTP:", error)
        setError("Failed to verify OTP. Please try again.")
      }
    },
    [initializeOTPless],
  )

  return { jwtToken, isVerified, error, initiateOtp, verifyOtp, setIsVerified, isSDKLoaded, setJwtToken }
}

