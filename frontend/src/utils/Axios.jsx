import axios from "axios";
import { baseURL } from "./Endpoint";


export default axios.create({
    baseURL: baseURL,
    withCredentials: true
})