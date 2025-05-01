import React from "react"
import Lottie from "react-lottie-player"

const FailureAnimation = () => {
  return (
    <div style={{ textAlign: "center" }}>
      <Lottie
        loop
        animationData={require("../components/Animation - Failure.json")} // Replace with your failure animation JSON file
        play
        style={{ height: 200 }}
      />
    </div>
  )
}

export default FailureAnimation

