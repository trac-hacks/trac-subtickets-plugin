(function() {
    var $;
    
    $ = jQuery;

    // content must have been defined via add_script_data()
    $(document).ready(function() {
        $('div#ticket').append(content);
    });

}).call(this);
