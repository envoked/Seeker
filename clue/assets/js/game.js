if (typeof console=="undefined"){console={log:function(A){var B=false;if(B){alert(A)}}}}

Game = {
    last_update: null,
    last_activity: null,
    update_interval: 1000*5, //ms between updates
    busy_interval: 300,
    activity_timeout: 1000*60*60,
    updateing: false,
    paused: false,
    state: null,
    guess: {},
    
    init: function(id, el, media_url)
    {
        this.id = id;
        this.el = el;
        this.media_url = media_url;
        this.messages_button = $('#show_messages')
        Game.interval_id = setInterval(Game.busyLoop, Game.busy_interval)
    },
    
    //LB - The game needs to be smart about refreshing itself
    busyLoop: function()
    {
        if (!Game.last_update)
        {
            Game.last_update = new Date()
            Game.last_activity = new Date()
            Game.reload()
        }

        if (new Date().valueOf() > (Game.update_interval + Game.last_update.valueOf()))
        {
            console.log('Updating')
            Game.reload()
        }
        
        if (new Date().valueOf() > (Game.activity_timeout + Game.last_activity.valueOf()) && !Game.paused)
        {
            console.log("Going to sleep...")
            Game.pause()
        }
    },
    
    /*alled to update the game automatically (no params) or to take a turn
    /@params - array
        {move: '2,3,}
        {investigate: player_d}
        {guess: user_id=role_id}
    */
    reload: function(params)
    {
        if (Game.updating && typeof params == 'undefined')
        {
            return
        }
        if (params) {
            Game.last_activity = new Date()
            Game.last_update = new Date()
            Game.updating = true
            console.log("Action:")
            console.log(params)
        }
        else params = {}
        
        $.ajax({
            url: '/seeker/game/' + Game.id + '/?' + jQuery.param(params),
            data: params,
            type: 'POST',
            success: function(data) {
                Game._game = data
                Game.updating = false
                Game.last_update = new Date()

                if (Game._game.game.player.unkown_facts == 0)
                {
                    if (Game.state != 'complete') alert("You know everything")
                    Game.pause()
                }
                if (Game._game.complete && Game.state != 'complete')
                {
                    alert("The game just ended")
                    Game.state = 'complete'
                    Game.pause()
                }
                if (Game._game.new_alerts)
                {
                    for (a in Game._game.new_alerts)
                    {
                        new_alert = Game._game.new_alerts[a]
                        console.log(new_alert)
                        alert(new_alert.text)
                        Game.viewedAlert(new_alert.id)
                    }
                }
                if (Game._game.unviewed_alerts)
                {
                    $('#show_alerts').find('.ui-btn-text').html("Alerts (" + Game._game.unviewed_alerts + ")")
                }
                if (Game._game.turns_allowed <= 0)
                {
                    Game.state = "frozen"
                }
                
                Game.redraw();            
            },
            error: function() {
                Game.last_update = new Date()
            },
            dataType: 'json'});  
    },
    
    redraw: function()
    {
        this.rows = []
        this.el.html("");
        this.el.css('width', $(window).width() + 'px')
        this.el.css('height', Game.el.width() + 'px')
        
        for (col=0; col<this._game.game.board_size; col++)
        {
            var column = []
            var tr = $('<div class="row">')
            
            for (row=0; row<this._game.game.board_size; row++)
            {
                var td = $('<div class="cell">').attr('x', row).attr('y', col)
                td.append($('<div class="inner">'))
                td.append($('<div class="over">'))
                var td_inner = $(td.find('.inner'))
                var player = this.playerAt(row, col)
                
                //If square is in moveable range
                if (Math.abs(this._game.game.player.x - row) <= 1 && Math.abs(this._game.game.player.y - col) <= 1)
                {
                    td.addClass('can-move selectable')
                    
                }
                //If there is a cubicle here
                var cubicle = this.cubicleAt(row, col)
                if (cubicle)
                {
                    td.addClass('a-cubicle').attr('cell', cubicle.id)
                    if (this.knowsPlayer(cubicle.player_id))
                    {
                        var owner = this.getById('players', cubicle.player_id)
                        td.append($('<div class="text-overlay" style="top:2em">').html(owner.user.username))
                    }
                }
                //If the cubicle is yours
                if (this._game.game.player.cell.x == row && this._game.game.player.cell.y == col)
                {
                    td.addClass('your-cubicle selectable')
                    td.append($('<div class="text-overlay br">').html("Your Cubicle"))
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/cubicle2.png">'))
                }
                else if (cubicle)
                {
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/cubicle1.png">'))
                }
                
                //If there is a player here
                if (player)
                {
                    td.addClass('occupied').attr('player', player.id)
                    if(player.user.username.length > 10) {
                        display_name = player.user.username.substring(0, 9) + "...";
                    }
                    else {
                        display_name = player.user.username;       
                    }
                    if (this.knowsPlayer(player.id)) td_inner.append($('<div class="text-overlay" style="top:2em">').html(player.role.name))
                    if (!player.is_current) display_name = '<strike>' + display_name + '</strike>'
                    td.append($('<div class="text-overlay">').html(display_name))
                }
                //If the player is you
                if (this._game.game.player.x == row && this._game.game.player.y == col)
                {
                    td.addClass('you')
                    assign_player_avatar(td_inner, this._game.game.player)
                    
                    if (Game._game.turns_allowed <= 0)
                    {
                        td.append($('<div class="text-overlay text-overlay-central">').html("Wait " + Math.abs(Game._game.turns_allowed)))
                        td.addClass('frozen')
                    }
                    
                }
                else if (player)
                {
                    assign_player_avatar(td_inner, player)
                    //td_inner.append($('<img class="tile" src="' + this.media_url + 'img/char2.png">'))   
                }

                td.css('width', Math.floor(this.el.width()/this._game.game.board_size))
                td.css('height', Math.floor(this.el.height()/this._game.game.board_size))
                td.click(GameCell.cellClick)
                column.push(td)
                tr.append(td)
            }
            
            this.el.append(tr)
            this.rows.push(column)
            $.fixedToolbars.show()
        }
    },
    
    showHelp: function()
    {
        alert("Coming when Help documentation is written.");
    },
    
    showAlerts: function(data)
    {
        $.mobile.changePage('/seeker/' + Game.id + '/alerts/', "none", false, true)
    },
    
    viewedAlert: function(alert_id, callback)
    {
        if (typeof callback != "function") callback = function() {}
        $.post('/seeker/game/' + Game.id + '/alert/viewed/', {id: alert_id}, callback, 'json')
    },
    
    investigate: function()
    {
        Game.el.addClass('guessing-player')
        Game.state = "investigating"
    },
    
    cluesForPlayer: function()
    {
        Game.el.addClass('guessing-player')
        Game.state = "clues_for_player"
    },
    
    showGuesser: function()
    {
        if (Game.state == 'complete')
        {
            alert("Game is over")
            return false;
        }
        if (Game.inCubible())
        {
            Game.guess = {}
            Game.state = 'guessing';
            Game.el.addClass('guessing-player')
            alert("Click on a player to guess")
        }
        else
        {
            alert("You must be in your cubeicle to guess.")
        }
    },
    
    showRoleGuesser: function()
    {
        $.mobile.changePage({url: '/seeker/game/' + Game.id + '/guesser/', type: 'post', data: {player: Game.guess.player}}, "slide", false, false)
        Game.el.removeClass('guessing-player')
        /*
        $.post('/seeker/game/' + Game.id + '/guesser/', {player: Game.guess.player},
            function(data) {
                Game.el.removeClass('guessing-player')
                lightbox(data)
            })
        */
    },
    
    showClues: function()
    {
        $.post('/seeker/game/' + this.id + '/clues/', {},
            function(data) {
                showView(data, {left_button: "< Game"})
                $('#clues').show()
            })
    },
    
    submitGuess: function()
    {     
        $.post('/seeker/game/' + Game.id + '/guess/', Game.guess,
            function(data) {
                if (data.correct)
                {
                    alert("Correct!")
                    Game.el.removeClass('guessing-cubicle')
                }
                else
                {
                    alert("Wrong")
                }
            }, 'json')
    },
    
    showBoard: function()
    {
        $('#clues').hide()
        $('#guesser').hide()
    },
    
    //is player in their cubicle?
    inCubible: function()
    {
        //If there is a cubicle here
        var cubicle = this.cubicleAt(this._game.game.player.x, this._game.game.player.y)
        if (this._game.game.player.cell.x == this._game.game.player.x && this._game.game.player.cell.y == this._game.game.player.y)
        {
            return true
        }
        return false
    },
    
    knowsPlayer: function(player_id)
    {
        for (var i in this._game.game.correct_guesses)
        {
            var guess =  this._game.game.correct_guesses[i]
            if (guess.other_player == player_id) return true
        }
        return false;
    },
    
    getById: function(type, id)
    {
        for (var i in this._game.game[type])
        {
            var obj = this._game.game[type][i]
            if (obj.id == id) return obj
        }
        return null
    },
    
    playerAt: function(x, y)
    {
        for (var id in this._game.game.players)
        {
            var player = this._game.game.players[id]
            if (player.x == x && player.y == y) return player;
        }
        
        return null;
    },
    
    cubicleAt: function(x, y)
    {
        for (var id in this._game.game.players)
        {
            var cell = this._game.game.players[id].cell
            if (cell.x == x && cell.y == y) return cell;
        }
        
        return null;
    },
    
    pause: function()
    {
        if (!Game.paused)
        {
            if ($('#pause')) $('#pause span span').text('Go')
            Game.paused = true
            clearInterval(Game.interval_id)
        }
        else
        {
            if ($('#pause')) $('#pause span span').text('Pause')
            Game.paused = false
            Game.interval_id = setInterval(Game.busyLoop, Game.update_interval)
        }
    },
    
    guessCubicle: function(role)
    {
        Game.state = 'guessing-cell';
        Game.el.addClass('guessing-cubicle')
        Game.guess.role = role;
    }
}

GameCell = {
  
    cellClick: function(evt)
    {
        if (!Game.active)
        {
            console.log("Waking up...")
            Game.active = true
            if (Game.paused) Game.pause()
        }
        var target = $(this)
        
        if (Game.state == 'complete' || Game.state == 'frozen')
        {
            return false;
        }
        
        if (Game.state == 'guessing')
        {
            if (target.hasClass('occupied'))
            {
                var player_id = target.attr('player')
                Game.guess.player = player_id;
                alert("What's their role?")
                Game.state = 'guessing-role';
                Game.showRoleGuesser()
                
                return false;
            }
        }
        else if (Game.state == 'guessing-cell')
        {
            var cell_id = target.attr('cell')
            Game.guess.cell = cell_id;
            
            Game.submitGuess()
            return false;
        }
        
        if (Game.state == "investigating")
        {
            if (target.hasClass('occupied') && target.hasClass('can-move'))
            {
                var player = Game.getById('players', parseInt(target.attr('player')))
                if (player.is_current) {
                    Game.state = null;
                    Game.reload({'investigate': target.attr('player')})
                }
                else
                    alert("This player is no longer active")
            }
            else if (target.hasClass('occupied'))
            {
                var player = Game.getById('players', parseInt(target.attr('player')))
                if (!player.is_current)
                    alert("This player is no longer active")
                else alert("You must be adjacent to investigate")
            }
            return false;
        }
        else if (Game.state == "clues_for_player")
        {
            if (target.hasClass('occupied')) {
                var player_id = target.attr('player');
                $('#clues_for_player').remove()
                $.mobile.changePage('/seeker/game/' + Game.id + '/clues_for_player/?player=' + player_id)
            }
 
            return false;
        }
        
        if (target.hasClass('can-move'))
        {
            Game._game.game.player.x = parseInt(target.attr('x'))
            Game._game.game.player.y = parseInt(target.attr('y'))
            Game.redraw()
            Game.reload({'move': target.attr('x') + ',' + target.attr('y')})
        }
        
    }
}

function assign_player_avatar(element, player) {
    //element.append($('<img class="tile" src="' + Game.media_url + 'img/char1.png">'))
    //alert(player.user.username)
    element.append($('<img class="tile" src="' + player.image + '" />'));
}

function show_alert(text) {
    text = text.replace(/ /g, "_");
    $("#content").append("<a id='open_dialog' style='display: none' data-rel='dialog' href='/seeker/game/show_notification/"+text+"'>open</a>");
    $("#open_dialog").click();
}

submitGuess = function()
{
    var user = $('#player')[0].value
    var role = $('#role')[0].value
    Game.submitGuess(user, role)
}