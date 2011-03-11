User = {}

Main = {
    showHelp: function()
    {
        alert("Coming when Help documentation is written.");
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