
Game = {
    last_update: null,
    update_interval: 3000, //ms between updates
    busy_interval: 300,
    updateing: false,
    paused: false,
    
    init: function(id, el, media_url)
    {
        this.id = id;
        this.el = el;
        this.updating = true;
        this.media_url = media_url;
        Game.interval_id = setInterval(Game.busyLoop, Game.busy_interval)
    },
    
    //LB - The game needs to be smart about refreshing itself
    busyLoop: function()
    {
        if (!Game.last_update)
        {
            Game.last_update = new Date()
            Game.reload()
        }

        if (new Date().valueOf() > (Game.update_interval + Game.last_update.valueOf()) && !Game.updating)
        {
            Game.reload()
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
        console.log("Updating ")
        if (params) console.log(params)
        Game.updating = true
        
        if (!params) params = {}
        $.post('/seeker/game/' + Game.id + '/', params,
            function(data, status, req) {
                Game._game = data
                Game.updating = false
                Game.last_update = new Date()
                
                if (!Game._game.is_current)
                {
                    alert("The game is over!")
                    document.location.href = '/lobby/home/';
                }
                if (Game._game.new_clue)
                {
                    alert(Game._game.new_clue.str)
                }
                
                Game.redraw();             
            }, 'json');  
    },
    
    redraw: function()
    {
        this.rows = []
        this.el.html("");
        this.el.css('height', $(window).height()*0.75)
        this.el.css('width', this.el.height())
        
        for (row=0; row<this._game.board_size; row++)
        {
            var column = []
            var tr = $('<div class="row">')
            
            for (col=0; col<this._game.board_size; col++)
            {
                var td = $('<div class="cell">').attr('x', row).attr('y', col)
                td.append($('<div class="inner">'))
                var td_inner = $(td.children()[0])
                var player = this.playerAt(row, col)
                
                //If there is a player here
                if (player)
                {
                    td.addClass('occupied').attr('player', player.id)
                    td_inner.append($('<div class="text-overlay">').html(player.user.username))
                }
                //If the player is you
                if (this._game.player.x == row && this._game.player.y == col)
                {
                    td.addClass('you')
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/char1.png">'))
                }
                else if (player)
                {
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/char2.png">'))   
                }
                //If square is in moveable range
                if (Math.abs(this._game.player.x - row) <= 1 && Math.abs(this._game.player.y - col) <= 1)
                {
                    td.addClass('can-move selectable')
                    
                }
                //If there is a cubicle here
                var cubicle = this.cubicleAt(row, col)
                if (cubicle)
                {
                    td.addClass('a-cubicle')
                }
                //If the cubicle is yours
                if (this._game.player.cell.x == row && this._game.player.cell.y == col)
                {
                    td.addClass('your-cubicle')
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/cubicle2.png">'))
                }
                else if (cubicle)
                {
                    td_inner.append($('<img class="tile" src="' + this.media_url + 'img/cubicle1.png">'))
                }

                td.css('width', Math.floor(this.el.width()/this._game.board_size))
                td.css('height', Math.floor(this.el.height()/this._game.board_size))
                td.click(GameCell.cellClick)
                column.push(td)
                tr.append(td)
            }
            
            this.el.append(tr)
            this.rows.push(column)
        }
    },
    
    showGuesser: function()
    {
        $.post('/seeker/game/' + this.id + '/guesser/', {},
            function(data) {
                showView(data)
                $('#guesser').show()
            })
    },
    
    showClues: function()
    {
        $.post('/seeker/game/' + this.id + '/clues/', {},
            function(data) {
                showView(data, {left_button: "< Game"})
                $('#clues').show()
            })
    },
    
    submitGuess: function(user, role)
    {     
        this.reload({'guess': user + '=' + role})
    },
    
    showBoard: function()
    {
        $('#clues').hide()
        $('#guesser').hide()
    },
    
    playerAt: function(x, y)
    {
        for (var id in this._game.players)
        {
            var player = this._game.players[id]
            if (player.x == x && player.y == y) return player;
        }
        
        return null;
    },
    
    cubicleAt: function(x, y)
    {
        for (var id in this._game.players)
        {
            var cell = this._game.players[id].cell
            if (cell.x == x && cell.y == y) return cell;
        }
        
        return null;
    },
    
    pause: function()
    {
        if (!Game.paused)
        {
            if ($('#pause')) $('#pause').text('Go')
            this.paused = true
            clearInterval(Game.interval_id)
        }
        else
        {
            if ($('#pause')) $('#pause').text('Pause')
            this.paused = false
            this.interval_id = setInterval(Game.interval_id, Game.update_interval)
        }
    }
}

GameCell = {
  
    cellClick: function(evt)
    {
        var target = $(this)
        
        if (target.hasClass('occupied') && target.hasClass('can-move'))
        {
            Game.reload({'investigate': target.attr('player')})
        }
        
        else if (target.hasClass('can-move'))
        {
            Game.reload({'move': target.attr('x') + ',' + target.attr('y')})
        }
        
        else if (target.hasClass('occupied'))
        {
            alert("You must be adjacent to a player to investigate.")
        }
    },
}

submitGuess = function()
{
    var user = $('#player')[0].value
    var role = $('#role')[0].value
    Game.submitGuess(user, role)
}