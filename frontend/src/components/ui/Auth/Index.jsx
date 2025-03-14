import React, { useState } from "react";
import { motion } from "framer-motion";
import "./styles.css";

function Index() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const toggleForm = () => setIsLogin(!isLogin);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = isLogin ? "/api/login" : "/api/signup";
    const payload = isLogin
      ? { email: formData.email, password: formData.password }
      : formData;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      console.log("Response:", data);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="relative flex flex-col justify-center items-center h-screen p-6 gradient-bg">
    {/* Typing Animation for "mycloudy" */}
    <motion.h1
        className="text-6xl font-medium font-monoton text-[#1795DC] mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 2 }}
    >
        {["m", "y", "c", "l", "o", "u", "d", "y"].map((char, index) => (
        <motion.span
            key={index}
            initial={{ opacity: 0, y: -10 }} // Slide down instead of left
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2, duration: 0.3 }}
        >
            {char}
        </motion.span>
        ))}
    </motion.h1>

    {/* Login / Signup Form */}
    <motion.div
        className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-md"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
    >
        <h2 className="text-2xl font-semibold font-poppins text-black text-center mb-4">
        {isLogin ? "LOGIN" : "SIGN UP"}
        </h2>

        <form className="space-y-4">
        {!isLogin && (
            <input
            type="text"
            name="name"
            placeholder="Name"
            value={formData.name}
            onChange={handleChange}
            className="w-full p-4 border border-gray-300 rounded-4xl font-poppins"
            required
            />
        )}
        <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className="w-full p-4 border border-gray-300 rounded-4xl font-poppins"
            required
        />
        <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className="w-full p-4 border border-gray-300 rounded-4xl font-poppins"
            required
        />
        {!isLogin && (
            <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full p-4 border border-gray-300 rounded-4xl font-poppins"
            required
            />
        )}

        <button
            type="submit"
            className="w-full bg-[#1795DC] text-white font-semibold py-2 rounded-3xl hover:bg-[#1078b4] transition"
        >
            {isLogin ? "LOGIN" : "SIGN UP"}
        </button>
        </form>

        <p className="text-sm text-center mt-4">
        {isLogin ? "Don't have an account?" : "Already have an account?"}
        <button className="text-[#1795DC] font-semibold ml-1" onClick={toggleForm}>
            {isLogin ? "Sign Up" : "Login"}
        </button>
        </p>
    </motion.div>
    </div>
  );
}

export default Index;