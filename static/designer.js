const text = document.getElementById("text")

text.ondragend = e => {
  text.style.position = "absolute"
  text.style.left = e.pageX + "px"
  text.style.top = e.pageY + "px"
}

function save() {
  fetch("/save_design", { method: "POST" })
}

function print() {
  window.location = "/print"
}
