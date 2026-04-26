const button = document.getElementById("send_btn");
const text_input = document.getElementById("user_msg");

function create_human_msg(msg) {
    const msg_container = document.getElementById("msg_container")
    const human_msg = document.createElement("div");

    human_msg.classList.add("msg", "human");
    human_msg.textContent = msg;
    msg_container.appendChild(human_msg)
}

function create_ai_msg(msg) {
    const msg_container = document.getElementById("msg_container")
    const ai_msg = document.createElement("div");
    
    ai_msg.classList.add("msg", "ai");
    ai_msg.innerHTML = msg;
    msg_container.appendChild(ai_msg)

}

function send() {
    const human_msg = text_input.value;
    create_human_msg(human_msg)
    fetch("http://127.0.0.1:8000/send", {
        method : "POST",
        headers: {"Content-Type" : "application/json"},
        body : JSON.stringify({content:human_msg})
    })
    .then(response => response.json())
    .then(response_json => {
        const ai_msg = response_json.response_content
        text_input.value = ""
        create_ai_msg(ai_msg)
        })
        .catch(() => {
            create_ai_msg("Error al conectar con el servidor")

    })
}


button.addEventListener("click", () => send())

text_input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        send()
    }
})