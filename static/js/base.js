$(function() {

  $('#btn-search').click(function(){
    window.location = window.location.origin + '?symbol=' + $('#input-symbol').val();
  });

  $('#btn-buy').click(function(){
    window.location = '/buy/' +
                      $('#symbol').html() + '/' +
                      $('#input-quantity').val() + '/' +
                      $('#ask-price').html() + '/' +
                      window.location.search;
  });
  $('#btn-sell').click(function(){
    window.location = '/sell/' +
                      $('#symbol').html() + '/' +
                      $('#input-quantity').val() + '/' +
                      $('#bid-price').html() + '/' +
                      window.location.search;
  });
});
