$(document).ready(
    function () {
        if(window.location.href.indexOf("reload") > -1) {
            $( ".opaque" ).show();
            $( ".loader" ).show();
            setTimeout(function(){location.replace(window.location.href.replace("/reload",""));},4000);
        }
    }
);

function loading(){
    $( ".opaque" ).show();
    $( ".loader" ).show();
    setTimeout(function(){$( ".opaque" ).hide();$( ".loader" ).hide();},3000);
}