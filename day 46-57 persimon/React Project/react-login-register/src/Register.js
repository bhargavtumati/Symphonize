import React, { useState } from "react";
import axios from "axios";
import './App.css';

function Register () {

   
    const [register, setRegister] = useState({
      email: "",
        name: "",
       
        password: ""
    });

    const handleChange = (e) => {
      setRegister({
        ...register,
        [e.target.name]:e.target.value
      })

    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log(register);

        try{
            const response = await axios.post('http://localhost:8080/addUser', register);
            console.log(response.data);
            if(!response.data ) {
              alert("Invalid email or Password or name");
          }
          else {
              alert("User added successfully");

          }
            

       } catch(error){
        console.log(error);

       }
       
}
const redirectToLogin = () => {
  window.location.href = "/login";
}
    return (
       <div className="container">
      <form onSubmit={handleSubmit}>
        <h2>Register</h2>

        
        

        <label>Email:</label>
        <input
          type="email"
          name="email"
          placeholder="Enter your email"
          value={register.email}
          onChange={handleChange}
        />
        <br /><br />

        <label>Name:</label>
        <input
          type="text"
          name="name"
          placeholder="Enter your name"
          value={register.name}
          onChange={handleChange}
        />
        <br /><br />

        <label>Password:</label>
        <input
          type="password"
          name="password"
          placeholder="Enter your password"
          value={register.password}
          onChange={handleChange}
        />
        <br /><br />

        <button type="submit">Register</button>

        <br />
    <span>Already have an account? </span>
    <button type="button" onClick={redirectToLogin}>Login</button>
    
      </form>
      
    </div>
    )
}

export default Register;