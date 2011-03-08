
Lobby = {
    id: null,
    update_interval: 2000,  //ms
    media_url: '/',
    
    //Call from view after id is set
    init: function()
    {
        $('ul').listview()
        Lobby.updateMembers()
        Lobby.go()
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
        //alert(Lobby.creator);
        $(Lobby.members).each(function(i, member)
        {
            h = "<li><img class='ui-li-icon small_avatar' src='" + member.image + "' /><span class='text'><b>" + member.user.username + "</b>"
            h += " at " + member.created;
            if(User.id == Lobby.creator) {
                if (member.user.id != Lobby.creator) {
                    h += " <a href='javascript: Lobby.removeUser("+ member.id +")'>x</a>";
                }
            }
            if(User.id == member.user.id) {
                h += " <a data-rel='dialog' href='/lobby/show_character_picker/"+Lobby.id+"/'>Pick Character</a></span></li>";
            }

            $('#members').append(h)
            
            //$('#id_to').innerHTML += '<option value="' + member.user.id + '">' + member.user.username + '</option>'
        });
        
        $('ul').listview('refresh')
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
    },

    pickCharacter: function(element)
    {
        $(".picker_img").removeClass("selected");
        $(element).addClass("selected");

        $("#creator_image").val(element.id);
    },
    
    go: function()
    {
        Lobby.update_timer = setInterval(Lobby.updateMembers, Lobby.update_interval)
    },
    
    pause: function()
    {
        clearInterval(Lobby.update_timer)
    }
}


//update_messages = new PeriodicalExecuter(Lobby.updateMessages, 2)