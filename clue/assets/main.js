User = {}

submitForm = function(form)
{
    var form = $(form);
    new Ajax.Request(form.action, {
        parameters: form.serialize(true),
        onSuccess: function(resp) {
            
        }
    })
}