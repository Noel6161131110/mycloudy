import Axios from "../../utils/Axios";
import { baseURL } from "../../utils/Endpoint";

const LoginUrl = `${baseURL}/users/login`;
const registerAdminUrl = `${baseURL}/users?status=onboarding`;

const handleLogout = (navigate) => {
  sessionStorage.removeItem("accessToken");
  sessionStorage.removeItem("refreshToken");
  sessionStorage.removeItem("name");
  sessionStorage.removeItem("email");

  navigate("/auth");
}

const handleSubmit = async (e, isLogin, formData, navigate) => {
  e.preventDefault();

  const endpoint = isLogin ? LoginUrl : registerAdminUrl;
  const payload = isLogin
      ? { email: formData.email, password: formData.password }
      : {
          name: formData.name,
          email: formData.email,
          password: formData.password,
          role: "admin",
          is_active: true,
      };

  try {
      const response = await Axios.post(endpoint, payload);

      if(endpoint === registerAdminUrl) {
        if (response.status === 201) {
            console.log("Successful response:", response.data);

            sessionStorage.setItem("accessToken", response.data.accessToken);
            sessionStorage.setItem("refreshToken", response.data.refreshToken);
            sessionStorage.setItem("name", response.data.name);
            sessionStorage.setItem("email", response.data.email);

            navigate("/dashboard");
        } 
        else {
            console.log("Response received but not 201:", response.data);
        }
      }
      else if(endpoint === LoginUrl) {
          if (response.status === 200) {
            console.log("Successful response:", response.data);

            sessionStorage.setItem("accessToken", response.data.accessToken);
            sessionStorage.setItem("refreshToken", response.data.refreshToken);
            sessionStorage.setItem("name", response.data.name);
            sessionStorage.setItem("email", response.data.email);

            navigate("/dashboard");
          } else {
              console.log("Response received but not 201:", response.data);
          }
      }
      
  } catch (error) {
      console.error("Error:", error);
  }
};

const CheckIfUsersExist = async ( setIsLogin ) => {
  try {
    const response = await Axios.get("/users");
    const users = response.data.users;
    if (users.length === 0) {
      setIsLogin(false); // No users exist, default to Signup
    }

    console.log("Users:", users);

  } catch (error) {
    console.error("Error checking users:", error);
  }
};


export { handleSubmit, CheckIfUsersExist, handleLogout };
