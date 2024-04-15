import { AxiosInstance, default as axios } from 'axios'

const instance = axios.create({
    baseURL: 'http://localhost:8000',
})

export default instance;