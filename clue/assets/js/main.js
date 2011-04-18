User = {}
$(document).bind("mobileinit", function(){
//$.mobile.ajaxEnabled = false;
})

Main = {
    helpMenu: function(target, previous)
    {
        $('#help #' + target).show();
        $('#help #' + previous).hide();
    }
}

submitForm = function(_form)
{
    var form = $(_form);
    new Ajax.Request(form.action, {
        parameters: form.serialize(true),
        onSuccess: function(resp) {
            
        }
    })
}

String.prototype.format = function(obj) {
    var formatted = this;
    for(i in obj) {
        formatted = formatted.replace("{" + i + "}", obj[i]);
    }
    return formatted;
};


$(document).bind("mobileinit", function(){
      $.mobile.defaultTransition = 'none';
});
/*
$('#page').live('pagebeforeshow', function(event, ui)
{
    //$('#seeker').remove()
    //$($('.ui-page')[0]).remove()
    //$('#' + ui.nextPage.attr("id")).remove()
})
*/

var fixgeometry = function() {
    console.log('fixgeo')
    /* Some orientation changes leave the scroll position at something
     * that isn't 0,0. This is annoying for user experience. */
    scroll(0, 0);
    
    /* Calculate the geometry that our content area should take */
    var header = $(".ui-header:visible");
    var footer = $(".ui-footer:visible");
    var content = $(".ui-content:visible");
    var viewport_height = $(window).height();
    
    var content_height = viewport_height - header.outerHeight() - footer.outerHeight();
    
    /* Trim margin/border/padding height */
    content_height -= (content.outerHeight() - content.height());
    content.height(content_height);
}; /* fixgeometry */

$(document).ready(function() {
    //$(window).bind("orientationchange resize pageshow pagecreate", fixgeometry);
});

lightbox = function(data)
{
    hideLightbox()
    var opaque = $('<div class="opaque">')
    opaque.click(function() { $('.ui-dialog').dialog('close') })
    var el = $('<div class="lightbox ui-dialog">')
    var header = $('<div class="header ui-corner-top ui-overlay-shadow ui-bar-a ui-header">')
    header.append('<h1>Alert</h1>')
    el.append(header)
    
    var content = $('<div class="content ui-content ui-body-c">')
    content.html(data)
    el.append(content)
    
    $('body').append(el)
    $('.ui-dialog').dialog()
    $.mobile.changePage($('.lightbox'), "none", false, true)
}

hideLightbox = function()
{
    //$('.ui-dialog').dialog('close')
    Game.alert_open = false
    $.mobile.changePage($('#seeker_game'))
    $('.ui-dialog').remove()
}