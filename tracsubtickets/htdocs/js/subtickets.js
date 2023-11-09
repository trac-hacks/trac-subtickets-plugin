jQuery(function(){
  const anchor = document.getElementById('ticket');
  if (!anchor) {
    return;
  }

  const div = document.createElement('div');
  div.outerHTML = subtickets_div;

  anchor.appendChild(div);
});
