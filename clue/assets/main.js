User = {}

submitForm = function(_form)
{
    var form = $(_form);
    new Ajax.Request(form.action, {
        parameters: form.serialize(true),
        onSuccess: function(resp) {
            
        }
    })
}

UPDATE_INTERVAL = 5000;

Game = {
    
    init: function(id, el)
    {
        this.id = id;
        this.el = el;
        this.updating = true;
        this.update_interval = UPDATE_INTERVAL;
        this.reload();
    },
    
    reload: function(params)
    {
        if (!params) params = {}
        $.post('/seeker/game/' + Game.id + '/', params,
            function(data) {
                Game._game = eval(data)
                
                if (!Game._game.is_current)
                {
                    alert("The game is over!")
                    document.location.href = '/lobby/home/';
                }
                if (Game._game.new_co)
                {
                    alert(Game._game.new_co.clue.str)
                }
                
                Game.redraw();             
                setTimeout(Game.reload, Game.update_interval)
            });  
    },
    
    redraw: function()
    {
        this.rows = []
        this.el.html("");
        //this.el.css('width', this._game.board_size*68)
        
        for (row=0; row<this._game.board_size; row++)
        {
            var column = []
            var tr = $('<div class="row">')
            
            for (col=0; col<this._game.board_size; col++)
            {
                var td = $('<div class="cell">').attr('x', row).attr('y', col)
                var player = this.playerAt(row, col)
                
                if (player)
                {
                    td.addClass('occupied').attr('player', player.id)
                    td.html(player.user.username)
                }
                
                if (this._game.player.x == row && this._game.player.y == col)
                {
                    td.addClass('you')
                }
                
                if (Math.abs(this._game.player.x - row) <= 1 && Math.abs(this._game.player.y - col) <= 1)
                {
                    td.addClass('can-move')  
                }

                td.css('width', 300.0/this._game.board_size-5)
                td.css('height', 300.0/this._game.board_size-5)
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
                $('#guesser').html(data)
                $('#guesser').show()
            })
    },
    
    showClues: function()
    {
        $.post('/seeker/game/' + this.id + '/clues/', {},
            function(data) {
                $('#clues').html(data)
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
            player = this._game.players[id]
            if (player.x == x && player.y == y) return player;
        }
        
        return null;
    },
    
    pause: function()
    {
        if (this.updating)
        {
            this.update_interval = 1000000
            this.updating = false
            if ($('#pause')) $('#pause').html('Go')
        }
        else
        {
            this.update_interval = UPDATE_INTERVAL
            if ($('#pause')) $('#pause').html('Pause')
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