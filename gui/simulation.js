var cm = {};

cm.grids = [];

cm.log = console.log ? console.log : function(){};

cm.draw = function(){
	var grids = this.grids;
	for(var g=0,gn=grids.length;g<gn;g++)
		grids[g]._draw();
};

cm.GridCell = function(args){
	$.extend(this,args);
	this._rectangle = {};
};

cm.GridCell.prototype = {
	x: -1,
	y: -1,
	sensor: false,
	burning: false,
	burningTime: -1,
	sensorTime: 0,
	_rectangle: null,
	draw:function(g,selected){
		var r = this._rectangle;
		// TODO: Unless the state has changed,
		// the colors can be stored and reused,
		// i.e. not calculated for each draw
		if (selected)
		{
			if (this.sensorTime && this.burningTime >= 0)
				r.fillStyle = '#fc9';
			else if (this.sensorTime)
				r.fillStyle = '#dd9';
			else if (this.burningTime >= 0)
				r.fillStyle='#f99';
			else
				r.fillStyle='#ccc';
		}
		else
		{
			if (this.sensorTime && this.burningTime >= 0)
				r.fillStyle = '#e60';
			else if (this.sensorTime)
				r.fillStyle = '#dd0';
			else if (this.burningTime >= 0)
				r.fillStyle='#e00';
			else
				r.fillStyle='#222';
		}
		var z = g.zoom;
		r.x = this.x*z + 0.5;
		r.y = this.y*z + 0.5;
		r.width = z;
		r.height = z;
		r.strokeWidth = 1;
		r.strokeStyle = g.borderColor;
		g.self.drawRect(r);
	},
};

cm.Grid = function(args){
	$.extend(this,args);
	this.parent = $(this.parent);
	this.self = $(this.self);
	var cells = this._cells = [];
	var that = this;

	for(var x=0,xn=this.sizeX;x<xn;x++)
	{
		cells[x] = [];
		for(var y=0,yn=this.sizeY;y<yn;y++)
		{
			cells[x][y] = new cm.GridCell({
				x:x,
				y:y
			});
		}
	}
	
	this._draw = function(){
		// Ensure that draw is not called too often
		clearTimeout(that._drawTimeout);
		that._drawTimeout = setTimeout(function(){that.onDraw()},200);
	};
	
	this.self.mousemove(function(ev){
		// Ensure that mouseover is not called too often
		clearTimeout(that._mouseTimeout);
		that._mouseTimeout = setTimeout(function(){
			var o = that.self.offset();
			var x = Math.floor((ev.clientX+$(window).scrollLeft()-o.left) / that.zoom);
			var y = Math.floor((ev.clientY+$(window).scrollTop()-o.top) / that.zoom);
			
			if (x==null || y==null || x < 0 || x >= that.sizeX || y < 0 || y >= that.sizeY )
			{
				that.onMouseOut(ev,that._cells[that._mouseX][that._mouseY]);
				$('#tooltip').hide();
				return;
			}
			
			if (x != that._mouseX || y != that._mouseY)
			{
				var c = that._cells;
				that.onMouseOut(ev,that._cells[that._mouseX][that._mouseY])
				that.onMouseOver(ev,that._cells[x][y]);
			}
			
			that._mouseX = x;
			that._mouseY = y;
		},10);
	});
	
	this.self.mouseout(function(ev){
		that.onMouseOut(ev,that._cells[that._mouseX][that._mouseY]);
		$('#tooltip').hide();
	});
	
	this.self.click(function(ev){
		var o = that.self.offset();
		var x = Math.floor((ev.clientX+$(window).scrollLeft()-o.left) / that.zoom);
		var y = Math.floor((ev.clientY+$(window).scrollTop()-o.top) / that.zoom);
		
		if (x==null || y==null || x < 0 || x >= that.sizeX || y < 0 || y >= that.sizeY )
			return;
		
		that.onMouseClick(ev,that._cells[x][y]);
	});
	
	cm.grids.push(this);
	
	$(document).ready(function(){
		that.self.appendTo(that.parent);
		that._draw();
	});
};

cm.Grid.prototype = {
	parent:'body',
	self:'<canvas/>',
	sizeX: 71,
	sizeY: 71,
	zoom: 10,
	backgroundColor: '#222',
	foregroundColor: '#ccc',
	borderColor: '#111',
	windMagnitude: 1,
	humidity: 50,
	chanceOfBurning: 58,
	windDirection: 0, // radians
	_cells: null,
	_time: 0,
	_mouseTimeout: null,
	_mouseX: 0,
	_mouseY: 0,
	_draw: null,
	_drawTimeout: null,
	_next: function(){
		cm.log('next!');
		var mr = Math.random;
		var mf = Math.floor;
		
		//   For each cell, 9 cells are stored in variables
		//   where C5 is the current cell, and the others
		//   are the neighboors.
		//
		//    C1    C2    C3
		//    C4    C5    C6   -----> x
		//    C7    C8    C9
		//
		//           |
		//           |
		//           V
		//           y
		
		var c = this._cells;
		var c1,c2,c3,c4,c5,c6,c7,c8,c9; // neighbooring cells
		var x0,x1,x2,xn; // cell x indicies 
		var y0,y1,y2,yn; // cell y indicies
		
		var burning = 0; // number of burning neighboor cells
		var sensor = 0; // number of sensed neighboor cells
		
		this.windMagnitude = parseInt($('#windMag').val());
		var wd = parseInt($('#windDir').val());
		this.humidity = parseInt($('#himidity').val())
		var wdr = wd*Math.PI/180;
		var wx = this.windMagnitude * Math.cos(wdr);
		var wy = this.windMagnitude * Math.sin(wdr);
		wx = Math.abs(wx) > 0 && Math.abs(wx) <= 0.00009 ? 0 : wx;
		wy = Math.abs(wy) > 0 && Math.abs(wy) <= 0.00009 ? 0 : wy;
		var burn = this.chanceOfBurning*this.windMagnitude;
		if(burn == 0)
			{
			burn = this.chanceOfBurning;
			}
		var hum  = 5-Math.round(this.humidity/10)
		var combust;
		
		var time = ++this._time; // time now

		for(x0=-1,x1=0,x2=1,xn=this.sizeX;x1<xn;x0++,x1++,x2++)
		{
			x0v = x1 > 0;
			x2v = x2 < xn;
			
			for(y0=-1,y1=0,y2=1,yn=this.sizeY;y1<yn;y0++,y1++,y2++)
			{
				sensor = 0;
				burning = 0;
				combust = 0;
				c5 = c[x1][y1];
				
				if (c5.sensorTime!=time)
					c5.sensorTime = 0;
				
				if (y0 >= 0)
				{
					c1 = x0v ? c[x0][y0] : null;
					c2 =       c[x1][y0] ;
					c3 = x2v ? c[x2][y0] : null;
					
					if (c1) 
					{
						if (c1.burningTime >=0 && c1.burningTime != time)
						{
							burning+=(4+(wx!=0?Math.round(wx*3):-1)+(wy!=0?Math.round(wy*-3):-1));
							combust++;
						}
						if (c1.sensorTime)
							sensor++;
					}
					if (c2)
					{
						if (c2.burningTime >=0 && c2.burningTime != time)
							{
							burning+=(8+(wy!=0?Math.round(wy*-7):-4));
							combust++;
							}
						if (c2.sensorTime)
							sensor++;
					}
					if (c3)
					{
						if (c3.burningTime >=0 && c3.burningTime != time)
						{
							burning+=(4+(wx!=0?Math.round(wx*-3):-1)+(wy!=0?Math.round(wy*-3):-1));
							combust++;
						}
						if (c3.sensorTime)
							sensor++;
					}
				}
				if (x0v)
				{
					c4 = c[x0][y1];
					
					if (c4.burningTime >=0 && c4.burningTime != time)
					{	
						burning+=(8+(wx!=0?Math.round(wx*7):-4));
						combust++;
					}
					if (c4.sensorTime)
						sensor++;
				}
				//----------------- c5 is self ---------------------//
				if (x2v)
				{
					c6 = c[x2][y1];
					
					if (c6.burningTime >=0 && c6.burningTime != time)
					{	
						burning+=(8+(wx!=0?Math.round(wx*-7):-4));
						combust++;
					}
					if (c6.sensorTime)
						sensor++;
				}
				if (y2 < yn) 
				{
					c7 = x0v ? c[x0][y2] : null;
					c8 =       c[x1][y2] ;
					c9 = x2v ? c[x2][y2] : null;
					
					if (c7)
					{
						if (c7.burningTime >=0 && c7.burningTime != time)
						{	
							burning+=(4+(wx!=0?Math.round(wx*3):-1)+(wy!=0?Math.round(wy*3):-1));
							combust++;
						}
						if (c7.sensorTime)
							sensor++;
					}
					if (c8)
					{
						if (c8.burningTime >=0 && c8.burningTime != time)
						{	
							burning+=(8+(wy!=0?Math.round(wy*7):-4));
							combust++;
						}
						if (c8.sensorTime)
							sensor++;
					}
					if (c9)
					{
						if (c9.burningTime >=0 && c9.burningTime != time)
						{	
							burning+=(4+(wx!=0?Math.round(wx*-3):-1)+(wy!=0?Math.round(wy*3):-1));
							combust++;
						}
						if (c9.sensorTime)
							sensor++;
					}
				}
				if (burning > 0)
				{
					burning += hum;
				}
				if (!(c5.burningTime>=0) && burning && combust == 8)
					{
						c5.burningTime = time;
					}
				else if ( !(c5.burningTime>=0) && burning && burning > mf(mr()*burn) )
					c5.burningTime = time;
					
				if ( !(c5.burningTime>=0) && !sensor && !c5.sensorTime && mr() <= 0.2)
					c5.sensorTime = time;
				
				c5.burningCount = combust;
			}
		}
		
		this.evaluate(null);
	},
	onMouseClick:function(ev,cell){
		cell.burningTime = this._time;
		cell.draw(this,false);		
	},
	onMouseOver:function(ev,cell){
		cell.draw(this,true);
		var o = this.self.offset();
		var z = this.zoom;
		$('#tooltip').text('['+cell.x+','+cell.y+']')
		.css('left',cell.x*z+o.left+(z<<1))
		.css('top',cell.y*z+o.top+(z<<1)).show();
	},
	onMouseOut:function(ev,cell){
		cell.draw(this,false);
	},
	onDraw:function(){		
		var p = this.parent;
		var s = this.self;
		s.attr('width',(this.sizeX*this.zoom+1)+"px");
		s.attr('height',(this.sizeY*this.zoom+1)+"px");
		s.loadCanvas();
		
		var c = this._cells;
		
		for(var x=0,nx=this.sizeX;x<nx;x++)
			for(var y=0,ny=this.sizeY;y<ny;y++)
				c[x][y].draw(this,false);
	},
	evaluate:function(target){
		var from = this._cells;
		var to = [];

		var ch = String.fromCharCode;
		
		for(var x=0,nx=this.sizeX;x<nx;x++)
		{			
			for(var y=0,ny=this.sizeY;y<ny;y++)
			{
				to.push(ch(from[x][y].burningCount));
			}
		}
		
		var that = this;
		
		$.ajax({
			url:'http://localhost:8000/simulate/fire',
			type: 'post',
			dataType: 'text',
			mimeType: 'application/json',
			data: {
				time: that._time,
				sizeX: that.sizeX,
				sizeY: that.sizeY,
				windDirection: that.windDirection,
				cells: Base64.encode(to.join(''))
			}
		});
	}
};

$.jCanvas({
	fromCenter: false,
	strokeWidth: 0,
	strokeStyle: "#111",
	strokeJoin: "miter",
	strokeCap: "square"
});

$(window).resize(function(){
	cm.draw();
});

$(document).ready(function(){
	
});

