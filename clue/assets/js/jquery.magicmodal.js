(function( $ ){

  var methods = {
     init : function( options ) {
		$("#modalWindow").bind('click.magicModal',methods.hide);
	 	this.bind('click.magicModal',methods.show);
     },
	 
	 show : function(){
		$('#modalMask, #modalWindow').fadeIn(300); 
	},
	 
	hide : function(){
		$('#modalMask, #modalWindow').fadeOut(300);
	}

  };

  $.fn.magicModal = function( method ) {
    
    if ( methods[method] ) {
      return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.magicModal' );
    }    
  
  };

})( jQuery );