import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "./styles.css";
import { CheckIfUsersExist, handleSubmit } from "../../../api/v1/Auth";

function Index() {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  useEffect(() => {
    CheckIfUsersExist(setIsLogin);
  }, []);


  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };


  return (
    <div className="relative flex flex-col justify-center items-center h-screen p-6 gradient-bg">
    {/* Typing Animation for "mycloudy" */}
    <motion.h1
        className="text-5xl font-medium font-monoton text-[#1795DC] mb-6 lg:text-6xl"
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
        {isLogin ? "LOGIN" : "REGISTER"}
        </h2>

        <form
          className="space-y-4"
          onSubmit={(e) => handleSubmit(e, isLogin, formData, navigate)}
        >
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
            {isLogin ? "LOGIN" : "REGISTER"}
        </button>
        </form>


    </motion.div>
    </div>
  );
}

export default Index;