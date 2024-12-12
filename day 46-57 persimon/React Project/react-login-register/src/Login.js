import React, { useState } from "react";
import axios from "axios";
import './App.css';

function Login () {

    const [password, setPasswordValue] = useState("");
    const [email, setEmailValue] = useState("");

    const setPassword = (e) => {
        setPasswordValue(e.target.value);
    }

    const setEmail = (e) => {
        setEmailValue(e.target.value);
    }

    const handleSubmit = async (e) => {
        //prevent default
        e.preventDefault();

        //api call
        console.log("this is our data "+ email +"   "+ password )
        
        //create an object with email and password for passing the api
        const data = {
            "email": email,
            "password": password
        }

        try{
            const response = await axios.post("http://localhost:8080/loginUser", data);

            console.log("this is the response " + response.data);
            if(!response.data ) {
                alert("Invalid email or Password");
            }
            else {
                alert("Login Successfull");

            }
            
        } catch(error) {
            console.error(error);
        }




    }

    const redirectToRegister = () => {
        window.location.href = "/register";
    }

    return (
       
        <div className="container">
           
           <form onSubmit={handleSubmit}>
           <h1> Bhargav Blog</h1>
            <label>User ID:</label>
            <input type="email" placeholder="Enter your user id" value={email} onChange={setEmail}/>
            <br></br>
            <br></br>
            <label>Password:</label>
            <input type="password" placeholder="Enter your password" value={password} onChange={setPassword}/>
            <br></br>
            <br></br>

            <button type="submit">Login</button>
    <br />
    <span>Don't have an account? </span>
    <button type="button" onClick={redirectToRegister}>Register</button>

            
           </form>

        </div>
    )
}

export default Login;