function Front(obj) {
  obj.style.zIndex = "1";
}
function Back(obj) {
  obj.style.zIndex = "0";
}
function ShowProductButtons(objID) {
  document.getElementById(objID).style.opacity = 0.98;
}
function HideProductButtons(objID) {
  document.getElementById(objID).style.opacity = 0;
}
function Decrease(objID) {
  count = parseInt(document.getElementById(objID).innerHTML);
  if (count > 1) {
    document.getElementById(objID).innerHTML = count - 1;
  }
}
function Increase(objID) {
  count = parseInt(document.getElementById(objID).innerHTML);
  document.getElementById(objID).innerHTML = count + 1;
}
function AddToBag(productID) {
  count = parseInt(document.getElementById("p_" + productID).innerHTML);
  if (count != 0) {
    window.location.href = "/products/addtobag/" + productID + "/" + count;
  }
}
function RemoveFromBag(productID) {
  count = parseInt(document.getElementById("p_" + productID).innerHTML);
  window.location.href = "/products/removefrombag/" + productID + "/" + count;
}
function ChangeLanguage(lang) {
  if (window.location.pathname == "/") {
    window.location.href = "/language/" + lang + "/root";
  }
  else {
    window.location.href = "/language/" + lang + window.location.pathname;
  }
}
function ConfirmPw() {
  pw1 = document.getElementById("inputPassword").value;
  pw2 = document.getElementById("inputPassword2").value;
  if (pw1 == pw2) {
    document.getElementById("form-register").submit();
  }
  else {
    document.getElementById("error").classList.remove("hidden");
    document.getElementById("error").style.marginBottom = "2vw";
  }
}
