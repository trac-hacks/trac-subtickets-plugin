jQuery(function($) {
  var ticketbox = document.getElementById('ticketbox');
  if (ticketbox === null)
    ticketbox = document.getElementById('ticket');
  if (ticketbox !== null) {
    var div = $(document.createElement('div'));
    div.html(subtickets_div);
    $(ticketbox).append(div.contents());
  }
});
