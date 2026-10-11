import axios from 'axios';
export const API=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://127.0.0.1:8000/api'});
API.interceptors.request.use(c=>{const t=localStorage.getItem('athlenet_access');if(t)c.headers.Authorization=`Bearer ${t}`;return c});
API.interceptors.response.use(r=>r,async e=>{if(e.response?.status===401&&localStorage.getItem('athlenet_refresh')){try{const r=await axios.post(`${API.defaults.baseURL}/token/refresh/`,{refresh:localStorage.getItem('athlenet_refresh')});localStorage.setItem('athlenet_access',r.data.access);e.config.headers.Authorization=`Bearer ${r.data.access}`;return axios(e.config)}catch{localStorage.clear();window.location='/login'}}return Promise.reject(e)});
