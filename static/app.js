(function () {

var STATUS, _blinkInterval;
function refreshQueues() {
  $.getJSON('/status', function (data) {
    STATUS = data;
    console.log(data);
    var n = data.length;

    var qs = $('#queues').detach().empty();
    while(n--) {
      var q = data[n];
      //if(q.name == "TEST") continue;

       qs.append("<a href='#" + q.id + "' id='q" + q.id + "' class='q status_" + q.status + " mode_current'><small class='current'>Trenutni broj</small><span>" +  (q.activeTicket || 0) + "</span><small>" + q.description + "</small></a>");
    }

    $(document.body).append(qs);
    $('#loading').hide();
  });
}

function blinkStatus() {
  var count = n = STATUS.length;
  while (n--) {
    //if(q.name == "TEST") continue;
    (function (n) {
    var q = $('#q' + STATUS[n].id)
	.transition({perspective: '200px', rotateY: '360deg', delay: 200*(count-n)}, 500)
	.transition({perspective: '200px', rotateY: '360deg'}, function () {
          $(this).css('rotateY', '0deg');
        });
    setTimeout(function () {
          if(q.hasClass("mode_current")) {
            q.removeClass("mode_current").addClass("mode_inline");
            q.find('.current').text('U redu čekaju');
            q.find('span').text(STATUS[n].waitingCustomers);
          } else {
            q.removeClass("mode_inline").addClass("mode_current");
            q.find('.current').text('Trenutni broj');
            q.find('span').text(STATUS[n].activeTicket);
          }
        }, 200*(count-n)+100);
    })(n);
  }
}

function requestTicket(q) {
  $('#loading').show();
  $.getJSON('/request/' + q, function (resp) {
    console.log("REQUESTED", resp);
    if("error" in resp) { alert(resp.error); }
    refreshQueues();
  });
}

$(function () {
  refreshQueues();
  setInterval(refreshQueues, 3*60*1000);
  _blinkInterval = setInterval(blinkStatus, 30*1000);

  $(document.body).on('click', '.q.status_ACTIVE', function () {
    requestTicket(this.href.split('#')[1]);
  });
});


})();
