
Lobby = {
    id: null,
    
    //Call from view after id is set
    init: function()
    {
        this.updateMembers()
    },
    
    updateMembers: function()
    {
        new Ajax.Request('/lobby/members/get/', {
            parameters: {'lobby': Lobby.id},
            onSuccess: function(resp)
            {
                Lobby.members = resp.responseText.evalJSON()
                Lobby._drawMembers()
            }
        })   
    },
    
    updateMessages: function()
    {
        new Ajax.Request('/lobby/messages/get/', {
            parameters: {'lobby': Lobby.id},
            onSuccess: function(resp)
            {
                Lobby.messages = resp.responseText.evalJSON()
                Lobby._drawMessages()
            }
        })
    },
    
    _drawMessages: function()
    {
        $("messages").update("")
        Lobby.messages.each(function(msg)
        {
            h = "<b>" + msg.sender.username + "</b> at " + msg.created + "<br/>"
            h += "<p>" + msg.content + "</p>"
            $('messages').innerHTML += h
            
        })
    },
    
    _drawMembers: function()
    {
        $('members').update("")
        //$('id_to').update("")
        
        Lobby.members.each(function(member)
        {
            if (member.user.id == User.id) return false;
            h = "<li><b>" + member.user.username + "</b>"
            h += " at " + member.created + "</li>"
            $('members').innerHTML += h
            
            //$('id_to').innerHTML += '<option value="' + member.user.id + '">' + member.user.username + '</option>'
        });
    },
    
    addCpuUser: function()
    {
        new Ajax.Request('/lobby/members/add_cpu_user/', {
            parameters: {'lobby': Lobby.id},
            onSuccess: function(resp)
            {
                
            }
        })
    }
}

update_members = new PeriodicalExecuter(Lobby.updateMembers, 2)
//update_messages = new PeriodicalExecuter(Lobby.updateMessages, 2)