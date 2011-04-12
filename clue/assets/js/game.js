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
    has_loaded_once: false,
    _text_el: 'board_text',
    turn_window: 10,
    active: true, //Is Player awake?
    player_active: true,//Is Player still current?
    update_id: 0,
    
    init: function(id, el, media_url, player_id)
    {
        this.id = id;
        this.player_id = player_id;
        this.el = el;
        this.text_el = $('#'+this._text_el)
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
            Game.reload({update: Game.update_id})
        }

        if (new Date().valueOf() > (Game.update_interval + Game.last_update.valueOf()))
        {
            console.log('Updating')
            Game.reload({update: Game.update_id})
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
        }
        else params = {}
        
        $.ajax({
            url: '/seeker/game/' + Game.id + '/?' + jQuery.param(params),
            data: params,
            type: 'POST',
            success: function(data) {
                Game.data = data
                if (Game.update_id == 0) Game.original_data = data
                Game.update_id += 1
                
                Game.updating = false
                Game.last_update = new Date()
     
                if (!Game.has_loaded_once) {
                    var role = Game.me(true).role.name;
                    Game.text_el.html("Shhhh, your role is the: " + role);
                }                
            
                if (Game.data.unkown_facts == 0)
                {
                    if (Game.state != 'complete') Game.text_el.html("You know everything")
                    Game.player_active = false;
                }

                if (Game.data.complete && Game.state != 'complete')
                {
                    if (Game.has_loaded_once)
                    {
                        Game.text_el.html("The game just ended.")
                    }
                    else {
                        Game.text_el.html("The game is over.")
                    }
                    
                    Game.state = 'complete'
                }
                
                //Only active games now
                if (Game.data.turns_allowed >= Game.turn_window && Game.has_loaded_once) {
                    Game.text_el.html("Other players are waiting on you, move!")
                }
                
                //If the last turn created alerts, show the first
                if (Game.data.extra.new_alerts)
                {
                    var new_alert = Game.data.extra.new_alerts[0]
                    Game.showAlert(new_alert)
                }
                //Otherwise if there are unviewed alerts, show them
                else if (Game.data.unviewed_alerts)
                {
                    var new_alert = Game.data.unviewed_alerts[0]
                    Game.showAlert(new_alert)               
                }
                
                //Update alerts button with correct count
                if (Game.data.unviewed_alerts)
                {
                    $('#show_alerts').find('.ui-btn-text').html("Alerts (" + Game.data.unviewed_alerts.length + ")")
                }
                else $('#show_alerts').find('.ui-btn-text').html("Alerts")
                
                if (Game.data.turns.allowed <= 0)
                {
                    Game.state = "frozen"
                    Game.text_el.html("Please wait other players to catch up")
        
                }
                else if (Game.state == "frozen")
                {
                    Game.state = ""
                }
                
                if (!Game.has_loaded_once) Game.draw()
                Game.redraw()
                
                Game.has_loaded_once = true;
                         
            },
            error: function() {
                Game.last_update = new Date()
                Game.text_el.html("Problem connecting to server...")
            },
            dataType: 'json'});  
    },
    
    draw: function()
    {
        this.rows = []
        this.el.html("");
        this.el.css('width', $(window).width() + 'px')
        this.el.css('height', Game.el.width() + 'px')
        var td_width = Math.floor((this.el.width()/this.data.game.board_size) - 6)
        var td_height = Math.floor((this.el.height()/this.data.game.board_size) - 6)
        
        for (col=0; col<this.data.game.board_size; col++)
        {
            var column = []
            var tr = $('<div class="row">')
            
            for (row=0; row<this.data.game.board_size; row++)
            {
                var td = $('<div class="cell">').attr('x', row).attr('y', col).attr('id', 'cell_' + row + '_' + col)
                td.append($('<div class="inner">'))
                td.append($('<div class="over">'))
                var td_inner = $(td.find('.inner'))
                
                td.css('width', td_width)
                td.css('height', td_height)
                td.click(GameCell.cellClick)
                column.push(td)
                tr.append(td)
                
            }
            
            this.el.append(tr)
            this.rows.push(column)
            $.fixedToolbars.show()
        }
    },
    
    redraw: function()
    {
        
        for (var col=0; col<this.data.game.board_size; col++)
        {
            for (var row=0; row<this.data.game.board_size; row++)
            {
                //Grab existing <div> and reset its class
                var td = $('#cell_' + row + '_' + col)
                td.attr('class', 'cell')
                td.find(".text-overlay").remove()
                
                var td_inner = $(td.find('.inner'))
                td_inner.html("")
                var player = this.playerAt(row, col)
                
                //If square is in moveable range
                if (Math.abs(this.me().x - row) <= 1 && Math.abs(this.me().y - col) <= 1)
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
                } else {
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/empty.png" style="opacity:0.8;">'))
                    
                }
                
                //If the cubicle is yours
                if (this.myCubicle().x == row && this.myCubicle().y == col)
                {
                    td.addClass('your-cubicle selectable')
                    td.append($('<div class="text-overlay br">').html("Your Cubicle"))
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/cubeNoWall.png">'))
                }
                else if (cubicle)
                {
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/cubeTopRightWall.png">'))
                }
                
                //If there is a player here
                if (player)
                {
                    td.addClass('occupied').attr('player', player.id)
                    var user = this.original_data.player_extra[player.id].user
                    
                    if (user.username.length > 10) {
                        display_name = user.username.substring(0, 9) + "...";
                    }
                    else {
                        display_name = user.username;       
                    }
                    if (this.knowsPlayer(player.id)) {
                        td_inner.append($('<div class="text-overlay" style="top:2em">').html(Game.original_data.player_extra[player.id]['role']['name']))
                    }
                    if (!player.is_current) display_name = '<strike>' + display_name + '</strike>'
                    td.append($('<div class="text-overlay">').html(display_name))
                }
                //If the player is you
                if (this.me().x == row && this.me().y == col)
                {
                    td.addClass('you')
                    assign_player_avatar(td_inner, Game.me())
                    
                    if (Game.data.turns_allowed <= 0)
                    {
                        td.append($('<div class="text-overlay text-overlay-central">').html("Waiting..."))
                        td.addClass('frozen')
                    }
                    
                }
                else if (player)
                {
                    assign_player_avatar(td_inner, player)
                    //td_inner.append($('<img class="tile" src="' + this.media_url + 'img/char2.png">'))   
                }

            }

            $.fixedToolbars.show()
        }
    },
    
    helpMenu: function(target, previous)
    {
        $('#help #' + target).show();
        $('#help #' + previous).hide();
    },
    
    //Show one alert under board
    showAlert: function(al)
    {
        try {        
            var mark_alert_viewed = $('<a href="#" style="line-height: 1.0em;" data-role="button" data-theme="b" onclick="Game.viewedAlert(' + al.id + ');">').html("OK")
            Game.text_el.html('<div class="alert"><p>' + al.text + '</p><div style="height: 1.0em"><a href="#" style="line-height: 1em;" data-role="button" data-theme="b" onclick="Game.viewedAlert(' + al.id + ');">OK</a></div><br style="clear:both" /></div>')
            $('#board_text a').button({inline: true})
        }
        catch(e){}
    },
    
    showAlerts: function(data)
    {
        $('#page_alerts').remove()
        $.mobile.changePage('/seeker/game/' + Game.id + '/alerts/', "none", false, true)
    },
    
    viewedAlert: function(alert_id, callback)
    {
        if (typeof callback != "function") callback = function() {}
        $.post('/seeker/game/' + Game.id + '/alert/viewed/', {id: alert_id}, callback, 'json')
        Game.text_el.html("");
    },
    
    investigate: function()
    {
        Game.el.addClass('guessing-player')
        Game.state = "investigating"
        Game.text_el.html("Select a player to investigate...")
    },
    
    cluesForPlayer: function()
    {
        Game.el.addClass('guessing-player')
        Game.state = "clues_for_player"
        Game.text_el.html("Select a player to review clues about them...")
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
            Game.el.addClass('guessing-player');
            Game.text_el.html("Select a player to guess their role and cubicle...");
        }
        else
        {
            Game.text_el.html("You must be in your cubicle to guess.");
        }
    },
    
    showRoleGuesser: function()
    {
        $('#page_guesser').remove()
        $.mobile.changePage({url: '/seeker/game/' + Game.id + '/guesser/', type: 'post', data: {player: Game.guess.player}})
        Game.el.removeClass('guessing-player')
    },
    
    showClues: function()
    {
        $.post('/seeker/game/' + this.id + '/clues/', {},
            function(data) {
                showView(data, {left_button: "< Game"})
                $('#clues').show();
                $('#homeButton').hide();
            })
    },
    
    submitGuess: function()
    {     
        $.post('/seeker/game/' + Game.id + '/guess/', Game.guess,
            function(data) {
                Game.clearState()
                Game.el.removeClass('guessing-cubicle')
                if (data.correct)
                {
                    Game.text_el.html("Correct!")
                }
                else
                {
                    Game.text_el.html("Wrong.  (Hint: you're one fact closer now)")
                }
            }, 'json')
    },
    
    showBoard: function()
    {
        $('#homeButton').show()
        $('#clues').hide()
        $('#guesser').hide()
    },
    
    //is player in their cubicle?
    inCubible: function()
    {
        if (this.myCubicle().x == this.me().x && this.myCubicle().y == this.me().y)
        {
            return true
        }
        return false
    },
    
    me: function(include_orginal_data)
    {
        if (typeof include_orginal_data == "undefined") include_orginal_data = false
        var _me = Game.data.me;
        if (include_orginal_data) $.extend(_me, _me, Game.original_data.player_extra[Game.data.me.id])
        return _me;
    },
    
    myCubicle: function()
    {
        return Game.data.my_cubicle;
    },
    
    knowsPlayer: function(player_id)
    {
        for (var i in this.data.correct_guesses)
        {
            var guess =  this.data.correct_guesses[i]
            if (guess.other_player == player_id) return true
        }
        return false;
    },
    
    getById: function(type, id)
    {
        for (var i in this.data[type])
        {
            var obj = this.data[type][i]
            if (obj.id == id) return obj
        }
        return null
    },
    
    playerAt: function(x, y)
    {
        for (var id in this.data.players)
        {
            var player = this.data.players[id]
            if (player.x == x && player.y == y) return player;
        }
        
        return null;
    },
    
    cubicleAt: function(x, y)
    {
        for (var id in this.original_data.player_cells)
        {
            var cell = this.original_data.player_cells[id]
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
    },
    
    //Removes variables related to bring in the process of guessing, investigating, and displaying state
    clearState: function()
    {
        Game.state = null;
        Game.el.removeClass('guessing-cubicle')
        Game.el.removeClass('guessing-player')
    }
}

GameCell = {
  
    cellClick: function(evt)
    {
        if (!Game.player_active) {
            return false;
        }
        
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
                //LB - were allowing investigation of inactive players atm
                if (player.is_current || true) {
                    Game.clearState()
                    Game.reload({'investigate': target.attr('player')})   
                }
            }
            else if (target.hasClass('occupied'))
            {
                var player = Game.getById('players', parseInt(target.attr('player')))
                Game.text_el.html("You must be adjacent to a player to investigate them.")
                Game.clearState()
            }
            return false;
        }
        else if (Game.state == "clues_for_player")
        {
            if (target.hasClass('occupied')) {
                var player_id = target.attr('player');
                //Forces reload of aJAX content
                $('#clues_for_player').remove()
                $.mobile.changePage('/seeker/game/' + Game.id + '/player/?player=' + player_id)
                Game.clearState()
            }
 
            return false;
        }
        
        if (target.hasClass('can-move'))
        {
            Game.data.me.x = parseInt(target.attr('x'))
            Game.data.me.y = parseInt(target.attr('y'))
            Game.redraw()
            Game.reload({'move': target.attr('x') + ',' + target.attr('y')})
        }
        else {
            Game.text_el.html("You may only move to adjacent squares.")
        }
        
        return false;
        
    }
}

function assign_player_avatar(element, player) {
    //element.append($('<img class="tile" src="' + Game.media_url + 'img/char1.png">'))
    //alert(player.user.username)
    element.append($('<img class="char tile" src="' + player.image + '" />'));
}

function show_alert(text) {
    text = text.replace(/ /g, "_");
    $("body").append("<a id='open_dialog' style='display: none' data-rel='dialog' href='/seeker/game/show_notification/"+text+"'>open</a>");
    $("#open_dialog").click();
}

submitGuess = function()
{
    var user = $('#player')[0].value
    var role = $('#role')[0].value
    Game.submitGuess(user, role)
    Game.clearState()
}