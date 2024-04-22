// function cpy(text) {
// 	navigator.clipboard.writeText(text)
// }  
 function cpy(text) {

  const newElement = document.createElement("textarea");
  newElement.value = text;
  console.log(text)
  // newElement.style.visibility = "hidden";
  document.body.appendChild(newElement);
  newElement.select();
  document.execCommand("copy");
  document.body.removeChild(newElement);
  }
