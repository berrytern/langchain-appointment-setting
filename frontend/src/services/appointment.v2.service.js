import axiosInstance from './axios'

function sendMessage(id, message) {
    return axiosInstance
        .post(`v2/appointment-setting/${id}`, {message})
        .then((response) => {console.log(response.data);return response.data})
        .catch((err) => alert(err))
}
export { sendMessage };