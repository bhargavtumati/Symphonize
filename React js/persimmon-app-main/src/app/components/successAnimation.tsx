import React from 'react';
import Lottie from 'react-lottie-player';

const SuccessAnimation = () => {
    return (
        <div style={{ textAlign: 'center' }}>
            <Lottie
                loop
                animationData={require('../components/Animation - 1732281767836.json')} // Replace with the path if you download the file
                play
                style={{height: 200 }}
            />
        </div>
    );
};

export default SuccessAnimation;
