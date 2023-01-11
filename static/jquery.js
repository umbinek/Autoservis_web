$(document).ready(function(){
    $("#ham").click(function(){
      $("nav ul").slideToggle();
    });
  
    $("h2").mouseenter(function(){
      $(this).find("div").fadeIn(500);
    });
    $("h2").mouseout(function(){
      $(this).find("div").fadeOut(500);
    });  
  
  });
  