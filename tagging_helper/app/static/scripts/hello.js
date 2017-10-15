
// document.oncontextmenu = showContextMenu;
String.prototype.insert = function (index, string) {
  if (index > 0)
    return this.substring(0, index) + string + this.substring(index, this.length);
  else
    return string + this;
};

function decodeHTML(str){
    return str
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&');
}

document.addEventListener('contextmenu', function(e) {
  var x = e.layerX;
  var y = e.layerY;
  var menu = document.getElementById('contextmenu');
  menu.style.left = x + 'px';
  menu.style.top = y + 'px';
  menu.style.display = 'block';
  e.preventDefault();
  return false;
}, false)

document.addEventListener('click', function(e) {
  var menu = document.getElementById('contextmenu');
  menu.style.display = 'none';
  return false;
}, false)


function addAnnotation(class_name) {
  text = document.getSelection().anchorNode.data
  selection = document.getSelection()
  var start_position = selection.anchorOffset;
  var end_position = selection.focusOffset;
  if (start_position > end_position)
    return
  text = text.insert(end_position, '</span>');
  text = text.insert(start_position, `<span class=${class_name}>`);
  document.getSelection().anchorNode.data = text

  var x = document.getElementById('test');
  x.innerHTML =  decodeHTML(x.innerHTML)
  saveText()
}


function cancelAnnotation() {
  text = document.getSelection().anchorNode.data
  var start_position = document.getSelection().anchorOffset;
  var end_position = document.getSelection().focusOffset;
  text = text.insert(end_position, '<span>');
  text = text.insert(start_position, '</span>');
  document.getSelection().anchorNode.data = text

  var x = document.getElementById('test');
  x.innerHTML =  decodeHTML(x.innerHTML)
  removeMeaninglesssAnnotition()
  saveText()
}

function removeMeaninglesssAnnotition() {
  var x = document.getElementById('test');
  x.innerHTML =  decodeHTML(x.innerHTML)
  tags = x.getElementsByTagName('span')
  for (i = 0; i < tags.length; i++) {
    if (tags[i].innerText.length == 0) {
      tags[i].parentNode.removeChild(tags[i]);
      i--;
    }
  }
}

function saveText() {
  text = document.getElementById('test').innerHTML
  text = text.replace(/<br>/g, '')
  document.getElementById('result').value = text
}
