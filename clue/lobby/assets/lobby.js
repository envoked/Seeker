
Lobby = {
    id: null,
    update_interval: 2000,  //ms
    
    //Call from view after id is set
    init: function()
    {
        this.updateMembers()
    },
    
    updateMembers: function()
    {
        $.post('/lobby/get_lobby/',
            {'lobby': Lobby.id},
            function(resp)
            {
                data = eval('(' + resp + ')')
                if (data['game']) document.location = '/seeker/game/' + data['game']
                Lobby.members = data['members']
                Lobby._drawMembers()
                setTimeout(Lobby.updateMembers, Lobby.update_interval)
            }
        )
    },
    
    updateMessages: function()
    {
        $.post('/lobby/messages/get/',
            {'lobby': Lobby.id},
            function(resp)
            {
                data = eval('(' + resp + ')')
                Lobby.messages = data
                Lobby._drawMessages()
            }
        )
    },
    /*
    _drawMessages: function()
    {
        $("messages").html("")
        Lobby.messages.each(function(i, msg)
        {
            h = "<b>" + msg.sender.username + "</b> at " + msg.created + "<br/>"
            h += "<p>" + msg.content + "</p>"
            $('messages').innerHTML += h
            
        })
    },*/
    
    _drawMembers: function()
    {
        $('#members').html("")
        //$('#id_to').update("")
        
        $(Lobby.members).each(function(i, member)
        {
            h = "<li><b>" + member.user.username + "</b>"
            h += " at " + member.created;
            if (member.user.id != User.id) {
                h += " <a href='javascript: Lobby.removeUser("+ member.id +")'>x</a></li>";
            }
            
            $('#members').append(h)
            
            //$('#id_to').innerHTML += '<option value="' + member.user.id + '">' + member.user.username + '</option>'
        });
    },
    
    addCpuUser: function()
    {
        $.post('/lobby/members/add_cpu_user/',
            {'lobby': Lobby.id},
            function(resp)
            {
                
            }
        )
    },
    
    removeUser: function(member_id)
    {
        $.post('/lobby/members/remove_member/',
            {'member_to_remove': member_id},
            function(resp)
            {
                
            }
        )
    },
    
    inviteMember: function()
    {
        $.post('/lobby/members/invite/',
            {'lobby': Lobby.id, 'email': $('#email').value},
            function(resp)
            {
                
            }
        )  
    }
}

//update_messages = new PeriodicalExecuter(Lobby.updateMessages, 2)